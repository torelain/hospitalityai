import httpx

from ...domain.models import ProcessingResult
from ...domain.ports import EmailSenderPort


class PostmarkEmailSender(EmailSenderPort):
    def __init__(self, api_token: str, front_desk_email: str, from_email: str):
        self._api_token = api_token
        self._front_desk_email = front_desk_email
        self._from_email = from_email

    def send_auto_booking_notification(self, result: ProcessingResult) -> None:
        booking = result.booking_data
        self._send(
            subject=f"Booking created — {booking.guest_name} ({booking.arrival_date} – {booking.departure_date})",
            body=(
                f"A booking was automatically created in Mews.\n\n"
                f"Reservation ID: {result.mews_reservation_id}\n"
                f"Guest: {booking.guest_name}\n"
                f"Arrival: {booking.arrival_date}\n"
                f"Departure: {booking.departure_date}\n"
                f"Room: {booking.room_category}\n"
                f"Guests: {booking.num_guests}\n"
                f"Agency: {booking.agency_name or '—'}\n"
                f"Special wishes: {booking.special_wishes or '—'}\n\n"
                f"--- Original email ---\n{result.email.text_body}"
            ),
        )

    def send_assisted_handoff(self, result: ProcessingResult) -> None:
        booking = result.booking_data
        self._send(
            subject=f"Action required — booking confirmation from {result.email.from_name}",
            body=(
                f"Hospitality AI could not process this booking automatically. Please review.\n\n"
                f"Extracted data:\n"
                f"  Guest: {booking.guest_name if booking else '—'}\n"
                f"  Arrival: {booking.arrival_date if booking else '—'}\n"
                f"  Departure: {booking.departure_date if booking else '—'}\n"
                f"  Room: {booking.room_category if booking else '—'}\n"
                f"  Guests: {booking.num_guests if booking else '—'}\n"
                f"  Agency: {booking.agency_name if booking else '—'}\n\n"
                f"--- Original email ---\n{result.email.text_body}"
            ),
        )

    def send_pass_through(self, result: ProcessingResult) -> None:
        failure_note = (
            f"Note: Hospitality AI is currently unavailable ({result.failure_reason}).\n\n"
            if result.failure_reason
            else ""
        )
        self._send(
            subject=f"FWD: {result.email.subject}",
            body=f"{failure_note}--- Original email ---\n{result.email.text_body}",
        )

    def _send(self, subject: str, body: str) -> None:
        httpx.post(
            "https://api.postmarkapp.com/email",
            headers={"X-Postmark-Server-Token": self._api_token},
            json={
                "From": self._from_email,
                "To": self._front_desk_email,
                "Subject": subject,
                "TextBody": body,
            },
            timeout=10.0,
        ).raise_for_status()
