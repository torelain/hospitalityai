# Architecture

Diagrams are written in [Mermaid](https://mermaid.js.org/) using C4 notation and render natively on GitHub.

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
