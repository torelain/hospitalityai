"""
Eval script: run extraction against all .eml files in docs/mail/.

Usage (from services/tujur/):
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

from adapters.mews.rate_plans import resolve_voucher_code
from domain.models import InboundEmail

SYSTEM_PROMPT = """You are a booking data extractor for Santé Royale Rügen Resort (Göhren, Germany).
Extract every confirmed/requested booking from the email. A single email may contain
many bookings (rooming lists, AKON participant lists). Process each booking independently.

## Output
For each booking return: guest_name, arrival_date (YYYY-MM-DD),
departure_date (YYYY-MM-DD), room_category, num_guests, agency_name, rate_plan_name,
voucher_code, voucher_code_confidence, and an overall confidence.

## Date handling
- "X Tage" = X days including arrival and departure → nights = Tage − 1.
- When both "Tage" and "Nächte" appear, "Nächte" wins.
- Date formats vary (14.05.26, 03-Aug-2026, 5.Okt.26, "15 August 2026") — normalise to ISO.

## Room category
Map the email's free-text room description to **one of the canonical Mews categories**
(use this exact spelling — never invent new labels):
- Doppelzimmer
- Doppelzimmer Komfort
- Doppelzimmer mit Balkon
- Doppelzimmer Komfort mit Balkon
- Doppelzimmer mit Meerblick
- Doppelzimmer mit Meerblick (mit Balkon)
- Doppelzimmer mit Meerblick (ohne Balkon)
- Suite (mit Meerblick)
- Suite (ohne Meerblick)
- Hundefreundliches Zimmer
Heuristics: "EZ" / "Einzelzimmer" → Doppelzimmer (single use); "DZ Standard" →
Doppelzimmer; "Hund" / "mit Hund" → Hundefreundliches Zimmer; "Meerblick" →
the matching Meerblick variant (with/ohne Balkon if specified).

## Voucher code (Mews `Rate`)
Voucher codes follow the structure `RR-{CHANNEL}-{DURATION}-VP[-{SUFFIX}]`, where:
- CHANNEL identifies the booking source
- DURATION is `KURZ` (short), `MITTEL` (mid), `LANG` (long), or a numeric night count
- VP = Vollpension (full board), AI = All Inclusive, optional product suffix

### Channels (derived from sender domain / agency)
| Sender / agency | Channel | Notes |
|---|---|---|
| `@reisenaktuell.com` (Reisen Aktuell) | REAK | bookinglist emails, multi-booking |
| `@kurz-mal-weg.de` / `@kurzmalweg.zohodesk.eu` (GetAway Travel) | VERA | |
| `@pa-touristik.info` (PA Touristik / Wörlitz Tourist) | VERA | Wörlitz + Kuren focus |
| `@dertouristik.com` (Clevertours / DERTOUR) | VERA | |
| `@pepxpress.com` (pepXpress) | VERA | |
| `@seltamed.de` (Selta Med) | VERA | mostly Kuren (7/14 nights) |
| `@schauinsland-reisen.de` | VERA | |
| `@compassmail.de` (Compass Kreuzfahrten) | VERA | |
| `@akon.de` (AKON Aktivkonzept / reisewell.de) | AKON | KURZ=4 nights, LANG=7 nights |
| Booking.com / OTA confirmations | OTA | code shape varies, prefer keyword fallback |
| Direct guest email (`gmx`, `web.de`, `t-online`, `gmail`, etc.) — first-party request | DIR | phone/email request |
| Hotel booking engine confirmation | ONL | "Buchungssystem", "Mews Booking Engine" |

### Duration mapping (nights → DURATION token)
- `KURZ`: 3 nights (4 for AKON)
- `MITTEL`: 5 nights
- `LANG`: 7 nights (also 7 for AKON)
- Other night counts use the numeric form, e.g. `RR-VERA-07-VP-KW`, `RR-VERA-14-VP-WP`.

### Default codes by (channel, nights)
- REAK: 3→`RR-REAK-KURZ-VP`, 5→`RR-REAK-MITTEL-VP`, 7→`RR-REAK-LANG-VP`
- VERA: 3→`RR-VERA-KURZ-VP`, 5→`RR-VERA-MITTEL-VP`, 7→`RR-VERA-LANG-VP`
- AKON: 4→`RR-AKON-KURZ-VP`, 7→`RR-AKON-LANG-VP`
- DIR : 3→`RR-DIR-KURZ-VP`, 5→`RR-DIR-MITTEL-VP`, 7→`RR-DIR-LANG-VP`
- ONL : 3→`RR-ONL-KURZ-VP`, 5→`RR-ONL-MITTEL-VP`, 7→`RR-ONL-LANG-VP`

### Disambiguation keywords (override the default)
- "Wörlitz" / "Wörlitz Buspendel" + 4 nights (PA Touristik) → `RR-WÖR-VP`
- "Kuren" / "Kur" / "Kurpaket" + 7 nights → `RR-VERA-07-VP-WP` (default Wochenpauschale).
  Variants: "Kurwoche" → `-VP-KW`; "Rügener Kururlaub" / "Reha-Kur" → `-VP-RK`.
  14 nights → `RR-VERA-14-VP-WP` (or `-KW` / `-RK` by same rule).
- "Verlängerungsnacht" or a standalone 1-night stay → `RR-ST-0024-VERLÄNGERUNG-01-VP`
- "Begleitperson" / "Begl." + AKON → append `-BP` (`RR-AKON-KURZ-VP-BP`, `RR-AKON-LANG-VP-BP`)
- "VIP" + direct/online → `RR-SO-DIR-VIP` (direct) or `RR-SO-ONL-VIP` (booking engine)
- "Weihnachten" / "Wintergedöns" + 10 nights in Dec/Jan → `RR-SO-1225-{CHANNEL}-10-VP-WS`
- "Silvester" + 5 nights in Dec/Jan → `RR-SO-1225-{CHANNEL}-05-VP-SI`
- "Sorgenfrei Spezial" / "All Inclusive" package → `RR-SO-0326-{CHANNEL}-{DUR}-AI`
- "Preisspecial Upgrade to AI" + Reisen Aktuell → `RR-SO-0226-REAK-{DUR}-AIL`

### Confidence for voucher_code
- "high" — sender domain matched a known agency AND nights match a default duration
  AND no ambiguous keywords. E.g. `@reisenaktuell.com` + 7 nights → `RR-REAK-LANG-VP`.
- "low" — sender unknown, nights atypical, ambiguous keywords (e.g. "Kur" but nights
  don't match a Kuren package), forwarded chains where the original agency is unclear,
  or any OTA/Booking.com email (legacy code shapes, prefer human review).
  Leave `voucher_code` blank when you have no defensible guess — never invent a code.

## Confidence
Set confidence: "low" when the booking is incomplete (missing dates / guest) or when
the email is not actually a booking notification."""

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
        "voucher_code": {"type": "string", "description": "Mews voucher code (e.g. RR-VERA-LANG-VP). Omit if you have no defensible guess."},
        "voucher_code_confidence": {"type": "string", "enum": ["high", "low"], "description": "high only when sender domain + nights match a default rule with no ambiguity."},
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

MAIL_DIR = Path(__file__).parents[4] / "docs" / "hotels" / "ruegen" / os.environ.get("MAIL_SUBDIR", "booking-emails")


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

    voucher = (data.get("voucher_code") or "").strip() or None
    voucher_confidence = data.get("voucher_code_confidence")
    resolve_method = "claude" if voucher else "-"

    if not voucher and rate_plan and nights is not None:
        try:
            voucher = resolve_voucher_code(rate_plan, nights)
            if voucher:
                resolve_method = "keyword"
                voucher_confidence = "low"
        except Exception:
            pass

    suffix = f" [{booking_index + 1}]" if booking_index > 0 else ""
    confidence = data.get("confidence")
    needs_review = not voucher or confidence == "low" or voucher_confidence == "low"
    return {
        "file": path.name + suffix,
        "arrival_date": arrival,
        "departure_date": departure,
        "nights": nights,
        "num_guests": data.get("num_guests"),
        "rate_plan_name": rate_plan,
        "voucher_code": voucher,
        "voucher_code_confidence": voucher_confidence,
        "resolve_method": resolve_method,
        "room_category": data.get("room_category"),
        "guest_name": data.get("guest_name"),
        "agency_name": data.get("agency_name"),
        "confidence": confidence,
        "needs_review": needs_review,
        "review_reason": None,
        "error": None,
    }


def build_review_row(path: Path, reason: str) -> dict:
    """Synthesise a row for an .eml that produced no Claude bookings — flag for human review."""
    return {
        "file": path.name,
        "arrival_date": None,
        "departure_date": None,
        "nights": None,
        "num_guests": None,
        "rate_plan_name": None,
        "voucher_code": None,
        "voucher_code_confidence": None,
        "resolve_method": "-",
        "room_category": None,
        "guest_name": None,
        "agency_name": None,
        "confidence": None,
        "needs_review": True,
        "review_reason": reason,
        "error": None,
    }


def print_table(rows: list[dict]) -> None:
    col = {"file": 40, "arrival": 12, "depart": 12, "nights": 6, "guests": 6, "voucher": 32, "method": 8, "conf": 5, "review": 7}
    header = (
        f"{'File':<{col['file']}} {'Arrival':<{col['arrival']}} {'Depart':<{col['depart']}} "
        f"{'Nights':>{col['nights']}} {'Guests':>{col['guests']}} "
        f"{'Voucher (resolved)':<{col['voucher']}} {'Method':<{col['method']}} "
        f"{'Conf':<{col['conf']}} {'Review':<{col['review']}}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        if r["error"]:
            print(f"{r['file'][:col['file']]:<{col['file']}} ERROR: {r['error']}")
            continue
        review_flag = "REVIEW" if r.get("needs_review") else "ok"
        print(
            f"{r['file'][:col['file']]:<{col['file']}} "
            f"{(r['arrival_date'] or '?'):<{col['arrival']}} "
            f"{(r['departure_date'] or '?'):<{col['depart']}} "
            f"{str(r['nights'] or '?'):>{col['nights']}} "
            f"{str(r['num_guests'] or '?'):>{col['guests']}} "
            f"{(r['voucher_code'] or 'no match')[:col['voucher']]:<{col['voucher']}} "
            f"{(r.get('resolve_method') or '-'):<{col['method']}} "
            f"{(r['confidence'] or '?'):<{col['conf']}} "
            f"{review_flag:<{col['review']}}"
        )


def save_results(rows: list[dict], run_at: datetime) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    slug = run_at.strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"{slug}.json"
    json_path.write_text(json.dumps({"run_at": run_at.isoformat(), "rows": rows}, indent=2))

    csv_path = RESULTS_DIR / f"{slug}.csv"
    fields = ["file", "arrival_date", "departure_date", "nights", "num_guests", "rate_plan_name", "voucher_code", "voucher_code_confidence", "resolve_method", "room_category", "guest_name", "agency_name", "confidence", "needs_review", "review_reason", "error"]
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
            if not bookings:
                rows.append(build_review_row(path, "no_bookings_extracted"))
                continue
            for i, booking in enumerate(bookings):
                rows.append(build_row(path, booking, eml, i))
        except Exception as e:
            rows.append({
                "file": path.name,
                "error": str(e),
                "needs_review": True,
                "review_reason": "extraction_error",
                **{k: None for k in ["arrival_date", "departure_date", "nights", "num_guests", "rate_plan_name", "voucher_code", "voucher_code_confidence", "resolve_method", "room_category", "guest_name", "agency_name", "confidence"]},
            })

    print_table(rows)

    review_count = sum(1 for r in rows if r.get("needs_review"))
    print(f"\n{review_count}/{len(rows)} rows flagged for human review.")

    out = save_results(rows, run_at)
    print(f"Results saved to {out.parent.relative_to(Path.cwd())}/ ({run_at.strftime('%Y%m%d_%H%M%S')})")


if __name__ == "__main__":
    main()
