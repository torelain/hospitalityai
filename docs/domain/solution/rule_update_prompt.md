# Weekly Rule Update Prompt

Run this prompt once a week as a scheduled agent to keep the voucher code extraction rules
up to date as new training data arrives.

---

## Context

The email processor for Santé Royale Rügen Resort extracts booking data from incoming emails
and resolves Mews voucher codes. It uses a hybrid approach:

1. **Claude** reads the email and resolves the voucher code using a catalogue in the system prompt
2. **Rule-based fallback** (`resolve_by_context` in `adapters/mews/rate_plans.py`) handles cases
   where Claude cannot identify the agency from the sender domain
3. **Keyword fallback** (`resolve_voucher_code`) is a last resort based on rate plan name alone

The system prompt catalogue lives in:
`services/email-processor/tests/evals/run_extraction.py` — `SYSTEM_PROMPT`

Supporting rules live in:
`services/email-processor/adapters/mews/rate_plans.py` — `PACKAGE_NAME_ALIASES`, `AGENCY_NIGHTS_TO_CODE`, `SENDER_DOMAIN_TO_AGENCY`

The ground truth for rules is derived by matching incoming emails to Mews booking exports.
The matching script and matched output live in:
`training/matched_emails_mews.csv` (matched pairs: email file → Mews booking with voucher code)
`training/Buchungsmails 01.03.-25.04.26/` (email .eml files)
Mews export: any `.xlsx` file in `training/` named `Reservierungsbericht *.xlsx`

---

## Your task

### Step 1 — Reload and re-run the matching

Run the matching script to incorporate any new emails or Mews exports in `training/`:

```python
# From services/email-processor/
python3 - << 'EOF'
# (paste the full matching script from the last time it was run,
#  or reconstruct it: load Mews xlsx, load .eml files, match by ref number + name+date,
#  write matched_emails_mews.csv)
EOF
```

Check the match rate. If it dropped significantly, investigate whether a new Mews export
is needed (wider date range) or whether new email formats appeared.

### Step 2 — Analyse the matched pairs for new patterns

For each matched pair in `training/matched_emails_mews.csv`:
- Group by: sender domain → agency → voucher code
- Group by: agency + nights → voucher code
- Look for body keywords that correlate with specific codes when agency+nights is ambiguous
- Look for new sender domains not yet in `SENDER_DOMAIN_TO_AGENCY`
- Look for new package names / product keywords not yet in `PACKAGE_NAME_ALIASES`
- Look for voucher codes appearing in Mews that are not yet in `RATE_PLANS`

Key questions to answer:
1. Are there new agencies sending emails? What domain do they use?
2. Are there existing agencies now using a new rate plan or product?
3. Are there codes in the Mews export that don't exist in `rate_plans.py` yet?
4. Has any agency changed which codes they use (e.g. a seasonal special expired)?

### Step 3 — Update the files

**`adapters/mews/rate_plans.py`:**
- Add new sender domains to `SENDER_DOMAIN_TO_AGENCY`
- Add new package name aliases to `PACKAGE_NAME_ALIASES`
- Add new codes to the relevant group in `RATE_PLANS` (or create a new group)
- Update `AGENCY_NIGHTS_TO_CODE` if a deterministic rule emerged from the data
- Remove or flag codes that no longer appear in recent Mews exports (may have expired)

**`SYSTEM_PROMPT` in `run_extraction.py`:**
- Update the "Agency signals" section if new sender domains were found
- Update the "All available codes" catalogue with any new codes or groups
- Add new product keywords to the relevant section if they appeared in training emails
- Remove or annotate codes that belong to expired promotions (e.g. SO-0226 codes
  were a Feb 2026 special — flag once they stop appearing in new bookings)

### Step 4 — Re-run the eval and verify

```bash
cd services/email-processor
ANTHROPIC_API_KEY=... python3 -m tests.evals.run_extraction
```

Compare results against the previous run in `tests/evals/results/`. Check:
- Match rate did not regress
- No previously-resolved codes now show "no match"
- New emails added to `docs/hotels/ruegen/booking-emails/` resolve correctly
- Low-confidence resolutions decreased or stayed the same

### Step 5 — Commit

If changes were made, commit with:
```
chore(rules): weekly rule update YYYY-MM-DD

- Added X new sender domains
- Added Y package name aliases
- Added Z new codes to RATE_PLANS
- Eval: NN/NN emails resolved (up from NN/NN)
```

---

## What we know from prior analysis (do not re-derive, just extend)

**Sender domain → agency (confirmed from training data):**
| Domain | Agency | Channel |
|---|---|---|
| @reisenaktuell.com, @sante-royale.com | Reisen Aktuell | REAK |
| @dertouristik.com | Clevertours / DERTOUR | VERA |
| @akon.de, @oir.de | AKON Aktivkonzept | AKON/VERA |
| @pepxpress.com | pepXpress | VERA |
| @kurz-mal-weg.de | GetAway Travel | VERA |

**Key disambiguation keywords (confirmed from training data):**
| Keyword in email body | Resolves to |
|---|---|
| "Upgrade to AI" / "AIL" / "preisspecial" | RR-SO-0226-REAK-{DUR}-AIL (Reisen Aktuell only) |
| "Sorgenfrei" | RR-SO-0326-VERA-{DUR}-AI |
| "reisewell" | RR-VERA-{DUR}-VP (AKON sub-brand, standard wellness) |
| "Kennenlernwoche" | RR-VERA-07-VP-KW (Kuren, pepXpress) |
| "Begleitperson" | RR-AKON-KURZ-VP-BP |
| "Wörlitz" | RR-WÖR-VP |
| Weihnachten/Silvester + 10n | RR-SO-1225-VERA-10-VP-WS |

**AKON night count (different from global 3/5/7):**
- 4 nights → KURZ (AKON programme)
- 7 nights → LANG (AKON programme)
- 3 nights from AKON → reisewell (uses VERA codes, not AKON codes)

**One email can contain multiple bookings** (e.g. Reisen Aktuell Bookinglist, AKON list emails).
Each booking must be extracted and resolved independently.

**Unresolvable email types** (expected, do not try to force a code):
- SELTA MED "Aktueller Buchungsstand" — bulk status list, not individual bookings
- Direct inquiries with no agency/rate information (low confidence, omit voucher_code)
- Internal hotel operations emails (lock dates, departure info, etc.)
