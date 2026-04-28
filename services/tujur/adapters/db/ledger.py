import json
from dataclasses import asdict

from psycopg.types.json import Jsonb
from psycopg_pool import ConnectionPool

from domain.models import ProcessingResult
from domain.ports import BookingLedgerPort


class DBBookingLedger(BookingLedgerPort):
    def __init__(self, pool: ConnectionPool, hotel_mailbox: str):
        self._pool = pool
        self._hotel_mailbox = hotel_mailbox

    def has_processed(self, message_id: str) -> bool:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM extracted_bookings WHERE message_id = %s AND hotel_mailbox = %s LIMIT 1",
                (message_id, self._hotel_mailbox),
            )
            return cur.fetchone() is not None

    def persist(self, result: ProcessingResult) -> None:
        booking = result.booking_data
        raw_email = {
            "from_email": result.email.from_email,
            "from_name": result.email.from_name,
            "to_email": result.email.to_email,
            "subject": result.email.subject,
            "text_body": result.email.text_body,
            "received_at": result.email.received_at.isoformat(),
        }
        raw_extraction = _booking_to_dict(booking) if booking else None

        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO extracted_bookings (
                    message_id, hotel_mailbox, intent, processing_path,
                    guest_name, arrival_date, departure_date, room_category, num_guests,
                    agency_name, guest_email, special_wishes, voucher_code, confidence,
                    raw_email, raw_extraction, fake_reservation_id, failure_reason
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (message_id, hotel_mailbox) DO NOTHING
                """,
                (
                    result.email.message_id,
                    self._hotel_mailbox,
                    "booking_confirmation" if booking else "unknown",
                    result.path.value,
                    booking.guest_name if booking else None,
                    booking.arrival_date if booking else None,
                    booking.departure_date if booking else None,
                    booking.room_category if booking else None,
                    booking.num_guests if booking else None,
                    booking.agency_name if booking else None,
                    booking.guest_email if booking else None,
                    booking.special_wishes if booking else None,
                    booking.voucher_code if booking else None,
                    booking.confidence.value if booking else None,
                    Jsonb(raw_email),
                    Jsonb(raw_extraction) if raw_extraction else None,
                    result.mews_reservation_id,
                    result.failure_reason,
                ),
            )


def _booking_to_dict(booking) -> dict:
    data = asdict(booking)
    for key, value in list(data.items()):
        if hasattr(value, "isoformat"):
            data[key] = value.isoformat()
        elif hasattr(value, "value"):
            data[key] = value.value
    return data
