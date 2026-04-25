# Architecture

Diagrams are written in [Mermaid](https://mermaid.js.org/) using C4 notation and render natively on GitHub and GitLab.

---

## Conventions

- **Diagrams**: Mermaid + C4 model. C4 levels in use: C1 (Context), C2 (Container), C3 (Component) where needed.
- **Storage**: diagrams as Mermaid fenced code blocks in this README — no separate `.puml` files, no CI rendering step.
- **General principles**:
  - Monorepo — code and docs live together
  - ADRs for significant architecture decisions (see [`../adr/README.md`](../adr/README.md))
  - AI-first development: prompts versioned in `ai/prompts/`, agents in `ai/agents/`

### Repo structure (planned)

```
apps/           # User-facing applications (web, dashboard, api)
services/       # Backend services (booking, channel-integration, email-parser)
packages/       # Shared code (types, utilities)
ai/             # Agents, prompt templates, evaluations
infrastructure/ # Terraform, Docker
docs/
  architecture/ # Architecture diagrams (this folder)
  adr/          # Architecture Decision Records
  domain/       # Business rules, glossary, flows, event storming
.claude/
  CLAUDE.md     # Claude agent context (deliberately small — pointers to docs above)
```

---

## Mews Data Model

Key entities in the [Mews Connector API](https://docs.mews.com/connector-api) relevant to booking integration.

```mermaid
erDiagram
    Enterprise ||--o{ Service : "offers"
    Enterprise ||--o{ Resource : "has"
    Enterprise ||--o{ ResourceCategory : "defines"

    Service ||--o{ Reservation : "booked via"
    Service ||--o{ ResourceCategory : "categorizes"
    Service ||--o{ Rate : "priced by"
    Service ||--o{ RateGroup : "groups"

    ReservationGroup ||--o{ Reservation : "contains"

    Reservation }o--|| Customer : "AccountId"
    Reservation }o--o| Resource : "AssignedResourceId"
    Reservation }o--|| ResourceCategory : "RequestedResourceCategoryId"
    Reservation }o--|| Rate : "RateId"
    Reservation }o--o| Company : "TravelAgencyId / PartnerCompanyId"

    ResourceCategory ||--o{ Resource : "contains"
    Resource }o--o| Resource : "ParentResourceId"

    RateGroup ||--o{ Rate : "groups"
    Rate }o--o| Rate : "BaseRateId"

    Customer }o--o| Address : "AddressId"
    Customer }o--o| Company : "CompanyId"

    Reservation {
        string Id
        string Number
        enum State
        enum Origin
        datetime StartUtc
        datetime EndUtc
        string GroupId
        string AccountId
        string ServiceId
        string RateId
        string AssignedResourceId
        string RequestedResourceCategoryId
        string TravelAgencyId
        string ChannelNumber
        array PersonCounts
        enum Purpose
    }

    Customer {
        string Id
        string FirstName
        string LastName
        string Email
        string Phone
        string NationalityCode
        string LoyaltyCode
        string AddressId
        string CompanyId
    }

    Resource {
        string Id
        string Name
        enum State
        string ParentResourceId
        string EnterpriseId
        int FloorNumber
    }

    ResourceCategory {
        string Id
        string ServiceId
        string EnterpriseId
        enum Type
        int Capacity
        int ExtraCapacity
    }

    Rate {
        string Id
        string GroupId
        string ServiceId
        string BaseRateId
        boolean IsBaseRate
        boolean IsPublic
        enum Type
    }

    RateGroup {
        string Id
        string ServiceId
        string Name
    }

    Company {
        string Id
        string Name
    }

    Address {
        string Id
        string Line1
        string City
        string CountryCode
    }
```

## C1 — System Context (MVP)

> MVP scope: email channel from booking agencies only. Hotel Website, Channel Manager, Booking Portals, Hotel Guest, and Hotel Manager are out of scope for the MVP.

```mermaid
flowchart TD
    agencies["📧 **Booking Agencies**\nExternal travel agents"]
    hai["🤖 **Hospitality AI**\nClassifies emails, extracts booking data,\ncreates bookings or routes to front desk"]
    mews["🏨 **Mews**\nHotel PMS"]
    assistant["👤 **Booking Assistant**\nFront desk staff"]

    agencies -->|"Booking confirmation email"| hai
    hai -->|"Create booking · API"| mews
    hai -->|"Notification or handoff email"| assistant
```
