import json
from datetime import date

import anthropic

from ...domain.models import BookingData, ExtractionConfidence, InboundEmail
from ...domain.use_cases.process_email import BookingExtractor

SYSTEM_PROMPT = """You are a booking data extractor for a hotel.
Extract booking details from the email and return a JSON object with these fields:
- guest_name (string, required)
- arrival_date (string, YYYY-MM-DD, required)
- departure_date (string, YYYY-MM-DD, required)
- room_category (string, required)
- num_guests (integer, required)
- agency_name (string or null)
- guest_email (string or null)
- special_wishes (string or null)
- confidence (string: "high" if all required fields are clearly present, "low" otherwise)

Return only valid JSON, nothing else."""


class ClaudeBookingExtractor(BookingExtractor):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def extract(self, email: InboundEmail) -> BookingData:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Subject: {email.subject}\n\n{email.text_body}",
                }
            ],
        )
        data = json.loads(message.content[0].text.strip())
        return BookingData(
            guest_name=data["guest_name"],
            arrival_date=date.fromisoformat(data["arrival_date"]),
            departure_date=date.fromisoformat(data["departure_date"]),
            room_category=data["room_category"],
            num_guests=data["num_guests"],
            agency_name=data.get("agency_name"),
            guest_email=data.get("guest_email"),
            special_wishes=data.get("special_wishes"),
            confidence=ExtractionConfidence(data.get("confidence", "low")),
        )
