from psycopg_pool import ConnectionPool

SCHEMA = """
CREATE TABLE IF NOT EXISTS extracted_bookings (
    id                  BIGSERIAL PRIMARY KEY,
    message_id          TEXT NOT NULL,
    hotel_mailbox       TEXT NOT NULL,
    intent              TEXT NOT NULL,
    processing_path     TEXT NOT NULL,
    guest_name          TEXT,
    arrival_date        DATE,
    departure_date      DATE,
    room_category       TEXT,
    num_guests          INTEGER,
    agency_name         TEXT,
    guest_email         TEXT,
    special_wishes      TEXT,
    voucher_code        TEXT,
    confidence          TEXT,
    raw_email           JSONB NOT NULL,
    raw_extraction      JSONB,
    fake_reservation_id TEXT,
    failure_reason      TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (message_id, hotel_mailbox)
);

CREATE TABLE IF NOT EXISTS graph_subscriptions (
    subscription_id TEXT PRIMARY KEY,
    hotel_mailbox   TEXT NOT NULL UNIQUE,
    client_state    TEXT NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def run(pool: ConnectionPool) -> None:
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(SCHEMA)
