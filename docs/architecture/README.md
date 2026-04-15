# Architecture

Diagrams are written in [Mermaid](https://mermaid.js.org/) using C4 notation and render natively on GitHub.

## C1 — System Context (MVP)

> MVP scope: email channel from booking agencies only. Hotel Website, Channel Manager, Booking Portals, Hotel Guest, and Hotel Manager are out of scope for the MVP.

```mermaid
C4Context
  title System Context — Hospitality AI (MVP)

  Person(assistant, "Booking Assistant", "Receives email notifications and handles assisted or failed bookings")

  System(hospitality_ai, "Hospitality AI", "Classifies inbound booking emails, extracts booking data, and creates bookings in the PMS automatically or routes to the front desk.")

  System_Ext(agencies, "Booking Agencies", "External travel agents that send booking confirmation emails to the hotel")
  System_Ext(mews, "Mews", "Hotel PMS — where bookings are created and managed")

  Rel(agencies, hospitality_ai, "Sends booking confirmation emails", "Email")
  Rel(hospitality_ai, mews, "Creates bookings", "API")
  Rel(hospitality_ai, assistant, "Sends notification or handoff email", "Email")
```
