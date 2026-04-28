# Task: Learn Voucher Code Extraction Rules from Training Data

## What you are working on

Santé Royale Rügen Resort receives hotel booking emails from various travel agencies and
booking platforms. Each booking needs to be entered into Mews (the hotel PMS) with the
correct voucher/promo code. The goal is to teach an AI extractor to read incoming emails
and assign the correct Mews voucher code automatically.

## Current state

The extractor (`services/tujur/tests/evals/run_extraction.py`) currently:
- Uses Claude to extract booking fields (guest, dates, room, agency) from emails
- Supports multiple bookings per email (list emails like Reisen Aktuell Bookinglist)
- Has a basic `SYSTEM_PROMPT` with date handling only — no learned rules
- Falls back to `resolve_voucher_code` (keyword matcher) only when Claude returns nothing

The voucher code catalogue (all valid codes and their groupings) is in:
`services/tujur/adapters/mews/rate_plans.py` — `RATE_PLANS` dict.
**Do not remove this.** It is the source of truth for valid codes and powers the fallback
keyword resolver. Only the learned rules (domain mappings, keyword signals) belong in the
system prompt.

## Training data

All training data is in `training/` (gitignored, exists locally):

- `training/Buchungsmails 01.03.-25.04.26/` — 415 `.eml` email files
- `training/Reservierungsbericht *.xlsx` — Mews booking export with ground truth:
  columns include guest name, arrival/departure, nights, agency, voucher code (`Rate` col),
  rate plan name (`Promocode` col), agency reference number
- `training/matched_emails_mews.csv` — pre-matched pairs (email file → Mews booking),
  produced by matching on booking reference numbers and name+date. 102 of 415 emails matched.

## Ground truth for validation

`docs/hotels/ruegen/buchungen-hackathon.csv` — manually curated ground truth for the
emails in `docs/hotels/ruegen/booking-emails/`. Each row has the email filename and the
expected voucher code (`Paket` column).

Run the eval:
```bash
cd services/tujur
ANTHROPIC_API_KEY=... python3 -m tests.evals.run_extraction
```

Compare against ground truth order-independently — one email may contain multiple bookings,
so match by filename and check if any eval row from that file produced the expected code.

Target: >80% exact voucher code match on the hackathon set.

## Your task

### Step 1 — Analyse the training data

Load `training/matched_emails_mews.csv` and the `.eml` files. For each matched pair:

1. Parse the email — extract sender domain, subject, body text
2. Read the Mews ground truth — agency name, nights, voucher code (`rate` column in CSV)
3. Derive patterns:
   - Which sender domains map to which agency/channel?
   - Which agency + night count always produces the same voucher code?
   - Which body keywords (product names, package names) disambiguate when agency+nights
     alone is not enough?
   - Are there package name aliases (guest-facing product names that map to Mews rate plans)?
   - What types of emails are NOT individual bookings?

### Step 2 — Encode learnings in the system prompt only

Edit `SYSTEM_PROMPT` in `services/tujur/tests/evals/run_extraction.py`.

**Approach: briefing, not rules.** Give Claude the knowledge as context so it can reason —
do not write if/else logic or decision trees. Claude should be able to handle deviations,
new senders, and edge cases by understanding the *why* behind the patterns.

The prompt should contain:
- Voucher code structure explanation (channel · duration · product · what each segment means)
- What we know about known senders — their agency, typical channel, common products
- Disambiguation signals (keywords, night counts) for ambiguous cases
- The full list of available codes from `RATE_PLANS`, grouped by use case
- Guidance on unknown senders: infer from company name, email style, context
- What is NOT a booking (bulk status reports, ops emails, cancellations)

**Do not encode deterministic rules in Python.** The goal is to let Claude reason with
soft knowledge rather than hard code so it can handle cases we have not seen before.

`voucher_code` and `voucher_code_confidence` must be in `BOOKING_SCHEMA`.
`build_row` must use Claude's `voucher_code` as primary, `resolve_voucher_code` as fallback.

### Step 3 — Validate and iterate

Run the eval and compare against `docs/hotels/ruegen/buchungen-hackathon.csv`.
Iterate on the system prompt until the target accuracy is reached.

### Step 4 — Update the weekly rule prompt

Update `docs/domain/solution/rule_update_prompt.md` with findings so future weekly runs
can maintain the prompt without rediscovering patterns from scratch.

## Key files

| File | Purpose |
|---|---|
| `services/tujur/tests/evals/run_extraction.py` | Eval script + system prompt |
| `services/tujur/adapters/mews/rate_plans.py` | Code catalogue + keyword fallback — do not strip |
| `docs/hotels/ruegen/booking-emails/` | Rügen emails (eval input) |
| `docs/hotels/ruegen/buchungen-hackathon.csv` | Ground truth for eval |
| `training/matched_emails_mews.csv` | 102 matched training pairs |
| `training/Buchungsmails 01.03.-25.04.26/` | Full 415-email training set |
| `docs/domain/solution/rule_update_prompt.md` | Weekly rule update instructions |
