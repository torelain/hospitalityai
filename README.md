# Hospitality AI

An operating system for hotels. Centralizes hotel operations, starting with the booking process — one platform for all booking channels, guest interactions, and hotel operations.

---

## Documentation

> When you add or change anything in `docs/`, update this README at a matching level of abstraction.

| Section | Description |
|---|---|
| [Architecture](docs/architecture/README.md) | C4 diagrams — system context, containers, components |
| [Domain](docs/domain/README.md) | Business flows and rules |
| [MVP — Email Channel](docs/domain/solution/mvp_email_channel.md) | Requirements and flows for automated email booking management |
| [Event Storming — Email Channel](docs/domain/solution/event_storming_email_channel.md) | Domain events for the email-channel ingestion pipeline |
| [Extraction Rules](docs/domain/solution/extraction_rules.md) | Business rules for extracting booking data from agency emails |
| [Pain Points](docs/domain/problem/painpoints.md) | Insights aus Kundengesprächen, gegliedert nach Persona |
| [ADRs](docs/adr/README.md) | Architecture Decision Records |
| [Booking Emails](docs/booking-emails/) | Sample and real incoming booking emails from agencies |
| [Promocodes Rügen](docs/hotels/ruegen/promocodes.md) | Promocode-Gruppen und zugeteilte Raten für Santé Royale Rügen Resort |
| [Hackathon Buchungen Rügen](docs/hotels/ruegen/buchungen-hackathon.md) | 29 Beispielbuchungen für den Hackathon (Santé Royale Rügen Resort) |

---

## Glossary

| Term | Definition |
|---|---|
| **Booking Assistant** | Hotel staff who process and manage incoming bookings |
| **Booking Agency** | External travel agent that sends booking confirmations via email |
| **Booking Partner / Portal** | Large OTAs (e.g. booking.com) that integrate via the Channel Manager |
| **Channel Manager** | Third-party system that manages availability and rates across booking portals |
| **ERP System** | The hotel's core back-office system where bookings are recorded |
| **PMS (Property Management System)** | The hotel's property management software — the operational layer of the ERP where reservations are created and managed day-to-day |
| **Hotel Manager** | Oversees hotel operations and performance |
| **Hotel Guest** | Books rooms and manages their stay |
