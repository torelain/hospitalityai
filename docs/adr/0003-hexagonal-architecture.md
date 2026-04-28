# ADR-0003: Use Hexagonal Architecture

**Status:** Accepted  
**Date:** 2026-04-15

## Context

The MVP integrates multiple external systems (email ingress via Mailgun, Mews PMS via API, email egress). The core booking logic — intent classification, data extraction, availability checking, routing — must remain testable and portable regardless of which adapter is used on either side.

## Decision

The service follows hexagonal architecture (ports and adapters):

- **Domain core** — intent classifier, data extractor, booking orchestrator. No external dependencies.
- **Ports** — abstractions for inbound email, PMS access, and persistence. The current set evolves with the implementation; see `services/tujur/domain/ports.py` for the live list.
- **Adapters** — concrete implementations of each port, located under `services/tujur/adapters/`. Each adapter encapsulates one external provider (Microsoft Graph, Mews, Postgres, Anthropic, etc.).

This ADR documents the architectural choice. The specific port and adapter inventory is intentionally not enumerated here — it would drift the moment a new provider is added. Refer to the code for the current state.

## Consequences

- Core logic is fully testable without live external connections.
- Provider-pluggable: swapping Mews for another PMS, or Microsoft Graph for Gmail / IMAP, requires a new adapter, not domain changes. See [`docs/domain/solution/email_providers.md`](../domain/solution/email_providers.md) for the email-channel provider strategy.
- Slightly more scaffolding upfront — acceptable given the multi-adapter nature of the system.
- Clear boundaries make it easy to onboard contributors to a specific layer without understanding the whole system.
