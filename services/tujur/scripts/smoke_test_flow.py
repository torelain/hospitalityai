"""End-to-end flow smoke test with a mocked Graph mail client.

Runs classify → extract → PMS → ledger persist against the real Postgres
container started via docker-compose. The Graph fetch is bypassed by
constructing an InboundEmail directly.

Usage (from services/tujur/):
    python -m scripts.smoke_test_flow
"""

import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv

from adapters.claude.classifier import ClaudeIntentClassifier
from adapters.claude.extractor import ClaudeBookingExtractor
from adapters.db.connection import make_pool
from adapters.db.ledger import DBBookingLedger
from adapters.db.migrations import run as run_migrations
from adapters.db.pms import FakePMS
from domain.models import InboundEmail
from domain.use_cases.process_email import ProcessEmail

load_dotenv()


SAMPLE_EMAIL = InboundEmail(
    message_id="<smoke-test-flow-001@example.com>",
    from_email="reservations@dertour.de",
    from_name="DERTOUR Reservations",
    to_email="info@tujur.de",
    subject="Buchungsbestätigung – Familie Müller, 15.06.2026",
    text_body=(
        "Sehr geehrte Damen und Herren,\n\n"
        "wir bestätigen folgende Buchung:\n\n"
        "Gast: Hans Müller\n"
        "Anreise: 15.06.2026\n"
        "Abreise: 19.06.2026 (4 Nächte)\n"
        "Zimmerkategorie: Doppelzimmer Komfort\n"
        "Anzahl Gäste: 2\n"
        "Ratenplan: Kurzreisen\n"
        "DERTOUR Buchungsnummer: DT-998877\n"
        "E-Mail Gast: hans.mueller@example.de\n"
        "Sonderwünsche: Bitte ein ruhiges Zimmer zum Innenhof.\n\n"
        "Mit freundlichen Grüßen\nDERTOUR\n"
    ),
    received_at=datetime.now(timezone.utc),
)


def main() -> int:
    required = ["ANTHROPIC_API_KEY", "DATABASE_URL", "HOTEL_MAILBOX"]
    missing = [v for v in required if not os.environ.get(v)]
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    mailbox = os.environ["HOTEL_MAILBOX"]
    print(f"Connecting to DB and running migrations…")
    pool = make_pool(os.environ["DATABASE_URL"])
    run_migrations(pool)
    print("  ✓ migrations applied")

    use_case = ProcessEmail(
        classifier=ClaudeIntentClassifier(api_key=os.environ["ANTHROPIC_API_KEY"]),
        extractor=ClaudeBookingExtractor(api_key=os.environ["ANTHROPIC_API_KEY"]),
        pms=FakePMS(),
        ledger=DBBookingLedger(pool=pool, hotel_mailbox=mailbox),
    )

    print(f"Processing mock email: {SAMPLE_EMAIL.subject!r}")
    result = use_case.execute(SAMPLE_EMAIL)

    if result is None:
        print("  → skipped (already in ledger)")
    else:
        print(f"  → path={result.path.value}")
        if result.booking_data:
            b = result.booking_data
            print(f"     guest={b.guest_name!r}  {b.arrival_date}→{b.departure_date}")
            print(f"     room={b.room_category!r}  guests={b.num_guests}  conf={b.confidence.value}")
            print(f"     agency={b.agency_name!r}  voucher={b.voucher_code!r}")
        if result.mews_reservation_id:
            print(f"     reservation_id={result.mews_reservation_id}")
        if result.failure_reason:
            print(f"     failure_reason={result.failure_reason}")

    print("Verifying ledger row…")
    with pool.connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, processing_path, guest_name, arrival_date, departure_date, "
            "room_category, num_guests, voucher_code, fake_reservation_id, created_at "
            "FROM extracted_bookings WHERE message_id = %s AND hotel_mailbox = %s",
            (SAMPLE_EMAIL.message_id, mailbox),
        )
        row = cur.fetchone()
    if row is None:
        print("  ✗ no row found")
        return 2
    print(f"  ✓ row id={row[0]}  path={row[1]}  guest={row[2]!r}")
    print(f"     {row[3]}→{row[4]}  room={row[5]!r}  guests={row[6]}  voucher={row[7]!r}")
    print(f"     reservation_id={row[8]}  created_at={row[9]}")

    print("\nReplaying same email to exercise has_processed()…")
    second = use_case.execute(SAMPLE_EMAIL)
    print(f"  → {'skipped (deduped)' if second is None else 'processed again — DEDUP BROKEN'}")

    pool.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
