import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response

from ..adapters.claude.classifier import ClaudeIntentClassifier
from ..adapters.claude.extractor import ClaudeBookingExtractor
from ..adapters.db.connection import make_pool
from ..adapters.db.ledger import DBBookingLedger
from ..adapters.db.migrations import run as run_migrations
from ..adapters.db.pms import FakePMS
from ..adapters.graph.auth import GraphTokenCache
from ..adapters.graph.inbound import GraphInboundClient, parse_notification
from ..domain.models import Intent
from ..domain.use_cases.process_email import ProcessEmail
from .config import load as load_config

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

    try:
        yield
    finally:
        pool.close()


app = FastAPI(title="Hospitality AI — Email Processor", lifespan=lifespan)


def _build_use_case(request: Request) -> ProcessEmail:
    return ProcessEmail(
        classifier=ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"]),
        extractor=ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"]),
        pms=FakePMS(),
        ledger=DBBookingLedger(pool=request.app.state.pool, hotel_mailbox=request.app.state.hotel_mailbox),
    )


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
    from datetime import datetime as _dt

    from ..domain.models import InboundEmail

    email = InboundEmail(
        message_id=payload.get("message_id", "test"),
        from_email=payload.get("from_email", "test@example.com"),
        from_name=payload.get("from_name", ""),
        to_email=payload.get("to_email", ""),
        subject=payload.get("subject", ""),
        text_body=payload.get("text_body", ""),
        received_at=_dt.now(timezone.utc),
    )

    classifier = ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"])
    intent = classifier.classify(email)
    if intent != Intent.BOOKING_CONFIRMATION:
        return {"intent": intent.value, "booking": None}

    booking = ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"]).extract(email)
    return {
        "intent": intent.value,
        "booking": {
            "guest_name": booking.guest_name,
            "arrival_date": booking.arrival_date.isoformat(),
            "departure_date": booking.departure_date.isoformat(),
            "room_category": booking.room_category,
            "num_guests": booking.num_guests,
            "agency_name": booking.agency_name,
            "guest_email": booking.guest_email,
            "special_wishes": booking.special_wishes,
            "voucher_code": booking.voucher_code,
            "confidence": booking.confidence.value,
        },
    }


@app.post("/cron/renew-subscriptions")
def renew_subscriptions(request: Request):
    """Daily-cron target. Renews any subscription expiring within 36 hours.
    On 404 (Graph forgot it) — recreate from scratch."""
    pool = request.app.state.pool
    graph: GraphInboundClient = request.app.state.graph
    cutoff = datetime.now(timezone.utc) + timedelta(hours=36)

    renewed: list[str] = []
    recreated: list[str] = []

    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT subscription_id, hotel_mailbox, client_state FROM graph_subscriptions WHERE expires_at < %s",
            (cutoff,),
        )
        rows = cur.fetchall()

    for sub_id, mailbox, client_state in rows:
        try:
            response = graph.renew_subscription(sub_id)
            new_expires = _parse_iso(response["expirationDateTime"])
            with pool.connection() as conn, conn.cursor() as cur:
                cur.execute(
                    "UPDATE graph_subscriptions SET expires_at = %s WHERE subscription_id = %s",
                    (new_expires, sub_id),
                )
            renewed.append(sub_id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
            webhook_url = os.environ["GRAPH_WEBHOOK_URL"]
            new_sub = graph.create_subscription(mailbox, webhook_url, client_state)
            new_expires = _parse_iso(new_sub["expirationDateTime"])
            with pool.connection() as conn, conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM graph_subscriptions WHERE subscription_id = %s",
                    (sub_id,),
                )
                cur.execute(
                    "INSERT INTO graph_subscriptions (subscription_id, hotel_mailbox, client_state, expires_at) "
                    "VALUES (%s, %s, %s, %s)",
                    (new_sub["id"], mailbox, client_state, new_expires),
                )
            recreated.append(new_sub["id"])

    return {"renewed": renewed, "recreated": recreated}


@app.get("/health")
def health():
    return {"status": "ok"}


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
