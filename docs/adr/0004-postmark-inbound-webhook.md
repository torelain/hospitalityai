# ADR-0004: Use Postmark Inbound Webhook for Email Ingestion

**Status:** Superseded by [ADR-0008](0008-mailgun-inbound-webhook.md) (2026-04-25)
**Date:** 2026-04-15

## Context

The MVP needs to receive booking confirmation emails from booking agencies. Two approaches were considered:

- **IMAP polling** — periodically connect to the hotel inbox, pull unread emails, track state
- **Inbound webhook (forwarding)** — configure the hotel inbox to forward emails to an HTTP endpoint; receive a parsed JSON payload instantly

## Decision

Use **Postmark inbound webhook** as the email ingestion method.

A forwarding rule in the hotel email client routes incoming emails to a Postmark inbound address. Postmark parses the email and delivers a structured JSON payload via HTTP POST to our application endpoint the moment the email arrives.

## Consequences

- No polling loop, no IMAP connection state, no latency — emails are processed instantly
- Postmark handles MIME parsing, attachments, encoding — we receive clean structured JSON
- Our application exposes one HTTP endpoint as the inbound port (fits cleanly into hexagonal architecture)
- Postmark free tier is sufficient for hackathon and early production volume
- Adds Postmark as an external dependency — replaceable by any other inbound email service (Mailgun, SendGrid) without changing domain logic, only the adapter
- Requires a forwarding rule to be configured in the hotel inbox — one-time setup
