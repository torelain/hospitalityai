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
- Has **no learned rules** — all agency/domain/keyword rules have been stripped out


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
3. Derive patterns from the data to map the emails to the voucher code:
   - Which sender domains map to which agency/channel?
   - Which agency + night count always produces the same voucher code?
   - Which body keywords (product names, package names) disambiguate when agency+nights
     alone is not enough?
   - Are there package name aliases (guest-facing product names that map to Mews rate plans)?

### Step 2 — Encode rules in the system prompt
Edit the `SYSTEM_PROMPT` in `services/tujur/tests/evals/run_extraction.py`.

The prompt should give Claude:
- A compact explanation of the voucher code structure (channel · duration · product)
- A table of sender domains → agency/channel
- Disambiguation signals (keywords, night counts) for ambiguous cases
- Instructions to set `voucher_code` and `voucher_code_confidence` in the tool output

Add `voucher_code` and `voucher_code_confidence` back to `BOOKING_SCHEMA` in the same file.
Update `build_row` to use Claude's `voucher_code` as the primary resolution, falling back to
`resolve_voucher_code` only when Claude returns nothing.


## Key files
| File | Purpose |
|---|---|
| `services/tujur/tests/evals/run_extraction.py` | Eval script + system prompt |
| `docs/hotels/ruegen/booking-emails/` | 24 Rügen emails (eval input) |
| `training/matched_emails_mews.csv` | 102 matched training pairs |
| `training/Buchungsmails 01.03.-25.04.26/` | Full 415-email training set |
| `docs/domain/solution/rule_update_prompt.md` | Weekly rule update instructions |

## Additional Information
- Use the room category that are from the PMS (so not the ones from the mail)
- Please only extract a rule if the sample size is larger than 5
