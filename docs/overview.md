# Hospitality AI — Full Overview

> Single-page reference combining all project documentation. Source files live in their respective locations — this document is generated for review purposes.

---

## Table of Contents

1. [Project](#1-project)
2. [Glossary](#2-glossary)
3. [Architecture](#3-architecture)
4. [Domain — As-Is](#4-domain--as-is)
5. [Domain — MVP Email Channel (Prior Scope Doc)](#5-domain--mvp-email-channel-prior-scope-doc)
6. [Solution — MVP Flows](#6-solution--mvp-flows)
7. [Open Questions](#7-open-questions)

---

## 1. Project

Hospitality AI is an operating system for hotels. It centralizes hotel operations, starting with the booking process — one platform for all booking channels, guest interactions, and hotel operations.

**Current focus:** Booking process — integrating all incoming booking channels into one system.

### Booking Channels

| Channel | Integration method |
|---|---|
| Hotel Website | Direct API |
| Booking Agencies (e.g. travel agents) | Email (parsed, AI-powered) |
| Booking Portals (e.g. booking.com) | API via Channel Manager |

---

## 2. Glossary

| Term | Definition |
|---|---|
| **Booking Assistant** | Hotel staff who process and manage incoming bookings |
| **Booking Agency** | External travel agent that sends booking confirmations via email |
| **Booking Partner / Portal** | Large OTAs (e.g. booking.com) that integrate via the Channel Manager |
| **Channel Manager** | Third-party system that manages availability and rates across booking portals |
| **ERP System** | The hotel's core back-office system where bookings are recorded |
| **PMS (Property Management System)** | The hotel's property management software — the operational layer of the ERP where reservations are created and managed day-to-day |
| **Mews** | The PMS used by the first customer |
| **Hotel Manager** | Oversees hotel operations and performance |
| **Hotel Guest** | Books rooms and manages their stay |

---

## 3. Architecture

### C1 — System Context

> Shows Hospitality AI in relation to its users and external systems.

```mermaid
C4Context
  title System Context — Hospitality AI

  Person(guest, "Hotel Guest", "Books rooms and manages their stay")
  Person(assistant, "Booking Assistant", "Processes and manages incoming bookings")
  Person(manager, "Hotel Manager", "Oversees hotel operations and performance")

  System(hospitality_ai, "Hospitality AI", "Operating system for hotels. Centralizes booking management and hotel operations.")

  System_Ext(website, "Hotel Website", "Direct online booking channel for guests")
  System_Ext(channel_manager, "Channel Manager", "Manages availability and rates across booking channels")
  System_Ext(booking_portals, "Booking Portals", "Large OTAs like booking.com with API integration (via Channel Manager)")
  System_Ext(agencies, "Booking Agencies", "External agencies that confirm bookings via email")

  Rel(guest, website, "Books rooms via")
  Rel(guest, booking_portals, "Books rooms via")
  Rel(website, hospitality_ai, "Sends booking requests", "API")
  Rel(agencies, hospitality_ai, "Sends booking confirmations", "Email")
  Rel(channel_manager, hospitality_ai, "Syncs bookings and availability", "API")
  Rel(booking_portals, channel_manager, "Syncs bookings and availability", "API")
  Rel(assistant, hospitality_ai, "Manages bookings")
  Rel(manager, hospitality_ai, "Monitors operations")
```

---

## 4. Domain — As-Is

### Current Booking Process

> How bookings reach the hotel today, before Hospitality AI is in the picture.

```mermaid
sequenceDiagram
    actor Guest
    participant Website as Hotel Website
    participant Partner as Booking Partner
    participant Agency as Booking Agency
    participant CM as Channel Manager
    participant Agent as Hotel Support Agent
    participant ERP as ERP System

    note over Website,ERP: Assumption: Hotel Website has a direct API connection to the ERP system.<br/>Booking data is submitted automatically without manual intervention.
    note over Partner,CM: Assumption: Booking Partners integrate via the Channel Manager API.<br/>Booking and availability data is synced automatically to the ERP.

    rect rgb(235, 245, 255)
        Note over Guest,ERP: Path 1 — Website Booking
        Guest->>Website: Books room
        Website->>ERP: Sends booking via API
    end

    rect rgb(235, 255, 240)
        Note over Guest,ERP: Path 2 — Booking Partner
        Guest->>Partner: Books room
        Partner->>CM: Sends booking via API
        CM->>ERP: Syncs booking automatically
    end

    rect rgb(255, 245, 235)
        Note over Guest,ERP: Path 3 — Booking Agency
        Guest->>Agency: Requests booking
        Agency->>Agent: Sends booking confirmation via email
        Agent->>ERP: Manually enters booking data
    end

    rect rgb(250, 235, 255)
        Note over Guest,ERP: Post-Booking — Additional Services (any point after booking)
        Guest->>Agent: Sends email requesting additions (e.g. massage, flowers, dinner)
        Agent->>ERP: Manually adds services to booking
    end
```

---

## 5. Domain — MVP Email Channel (Prior Scope Doc)

> Source: `docs/domain/mvp_email_channel.md`

Automated processing of all inbound hotel emails related to bookings and booking modifications. The agent reads emails, classifies intent, interacts with the PMS, and drafts responses for the front desk — replacing fully manual data entry and reducing errors.

### Problem

Wellness and resort hotels receive ~75% of booking modification requests by email. Today, every email requires manual reading, manual PMS entry, and manual reply — creating time cost, quality risk (missed guest wishes, wrong data), and no audit trail linking emails to PMS records.

### Scope

| Email type | Sender | Description |
|---|---|---|
| Booking confirmation | Booking Agency | Agency confirms a booking on behalf of a guest |
| Booking request | Guest (direct) | Guest requests availability and a reservation |
| Modification request | Guest or Agency | Cancellation, date change, room category change, or similar |
| Special request | Guest | Add-on wishes not changing the core booking (e.g. dietary needs) |
| General inquiry | Guest | Question about the hotel, services, or existing booking |

### Flow 1 — New Booking (Request or Agency Confirmation)

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

### Flow 2 — Booking Modification

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

### Flow 3 — Special Requests and Inquiries

```mermaid
flowchart TD
    A([Special request or inquiry]) --> B{Check hotel rules and data}
    B --> |Request violates policy or not feasible| C[Draft polite rejection for front desk]
    B --> |Request matches defined exception / standard answer| D[Draft confirmation or answer for front desk]
    B --> |General inquiry| E[Draft answer based on hotel data and rules for front desk]
```

All outputs in Flow 3 are drafts — front desk reviews and sends.

---

## 6. Solution — MVP Flows

> Source: `docs/domain/solution/mvp/flows.md`

### Participants

| Participant | Description |
|---|---|
| Booking Agency | External travel agent sending booking confirmation emails |
| Email Inbox | Hotel email inbox receiving inbound traffic |
| Hospitality AI | The system — classifies, extracts, and routes |
| Mews | The hotel PMS where bookings are created |
| Front Desk | Hotel staff (Booking Assistant) receiving email handoffs |

### Flow — Inbound Email Processing

```mermaid
flowchart TD
    A([Inbound email received]) --> SYS{System healthy?}
    SYS --> |No| FAIL[Forward original email to Front Desk\n+ notice: Hospitality AI is currently unavailable]
    SYS --> |Yes| B{Classify intent}

    B --> |Booking agency confirmation| C[Extract booking data]
    B --> |Unknown / out of scope| PASS[Forward original email to Front Desk]

    C --> D{Extraction confidence}

    D --> |High confidence| E{Check availability in Mews}
    D --> |Low confidence| ASSIST[Send to Front Desk:\nsummary block + original email]

    E --> |Available| AUTO[Create booking in Mews]
    E --> |Not available| ASSIST

    AUTO --> NOTIFY[Notify Front Desk:\nbooking created confirmation]
```

### Path Summary

| Path | Trigger | System action | Front Desk receives |
|---|---|---|---|
| **1 — Automated** | Booking confirmation, high confidence, available | Create booking in Mews | Confirmation notification |
| **2 — Assisted** | Booking confirmation, low confidence or unavailable | No PMS action | Summary block + original email |
| **3 — Pass-through** | Unknown or out-of-scope intent | No PMS action | Original email only |
| **3b — System failure** | Mews or Hospitality AI unavailable | No PMS action | Original email + system unavailable notice |

### Out of Scope — MVP

The following email intents are not processed by Hospitality AI in the MVP.
All are routed via Path 3 (pass-through) to the Front Desk.

- Booking cancellations
- Booking modifications
- Special requests
- General inquiries

---

## 7. Open Questions

> Source: `docs/domain/solution/mvp/open_questions.md`

| # | Question | Raised | Status |
|---|---|---|---|
| 1 | Should a confirmation email also be sent to the booking agency after a successful auto-booking, in addition to the internal front desk notification? | 2026-04-15 | Open |
| 2 | Path 2 delivery format: one structured email (summary block + forwarded original) is the current assumption — confirm whether the summary should follow a specific template or be free-form AI-generated. | 2026-04-15 | Open |
