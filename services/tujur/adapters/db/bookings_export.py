from datetime import date, datetime
from decimal import Decimal

from psycopg_pool import ConnectionPool


class BookingExportRepo:
    """Read-side repo for analytics/export use cases — separate from the write-side
    BookingLedgerPort to keep the domain port focused on persistence."""

    EXPORT_COLUMNS = (
        "id, message_id, hotel_mailbox, intent, processing_path, "
        "guest_name, arrival_date, departure_date, room_category, num_guests, "
        "agency_name, guest_email, special_wishes, voucher_code, confidence, "
        "fake_reservation_id, failure_reason, created_at"
    )

    def __init__(self, pool: ConnectionPool):
        self._pool = pool

    def fetch_since(self, since: datetime) -> list[dict]:
        with self._pool.connection() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT {self.EXPORT_COLUMNS} FROM extracted_bookings "
                "WHERE created_at >= %s ORDER BY created_at DESC",
                (since,),
            )
            cols = [d.name for d in cur.description]
            return [_row_to_jsonable(dict(zip(cols, row))) for row in cur.fetchall()]


def _row_to_jsonable(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if isinstance(v, (date, datetime)):
            out[k] = v.isoformat()
        elif isinstance(v, Decimal):
            out[k] = float(v)
        else:
            out[k] = v
    return out
