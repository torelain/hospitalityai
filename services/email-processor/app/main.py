import os

from fastapi import FastAPI, HTTPException, Request

from ..adapters.claude.classifier import ClaudeIntentClassifier
from ..adapters.claude.extractor import ClaudeBookingExtractor
from ..adapters.mews.adapter import MewsAdapter
from ..adapters.mews.client import MewsClient
from ..adapters.postmark.inbound import parse_postmark_payload
from ..adapters.postmark.outbound import PostmarkEmailSender
from ..domain.models import Intent
from ..domain.use_cases.process_email import ProcessEmail

app = FastAPI(title="Hospitality AI — Email Processor")


def _claude_classifier() -> ClaudeIntentClassifier:
    return ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"])


def _claude_extractor() -> ClaudeBookingExtractor:
    return ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"])


def _build_use_case() -> ProcessEmail:
    mews_client = MewsClient(
        client_token=os.environ["MEWS_CLIENT_TOKEN"],
        access_token=os.environ["MEWS_ACCESS_TOKEN"],
        demo=os.environ.get("MEWS_DEMO", "true").lower() == "true",
    )
    return ProcessEmail(
        classifier=_claude_classifier(),
        extractor=_claude_extractor(),
        pms=MewsAdapter(
            client=mews_client,
            service_id=os.environ["MEWS_SERVICE_ID"],
        ),
        email_sender=PostmarkEmailSender(
            api_token=os.environ["POSTMARK_API_TOKEN"],
            front_desk_email=os.environ["FRONT_DESK_EMAIL"],
            from_email=os.environ["FROM_EMAIL"],
        ),
    )


@app.post("/extract")
async def extract(request: Request):
    """Classify and extract booking data. Requires only ANTHROPIC_API_KEY."""
    payload = await request.json()
    try:
        email = parse_postmark_payload(payload)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    intent = _claude_classifier().classify(email)
    if intent != Intent.BOOKING_CONFIRMATION:
        return {"intent": intent.value, "booking": None}

    booking = _claude_extractor().extract(email)
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


@app.post("/webhook/inbound-email")
async def inbound_email(request: Request):
    payload = await request.json()
    try:
        email = parse_postmark_payload(payload)
    except (KeyError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    use_case = _build_use_case()
    result = use_case.execute(email)
    return {"path": result.path.value, "reservation_id": result.mews_reservation_id}


@app.get("/health")
def health():
    return {"status": "ok"}
