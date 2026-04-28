from datetime import date

import anthropic

from domain.models import BookingData, ExtractionConfidence, InboundEmail
from domain.use_cases.process_email import BookingExtractor
from adapters.mews.rate_plans import resolve_voucher_code

SYSTEM_PROMPT = """You are a booking data extractor for a German hotel.
Extract booking details from the email.

Date handling:
- German emails may express stay length as "X Tage" (days including both arrival and departure).
  Convert to nights: nights = Tage - 1. Example: "4 Tage" = 3 nights.
- When both "Tage" and "Nächte" appear, use Nächte as authoritative.
- Always return the actual arrival and departure calendar dates in YYYY-MM-DD format."""

EXTRACT_BOOKING_TOOL: anthropic.types.ToolParam = {
    "name": "extract_booking",
    "description": "Extract structured booking data from a hotel booking confirmation email.",
    "input_schema": {
        "type": "object",
        "properties": {
            "guest_name": {
                "type": "string",
                "description": "Full name of the guest",
            },
            "arrival_date": {
                "type": "string",
                "description": "Arrival date in YYYY-MM-DD format",
            },
            "departure_date": {
                "type": "string",
                "description": "Departure date in YYYY-MM-DD format",
            },
            "room_category": {
                "type": "string",
                "description": "Room or accommodation category name",
            },
            "num_guests": {
                "type": "integer",
                "description": "Number of guests",
            },
            "rate_plan_name": {
                "type": "string",
                "description": "Rate plan or package name as stated in the email (e.g. 'Kurzreisen', 'Kuren'). Omit if not identifiable.",
            },
            "agency_name": {
                "type": "string",
                "description": "Name of the booking agency or OTA",
            },
            "agency_reference": {
                "type": "string",
                "description": "Booking reference number assigned by the agency or OTA (e.g. DERTOUR booking number, booking.com reservation ID). Omit if not present.",
            },
            "guest_email": {
                "type": "string",
                "description": "Guest email address",
            },
            "special_wishes": {
                "type": "string",
                "description": "Special requests or notes from the guest",
            },
            "confidence": {
                "type": "string",
                "enum": ["high", "low"],
                "description": "'high' if all required fields are clearly present, 'low' otherwise",
            },
        },
        "required": [
            "guest_name",
            "arrival_date",
            "departure_date",
            "room_category",
            "num_guests",
            "confidence",
        ],
    },
}

class ClaudeBookingExtractor(BookingExtractor):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def extract(self, email: InboundEmail) -> BookingData:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            tools=[EXTRACT_BOOKING_TOOL],
            tool_choice={"type": "tool", "name": "extract_booking"},
            messages=[
                {
                    "role": "user",
                    "content": f"Subject: {email.subject}\n\n{email.text_body}",
                }
            ],
        )

        tool_use = next(b for b in message.content if b.type == "tool_use")
        data = tool_use.input

        arrival = date.fromisoformat(data["arrival_date"])
        departure = date.fromisoformat(data["departure_date"])
        nights = (departure - arrival).days

        rate_plan_name = data.get("rate_plan_name")
        voucher_code = resolve_voucher_code(rate_plan_name, nights) if rate_plan_name else None

        return BookingData(
            guest_name=data["guest_name"],
            arrival_date=arrival,
            departure_date=departure,
            room_category=data["room_category"],
            num_guests=data["num_guests"],
            agency_name=data.get("agency_name"),
            agency_reference=data.get("agency_reference"),
            guest_email=data.get("guest_email"),
            special_wishes=data.get("special_wishes"),
            voucher_code=voucher_code,
            confidence=ExtractionConfidence(data.get("confidence", "low")),
        )
