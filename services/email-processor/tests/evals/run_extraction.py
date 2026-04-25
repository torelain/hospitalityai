"""
Eval script: run extraction against all .eml files in docs/mail/.

Usage (from services/email-processor/):
    ANTHROPIC_API_KEY=... python -m tests.evals.run_extraction

Prints a table to stdout and writes results to tests/evals/results/.
Each run produces a timestamped JSON file so runs can be compared over time.
"""

import csv
import email as email_lib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).parents[2]))

from adapters.mews.rate_plans import resolve_voucher_code, resolve_by_context
from domain.models import InboundEmail

SYSTEM_PROMPT = """You are a booking data extractor for Santé Royale Rügen Resort (Germany).
Extract all bookings from the email — a single email may contain multiple bookings.
For each booking, resolve the correct Mews voucher code.

## Date handling
- "X Tage" means X days including arrival and departure: nights = Tage - 1.
- When both "Tage" and "Nächte" appear, Nächte is authoritative.
- Return dates as YYYY-MM-DD.

## Voucher code catalogue
Each code encodes: channel · duration · product. Pick the best match using all signals
in the email (sender domain, agency name, package name, keywords, night count).

### Code anatomy
- Channel: VERA=travel agency, REAK=Reisen Aktuell, DIR=direct, ONL=online, AKON=AKON, WÖR=Wörlitz
- Duration: KURZ=3n, MITTEL=5n, LANG=7n (AKON: KURZ=4n, LANG=7n); or explicit 03/05/07/10/14/21
- Product: VP=Vollpension, AI=All Inclusive, AIL=All Inclusive Light
- Kur suffixes: WP=Wellnesspflege, KW=Kurwoche, RK=Rehakur

### Agency signals
- @reisenaktuell.com / @sante-royale.com → Reisen Aktuell (REAK channel)
- @dertouristik.com → Clevertours / DERTOUR (VERA channel)
- @akon.de / @oir.de → AKON
- @pepxpress.com → pepXpress (VERA channel)
- @kurz-mal-weg.de → GetAway (VERA channel)
- @kurzurlaub.de / @check24.de → booking platform → DIR channel (RR-DIR-{DUR}-VP)

### All available codes

**Reisen Aktuell — standard Kurzreisen (Vollpension):**
RR-REAK-KURZ-VP, RR-REAK-MITTEL-VP, RR-REAK-LANG-VP

**Reisen Aktuell — Preisspecial Upgrade to AI (All Inclusive Light):**
Signals: "Upgrade to AI", "AIL", "preisspecial" in email
RR-SO-0226-REAK-KURZ-AIL, RR-SO-0226-REAK-MITTEL-AIL, RR-SO-0226-REAK-LANG-AIL

**Sorgenfrei Spezial — VERA channel (All Inclusive):**
Signals: "Sorgenfrei", agency via VERA channel (clevertours, pepXpress, getaway, PA Touristik, etc.)
RR-SO-0326-VERA-03-AI (3n), RR-SO-0326-VERA-KURZ-AI (3n), RR-SO-0326-VERA-05-AI (5n),
RR-SO-0326-VERA-MITTEL-AI (5n), RR-SO-0326-VERA-07-AI (7n), RR-SO-0326-VERA-LANG-AI (7n)

**Sorgenfrei Spezial — Reisen Aktuell (All Inclusive):**
Signals: "Sorgenfrei" + Reisen Aktuell sender
RR-SO-0326-VERA-KURZ-AI, RR-SO-0326-VERA-MITTEL-AI, RR-SO-0326-VERA-LANG-AI

**VERA channel — standard Kurzreisen (Vollpension):**
Signals: clevertours/DERTOUR, pepXpress, reisewell (AKON sub-brand), PA Touristik, GetAway, Compass
RR-VERA-KURZ-VP, RR-VERA-MITTEL-VP, RR-VERA-LANG-VP

**AKON programme:**
Signals: @akon.de, "AKON" in email; KURZ=4n, LANG=7n
RR-AKON-KURZ-VP (4n), RR-AKON-LANG-VP (7n)
With Begleitperson: RR-AKON-KURZ-VP-BP (4n), RR-AKON-LANG-VP-BP (7n)
reisewell (3/5/7n wellness, not rehab) → RR-VERA-KURZ/MITTEL/LANG-VP

**Kuren (long-stay rehabilitation, 7/14/21 nights):**
Signals: "Kur", "Kennenlernwoche", "Rehabilitation", explicit 7/14/21n stay
VERA: RR-VERA-07/14/21-VP-WP/KW/RK
DIR:  RR-DIR-07/14/21-VP-WP/KW/RK

**Wörlitz Buspendel:** Signal: "Wörlitz" → RR-WÖR-VP

**Weihnachten/Silvester (10n stay around Christmas):**
Signals: December dates, 10 nights, "Weihnachten", "Silvester"
VERA: RR-SO-1225-VERA-10-VP-WS, RR-SO-1225-VERA-05-VP-WE, RR-SO-1225-VERA-05-VP-SI
REAK: RR-SO-1225-VERA-10-VP-WS (Reisen Aktuell guests use VERA code for Christmas)

**Direct / online bookings (no agency):**
RR-DIR-KURZ/MITTEL/LANG-VP, RR-ONL-KURZ/MITTEL/LANG-VP

**VIP:** RR-SO-DIR-VIP, RR-SO-ONL-VIP

Set voucher_code_confidence to "high" when you can identify the agency from the sender domain,
"low" when you are inferring from context only."""

BOOKING_SCHEMA = {
    "type": "object",
    "properties": {
        "guest_name": {"type": "string"},
        "arrival_date": {"type": "string", "description": "YYYY-MM-DD"},
        "departure_date": {"type": "string", "description": "YYYY-MM-DD"},
        "room_category": {"type": "string"},
        "num_guests": {"type": "integer"},
        "rate_plan_name": {"type": "string", "description": "Rate plan or package name as stated in the email. Omit if not identifiable."},
        "agency_name": {"type": "string"},
        "guest_email": {"type": "string"},
        "special_wishes": {"type": "string"},
        "voucher_code": {"type": "string", "description": "Mews voucher code resolved from sender domain + nights + keywords, e.g. RR-VERA-LANG-VP. Omit if not resolvable."},
        "voucher_code_confidence": {"type": "string", "enum": ["high", "low"], "description": "high if agency identified from sender domain, low if guessed from rate plan name only."},
        "confidence": {"type": "string", "enum": ["high", "low"]},
    },
    "required": ["guest_name", "arrival_date", "departure_date", "room_category", "num_guests", "confidence"],
}

EXTRACT_BOOKING_TOOL = {
    "name": "extract_bookings",
    "description": "Extract all bookings from a hotel booking email. A single email may contain multiple bookings (e.g. Reisen Aktuell bookinglists). Return one entry per booking.",
    "input_schema": {
        "type": "object",
        "properties": {
            "bookings": {
                "type": "array",
                "items": BOOKING_SCHEMA,
                "description": "List of bookings found in the email. Usually one, but may be several for list emails.",
            }
        },
        "required": ["bookings"],
    },
}

MAIL_DIR = Path(__file__).parents[4] / "docs" / "hotels" / "ruegen" / "booking-emails"


def parse_eml(path: Path) -> InboundEmail:
    with open(path, "rb") as f:
        msg = email_lib.message_from_bytes(f.read())

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                body = part.get_payload(decode=True).decode(charset, errors="replace")
                break
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")

    date_str = msg.get("Date", "")
    try:
        from email.utils import parsedate_to_datetime
        received_at = parsedate_to_datetime(date_str)
    except Exception:
        received_at = datetime.now()

    return InboundEmail(
        message_id=msg.get("Message-ID", path.name),
        from_email=msg.get("From", ""),
        from_name=msg.get("From", ""),
        to_email=msg.get("To", ""),
        subject=msg.get("Subject", ""),
        text_body=body,
        received_at=received_at,
    )


def extract_raw(client: anthropic.Anthropic, eml: InboundEmail) -> list[dict]:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[EXTRACT_BOOKING_TOOL],
        tool_choice={"type": "tool", "name": "extract_bookings"},
        messages=[
            {
                "role": "user",
                "content": f"From: {eml.from_email}\nSubject: {eml.subject}\n\n{eml.text_body}",
            }
        ],
    )
    tool_use = next(b for b in message.content if b.type == "tool_use")
    return tool_use.input.get("bookings", [])


RESULTS_DIR = Path(__file__).parent / "results"


def build_row(path: Path, data: dict, eml: "InboundEmail", booking_index: int = 0) -> dict:
    from datetime import date as date_type

    arrival = data.get("arrival_date")
    departure = data.get("departure_date")
    try:
        nights = (date_type.fromisoformat(departure) - date_type.fromisoformat(arrival)).days
    except Exception:
        nights = None

    rate_plan = data.get("rate_plan_name")

    # 1. Use Claude's resolved code if present
    voucher = data.get("voucher_code") or None
    resolve_method = "claude" if voucher else "-"

    # 2. Rule-based context resolver as fallback
    if not voucher and nights is not None:
        try:
            voucher = resolve_by_context(eml.from_email, nights, eml.text_body, rate_plan or "")
            resolve_method = "rules"
        except Exception:
            pass

    # 3. Keyword resolver as last resort
    if not voucher and rate_plan and nights is not None:
        try:
            voucher = resolve_voucher_code(rate_plan, nights)
            resolve_method = "keyword"
        except Exception:
            pass

    suffix = f" [{booking_index + 1}]" if booking_index > 0 else ""
    return {
        "file": path.name + suffix,
        "arrival_date": arrival,
        "departure_date": departure,
        "nights": nights,
        "num_guests": data.get("num_guests"),
        "rate_plan_name": rate_plan,
        "voucher_code": voucher,
        "resolve_method": resolve_method,
        "room_category": data.get("room_category"),
        "guest_name": data.get("guest_name"),
        "agency_name": data.get("agency_name"),
        "confidence": data.get("confidence"),
        "error": None,
    }


def print_table(rows: list[dict]) -> None:
    col = {"file": 40, "arrival": 12, "depart": 12, "nights": 6, "guests": 6, "voucher": 32, "method": 8, "conf": 5}
    header = (
        f"{'File':<{col['file']}} {'Arrival':<{col['arrival']}} {'Depart':<{col['depart']}} "
        f"{'Nights':>{col['nights']}} {'Guests':>{col['guests']}} "
        f"{'Voucher (resolved)':<{col['voucher']}} {'Method':<{col['method']}} {'Conf':<{col['conf']}}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        if r["error"]:
            print(f"{r['file'][:col['file']]:<{col['file']}} ERROR: {r['error']}")
            continue
        print(
            f"{r['file'][:col['file']]:<{col['file']}} "
            f"{(r['arrival_date'] or '?'):<{col['arrival']}} "
            f"{(r['departure_date'] or '?'):<{col['depart']}} "
            f"{str(r['nights'] or '?'):>{col['nights']}} "
            f"{str(r['num_guests'] or '?'):>{col['guests']}} "
            f"{(r['voucher_code'] or 'no match')[:col['voucher']]:<{col['voucher']}} "
            f"{(r.get('resolve_method') or '-'):<{col['method']}} "
            f"{(r['confidence'] or '?'):<{col['conf']}}"
        )


def save_results(rows: list[dict], run_at: datetime) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    slug = run_at.strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"{slug}.json"
    json_path.write_text(json.dumps({"run_at": run_at.isoformat(), "rows": rows}, indent=2))

    csv_path = RESULTS_DIR / f"{slug}.csv"
    fields = ["file", "arrival_date", "departure_date", "nights", "num_guests", "rate_plan_name", "voucher_code", "resolve_method", "room_category", "guest_name", "agency_name", "confidence", "error"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    return json_path


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    run_at = datetime.now()

    eml_files = sorted(MAIL_DIR.glob("*.eml"))
    if not eml_files:
        print(f"No .eml files found in {MAIL_DIR}")
        sys.exit(1)

    rows = []
    for path in eml_files:
        eml = parse_eml(path)
        try:
            bookings = extract_raw(client, eml)
            for i, booking in enumerate(bookings):
                rows.append(build_row(path, booking, eml, i))
        except Exception as e:
            rows.append({"file": path.name, "error": str(e), **{k: None for k in ["arrival_date", "departure_date", "nights", "num_guests", "rate_plan_name", "voucher_code", "resolve_method", "room_category", "guest_name", "agency_name", "confidence"]}})

    print_table(rows)

    out = save_results(rows, run_at)
    print(f"\nResults saved to {out.parent.relative_to(Path.cwd())}/ ({run_at.strftime('%Y%m%d_%H%M%S')})")


if __name__ == "__main__":
    main()
