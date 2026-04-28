import logging
import os
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, Request, Response

from adapters.claude.classifier import ClaudeIntentClassifier
from adapters.claude.extractor import ClaudeBookingExtractor
from adapters.db.bookings_export import BookingExportRepo
from adapters.db.connection import make_pool
from adapters.db.ledger import DBBookingLedger
from adapters.db.migrations import run as run_migrations
from adapters.db.pms import FakePMS
from adapters.db.subscriptions import GraphSubscriptionRepo
from adapters.graph.auth import GraphTokenCache
from adapters.graph.inbound import GraphInboundClient, parse_notification
from domain.models import InboundEmail, Intent
from domain.use_cases.process_email import ProcessEmail
from .config import load as load_config
from .security import require_cron_token

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    pool = make_pool(config.database_url)
    run_migrations(pool)

    token_cache = GraphTokenCache(
        tenant_id=config.hotel_tenant_id,
        client_id=config.azure_client_id,
        client_secret=config.azure_client_secret,
    )
    graph = GraphInboundClient(token_cache=token_cache)

    app.state.config = config
    app.state.pool = pool
    app.state.graph = graph
    app.state.hotel_mailbox = config.hotel_mailbox
    app.state.expected_client_state = config.graph_webhook_client_state
    app.state.cron_token = config.cron_token

    try:
        yield
    finally:
        pool.close()


app = FastAPI(title="Hospitality AI — Email Processor", lifespan=lifespan)


def _process_inbound(request_app, message_id: str) -> None:
    """Background task: fetches the full message from Graph and runs the use case.

    Uses request_app rather than request because the request lifecycle ends before this runs."""
    try:
        graph: GraphInboundClient = request_app.state.graph
        mailbox: str = request_app.state.hotel_mailbox
        email = graph.fetch_message(mailbox, message_id)

        use_case = ProcessEmail(
            classifier=ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"]),
            extractor=ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"]),
            pms=FakePMS(),
            ledger=DBBookingLedger(pool=request_app.state.pool, hotel_mailbox=mailbox),
        )
        use_case.execute(email)
    except Exception:
        logger.error("Background processing failed for message_id=%s", message_id, exc_info=True)


@app.post("/webhook/outlook-notification")
async def outlook_notification(request: Request, background_tasks: BackgroundTasks):
    # Subscription validation handshake — Graph sends ?validationToken=... on creation.
    # Must echo back as text/plain within 10 seconds.
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(content=validation_token, media_type="text/plain", status_code=200)

    payload = await request.json()
    expected_state = request.app.state.expected_client_state

    for notification in parse_notification(payload):
        if notification.get("clientState") != expected_state:
            logger.warning("Rejecting notification with unexpected clientState")
            continue
        message_id = notification.get("resourceData", {}).get("id")
        if not message_id:
            continue
        background_tasks.add_task(_process_inbound, request.app, message_id)

    return Response(status_code=202)


@app.post("/extract")
async def extract(request: Request):
    """Offline classify + extract for testing. Expects JSON {subject, text_body, from_email?, from_name?}."""
    payload = await request.json()

    email = InboundEmail(
        message_id=payload.get("message_id", "test"),
        from_email=payload.get("from_email", "test@example.com"),
        from_name=payload.get("from_name", ""),
        to_email=payload.get("to_email", ""),
        subject=payload.get("subject", ""),
        text_body=payload.get("text_body", ""),
        received_at=datetime.now(timezone.utc),
    )

    classifier = ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"])
    intent = classifier.classify(email)
    if intent != Intent.BOOKING_CONFIRMATION:
        return {"intent": intent.value, "booking": None}

    booking = ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"]).extract(email)
    return {"intent": intent.value, "booking": _booking_to_jsonable(booking)}


def _booking_to_jsonable(booking) -> dict:
    data = asdict(booking)
    for key, value in list(data.items()):
        if hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        elif hasattr(value, "value"):
            data[key] = value.value
    return data


@app.post("/cron/renew-subscriptions", dependencies=[Depends(require_cron_token)])
def renew_subscriptions(request: Request):
    """Daily-cron target. Renews any subscription expiring within 36 hours.
    On 404 (Graph forgot it) — recreate from scratch."""
    repo = GraphSubscriptionRepo(pool=request.app.state.pool)
    graph: GraphInboundClient = request.app.state.graph
    cutoff = datetime.now(timezone.utc) + timedelta(hours=36)

    renewed: list[str] = []
    recreated: list[str] = []

    for sub in repo.find_expiring_before(cutoff):
        try:
            response = graph.renew_subscription(sub.subscription_id)
            repo.update_expiry(sub.subscription_id, _parse_iso(response["expirationDateTime"]))
            renewed.append(sub.subscription_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
            webhook_url = os.environ["GRAPH_WEBHOOK_URL"]
            new_sub = graph.create_subscription(sub.hotel_mailbox, webhook_url, sub.client_state)
            repo.replace(
                old_id=sub.subscription_id,
                new_id=new_sub["id"],
                mailbox=sub.hotel_mailbox,
                client_state=sub.client_state,
                expires_at=_parse_iso(new_sub["expirationDateTime"]),
            )
            recreated.append(new_sub["id"])

    return {"renewed": renewed, "recreated": recreated}


@app.post("/cron/export-matchings", dependencies=[Depends(require_cron_token)])
def export_matchings(request: Request, days: int = 7):
    """Returns processed bookings from the last `days` days as JSON.
    Triggered weekly by GitHub Actions; downstream consumers commit the snapshot
    or pipe it to QA tooling."""
    repo = BookingExportRepo(pool=request.app.state.pool)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    bookings = repo.fetch_since(since)
    return {
        "since": since.isoformat(),
        "count": len(bookings),
        "bookings": bookings,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
