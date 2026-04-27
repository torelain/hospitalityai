# Task: Learn Voucher Code Extraction Rules from Training Data

## What you are working on

Santé Royale Rügen Resort receives hotel booking emails from various travel agencies and
booking platforms. Each booking needs to be entered into Mews (the hotel PMS) with the
correct voucher/promo code. The goal is to teach an AI extractor to read incoming emails
and assign the correct Mews voucher code automatically.

## Current state

The extractor (`services/email-processor/tests/evals/run_extraction.py`) currently:
- Uses Claude to extract booking fields (guest, dates, room, agency) from emails
- Supports multiple bookings per email (list emails like Reisen Aktuell Bookinglist)
- Falls back to a keyword matcher (`resolve_voucher_code` in `adapters/mews/rate_plans.py`)
  to attempt voucher code resolution from the extracted rate plan name
- Has **no learned rules** — all agency/domain/keyword rules have been stripped out

The voucher code catalogue (all valid codes and their groupings) is in:
`services/email-processor/adapters/mews/rate_plans.py` — `RATE_PLANS` dict

## Training data

All training data is in `training/` (gitignored, exists locally):

- `training/Buchungsmails 01.03.-25.04.26/` — 415 `.eml` email files
- `training/Reservierungsbericht *.xlsx` — Mews booking export with ground truth:
  columns include guest name, arrival/departure, nights, agency, voucher code (`Rate` col),
  rate plan name (`Promocode` col), agency reference number
- `training/matched_emails_mews.csv` — pre-matched pairs (email file → Mews booking),
  produced by matching on booking reference numbers and name+date. 102 of 415 emails matched.

## Your task

### Step 1 — Analyse the training data

Load `training/matched_emails_mews.csv` and the `.eml` files. For each matched pair:

1. Parse the email — extract sender domain, subject, body text
2. Read the Mews ground truth — agency name, nights, voucher code (`rate` column in CSV)
3. Derive patterns from the data to map the emails to the voucher code

### Step 2 — Encode rules in the system prompt

Edit the `SYSTEM_PROMPT` in `services/email-processor/tests/evals/run_extraction.py`.

The prompt should give Claude:
- A compact explanation of the voucher code structure (channel · duration · product)
- A table of sender domains → agency/channel
- The full list of available codes from `RATE_PLANS` in `rate_plans.py`, grouped by use case
- Disambiguation signals (keywords, night counts) for ambiguous cases
- Instructions to set `voucher_code` and `voucher_code_confidence` in the tool output

Add `voucher_code` and `voucher_code_confidence` back to `BOOKING_SCHEMA` in the same file.
Update `build_row` to use Claude's `voucher_code` as the primary resolution, falling back to
`resolve_voucher_code` only when Claude returns nothing.

### Step 3 — Optionally encode deterministic rules in rate_plans.py

For patterns that are 100% deterministic from the training data (e.g. a specific sender
domain always produces a specific code for a given night count), you may also encode them in
`adapters/mews/rate_plans.py` as a `resolve_by_context(sender, nights, body)` function.
This reduces API cost for high-volume, predictable cases.

### Step 4 — Update the weekly rule prompt

Update `docs/domain/solution/rule_update_prompt.md` with any new findings so future
weekly runs can maintain the rules without rediscovering them from scratch.

## Key files

| File | Purpose |
|---|---|
| `services/email-processor/tests/evals/run_extraction.py` | Eval script + system prompt |
| `services/email-processor/adapters/mews/rate_plans.py` | Code catalogue + resolver |
| `docs/hotels/ruegen/booking-emails/` | 24 Rügen emails (eval input) |
| `training/matched_emails_mews.csv` | 102 matched training pairs |
| `training/Buchungsmails 01.03.-25.04.26/` | Full 415-email training set |
| `docs/domain/solution/rule_update_prompt.md` | Weekly rule update instructions |

## Additional Information
- Use the room category that are from the PMS (so not the ones from the mail)
