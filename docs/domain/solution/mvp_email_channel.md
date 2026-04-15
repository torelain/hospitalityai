# MVP — Email Channel

Automated processing of all inbound hotel emails related to bookings and booking modifications. The agent reads emails, classifies intent, interacts with the PMS, and drafts responses for the front desk — replacing fully manual data entry and reducing errors.

## Problem

Wellness and resort hotels receive ~75% of booking modification requests by email. Today, every email requires manual reading, manual PMS entry, and manual reply — creating time cost, quality risk (missed guest wishes, wrong data), and no audit trail linking emails to PMS records.

## Scope

| Email type | Sender | Description |
|---|---|---|
| Booking confirmation | Booking Agency | Agency confirms a booking on behalf of a guest |
| Booking request | Guest (direct) | Guest requests availability and a reservation |
| Modification request | Guest or Agency | Cancellation, date change, room category change, or similar |
| Special request | Guest | Add-on wishes not changing the core booking (e.g. dietary needs) |
| General inquiry | Guest | Question about the hotel, services, or existing booking |

---

## Flow 1 — New Booking (Request or Agency Confirmation)

```mermaid
flowchart TD
    A([Inbound email detected]) --> B{Intent classification}
    B --> |New booking / confirmation| C{Is request complete?}
    B --> |Modification| F1([→ Flow 2])
    B --> |Special request / inquiry| F3([→ Flow 3])

    C --> |Missing info| D[Draft follow-up email requesting missing data]
    C --> |Complete| E{Check PMS availability}

    E --> |Available — firm booking| G[Enter booking in PMS as confirmed]
    E --> |Available — tentative request| H[Enter booking in PMS as optional]
    E --> |Not available| I[Draft rejection email with alternative proposal]

    G --> J[Draft confirmation email for front desk to send]
    H --> K[Draft offer email for front desk to send]
```

**Decision: firm vs. tentative**
- Agency confirmation email → firm booking
- Guest request without explicit commitment → tentative (optional in PMS, offer email drafted)

**PMS entry fields captured from email:**
guest name, contact details, arrival / departure dates, room category, number of guests, special wishes, booking source, agency name (if applicable)

---

## Flow 2 — Booking Modification

```mermaid
flowchart TD
    A([Modification request received]) --> B[Look up booking in PMS\nby name or booking number]
    B --> C{Booking found?}
    C --> |No| D[Draft clarification email]
    C --> |Yes| E{Who is the contract partner?}

    E --> |Direct hotel channel\nmail · phone · website| F{What type of modification?}
    E --> |OTA / Booking Portal| G[Draft rejection: guest must modify via original channel\nincl. hotel's position statement]
    E --> |Booking Agency| H[Draft rejection: modification must go through the agency]

    F --> |Cancellation or date/category change| I{Is modification free\nper cancellation policy?}
    F --> |Minor service adjustment\ne.g. room floor preference| F3([→ Flow 3 — Special request])

    I --> |Free — and new dates/category available| J[Apply change in PMS]
    J --> K[Draft confirmation email for front desk]

    I --> |Costs apply OR new option unavailable| L[Draft response with options and implications\nsee note below]
```

**Draft response when modification has cost or availability issues** must include:
- Applicable cancellation fee (e.g. "80% of booking value per contract")
- Availability check result for requested new dates / room category
- Alternative options if any
- Clear next step for the guest to confirm or decline

---

## Flow 3 — Special Requests and Inquiries

```mermaid
flowchart TD
    A([Special request or inquiry]) --> B{Check hotel rules and data}
    B --> |Request violates policy or not feasible| C[Draft polite rejection for front desk]
    B --> |Request matches defined exception / standard answer| D[Draft confirmation or answer for front desk]
    B --> |General inquiry| E[Draft answer based on hotel data and rules for front desk]
```

All outputs in Flow 3 are drafts — front desk reviews and sends.

---

## Daily Control Outputs

Two recurring reports, generated automatically each morning:

### 1 — Arrival report

Run twice: guests arriving in **2 weeks** and guests arriving in **3 days**.

For each report:
- List of all guests with that check-in date, pulled from PMS, including full booking details and notes
- Each row links to a detail view showing the original booking email(s) and full correspondence history
- Cross-check: PMS notes vs. email thread — flag any discrepancy (missing wish, conflicting data)

### 2 — Unanswered email report

Daily scan of the hotel inbox:
- Every inbound email in scope is matched to an outbound reply
- Emails with no reply drafted or sent are flagged for immediate front desk attention

---

## Key Benefits

| Benefit | Detail |
|---|---|
| Time saving | Eliminates manual PMS entry for email-channel bookings and modifications |
| Error reduction | No missed guest wishes, no mistyped dates or room categories |
| Audit trail | Every PMS record is linked to the originating email thread |
| Staff focus | Front desk reviews and approves; agent handles classification, data entry, and drafting |
