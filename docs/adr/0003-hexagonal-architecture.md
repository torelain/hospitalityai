# ADR-0003: Use Hexagonal Architecture

**Status:** Accepted  
**Date:** 2026-04-15

## Context

The MVP integrates multiple external systems (email ingress via Postmark, Mews PMS via API, email egress). The core booking logic — intent classification, data extraction, availability checking, routing — must remain testable and portable regardless of which adapter is used on either side.

## Decision

The service follows hexagonal architecture (ports and adapters):

- **Domain core** — intent classifier, data extractor, booking orchestrator. No external dependencies.
- **Inbound port** — `EmailIngress`: triggered by an incoming parsed email payload
- **Outbound ports** — `PMSPort`: create bookings and check availability; `EmailSender`: send notifications and handoffs
- **Adapters** — `PostmarkAdapter` (inbound), `MewsAdapter` (PMS), `SMTPAdapter` or `PostmarkAdapter` (outbound email)

## Consequences

- Core logic is fully testable without live Mews or email connections
- Swapping adapters (e.g. replacing Mews with another PMS) requires no changes to domain logic
- Slightly more scaffolding upfront — acceptable given the multi-adapter nature of the system
- Clear boundaries make it easy to onboard contributors to a specific layer without understanding the whole system
