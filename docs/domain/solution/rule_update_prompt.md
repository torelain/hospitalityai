# Weekly Rule Update Prompt

Run this prompt once a week as a scheduled agent to keep the voucher code extraction rules
up to date as new training data arrives.

---

## Context

The email processor for Santé Royale Rügen Resort extracts booking data from incoming emails
and resolves Mews voucher codes. It uses a hybrid approach:

1. **Claude** reads the email and resolves the voucher code using a catalogue in the system prompt
2. **Keyword fallback** (`resolve_voucher_code` in `adapters/mews/rate_plans.py`) is a last
   resort based on rate plan name alone

The system prompt lives in:
`services/email-processor/tests/evals/run_extraction.py` — `SYSTEM_PROMPT`

The voucher code catalogue lives in:
`services/email-processor/adapters/mews/rate_plans.py` — `RATE_PLANS`

The ground truth for rules is derived by matching incoming emails to Mews booking exports.
The matching script and matched output live in:
`training/match_results.csv` (matched pairs: email file → Mews booking with voucher code)
`training/Buchungsmails 25.04.25 - 25.04.26/` (email .eml files)
Mews export: any `.xlsx` file in `training/` named `Reservierungsbericht *.xlsx`
Matching script: `training/match_bookings.py`

---

## Your task

### Step 1 — Reload and re-run the matching

Run `training/match_bookings.py` to refresh `match_results.csv` against any new emails or
Mews exports. Check the match rate; if it dropped significantly, investigate whether a
wider Mews export is needed or whether a new email format appeared.

### Step 2 — Analyse the matched pairs for new patterns

For each matched pair in `training/match_results.csv`:
- Group by: sender domain → agency → voucher code
- Group by: agency + nights → voucher code
- Look for body keywords that correlate with specific codes when agency+nights is ambiguous
- Look for new sender domains
- Look for new package names / product keywords
- Look for voucher codes appearing in Mews that are not yet in `RATE_PLANS`

Key questions:
1. Are there new agencies sending emails? What domain do they use?
2. Are there existing agencies now using a new rate plan or product?
3. Are there codes in the Mews export that don't exist in `rate_plans.py` yet?
4. Has any agency changed which codes they use (e.g. a seasonal special expired)?

### Step 3 — Update the files

**`adapters/mews/rate_plans.py`:**
- Add new codes to the relevant group in `RATE_PLANS` (or create a new group)
- Remove or flag codes that no longer appear in recent Mews exports (may have expired)

**`SYSTEM_PROMPT` in `run_extraction.py`:**
- Update the catalogue / sender briefings with any new senders or codes found
- Remove or annotate codes that belong to expired promotions

### Step 4 — Re-run the eval and verify

```bash
cd services/email-processor
ANTHROPIC_API_KEY=... python3 -m tests.evals.run_extraction
```

Compare results against the previous run in `tests/evals/results/` and against
`docs/hotels/ruegen/buchungen-hackathon.csv`. Check:
- Match rate did not regress
- No previously-resolved codes now show "no match"
- New emails added to `docs/hotels/ruegen/booking-emails/` resolve correctly

### Step 5 — Commit

If changes were made, commit with:
```
chore(rules): weekly rule update YYYY-MM-DD

- Added X new sender domains
- Added Y package name aliases
- Added Z new codes to RATE_PLANS
- Eval: NN/NN emails resolved (up from NN/NN)
```
