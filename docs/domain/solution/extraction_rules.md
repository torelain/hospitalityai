# Booking Email Extraction Rules

Business rules for extracting structured booking data from agency emails.
These inform both the LLM prompt design and the post-extraction normalisation logic.

---

## Duration

### German "X Tage" convention

German hotel booking emails express stay length as **days including arrival and departure**, not nights. The system must convert to nights before resolving a voucher code.

| Email says | Actual nights |
|---|---|
| 4 Tage | 3 |
| 5 Tage | 4 |
| 6 Tage | 5 |
| 8 Tage | 7 |

**Rule:** `nights = tage - 1`

Agencies sometimes state both forms in the same email (e.g. *"4 Tage / 3 Nächte"*). When both are present, use **Nächte** as the authoritative value.

---

## Rate Plan → Voucher Code Resolution

### Duration labels

Within rate plan codes, KURZ / MITTEL / LANG map to fixed night counts:

| Label | Nights |
|---|---|
| KURZ | 3 |
| MITTEL | 5 |
| LANG | 7 |

### Resolution steps

1. Extract **rate plan name** from email (e.g. `"Kurzreise"`, `"Kuren"`)
2. Extract **number of nights** (applying the Tage→Nächte rule above if needed)
3. Map nights → duration label (`KURZ` / `MITTEL` / `LANG`)
4. Look up matching voucher code in `RATE_PLANS`
5. Call Mews `vouchers/getAll` with the resolved code to get the rate ID

### Known rate plan keywords found in emails

| Keyword in email | Rate plan |
|---|---|
| `Kurzreise` / `KURZREISE` | Kurzreisen |

> This list grows as more email samples are processed.

---

## OTA Emails

Emails from OTAs (DERTOUR, booking.com, Expedia, Secret Escapes etc.) use their own internal room codes and do not contain a rate plan name or voucher code hint. The mapping from OTA + room type → voucher code must be maintained as a separate lookup table outside of email extraction.
