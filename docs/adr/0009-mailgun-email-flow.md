# ADR-0009: Mailgun-Mediated Email Flow (Inbound + Outbound)

**Status:** Superseded by [ADR-0010](0010-microsoft-graph-direct-integration.md) (2026-04-26)
**Date:** 2026-04-25
**Supersedes:** [ADR-0008](0008-mailgun-inbound-webhook.md)

## Context

ADR-0008 picked Mailgun for **inbound** email but did not describe how the full round-trip works in practice. A common misconception is that "the webhook forwards the email to a mailbox." That is the wrong direction. This ADR documents the actual flow end-to-end so the architecture is unambiguous when onboarding new hotels.

The system has no mailbox of its own. Mailgun acts as a parsing relay between SMTP (where email lives) and HTTP (where our app lives), in both directions.

## Decision

Use Mailgun as the **bidirectional SMTP↔HTTP relay** for the email channel:

```
┌────────────────────┐      email       ┌──────────────────────┐
│  Booking Agency    │ ───────────────▶ │  Hotel Outlook box   │
└────────────────────┘                  └──────────┬───────────┘
                                                   │ Outlook redirect rule
                                                   ▼
                              <hotel>@inbound.hospitalityai.com
                              (MX → mxa/mxb.mailgun.org)
                                                   │
                                                   ▼
                                       ┌──────────────────────┐
                                       │   Mailgun (parses)   │
                                       └──────────┬───────────┘
                                                  │ HTTP POST (form-encoded)
                                                  ▼
                              POST /webhook/inbound-email
                                                  │
                                                  ▼
                                       ┌──────────────────────┐
                                       │   Hospitality AI     │
                                       │ classify → extract   │
                                       │ → Mews / front desk  │
                                       └──────────┬───────────┘
                                                  │ Mailgun messages API
                                                  ▼
                                       ┌──────────────────────┐
                                       │   Mailgun (sends)    │
                                       └──────────┬───────────┘
                                                  │ SMTP
                                                  ▼
                                       ┌──────────────────────┐
                                       │  Hotel Outlook box   │
                                       │      (front desk)    │
                                       └──────────────────────┘
```

**Inbound path:**
1. Booking agency sends email to the hotel's Outlook address.
2. An Outlook **redirect** rule (preserves original `From:`) sends the mail to a per-hotel address on our Mailgun-verified domain, e.g. `ruegen@inbound.hospitalityai.com`.
3. The MX record on `inbound.hospitalityai.com` points to Mailgun (`mxa.mailgun.org`, `mxb.mailgun.org`), so the mail lands at Mailgun — there is no mailbox on our side.
4. A Mailgun **inbound route** matches the recipient and POSTs a parsed payload (`application/x-www-form-urlencoded`) to `https://<our-app>/webhook/inbound-email`.
5. `parse_mailgun_payload()` maps the payload to an `InboundEmail`; the use case takes over.

**Outbound path:**
1. `MailgunEmailSender` calls Mailgun's messages API (`POST /v3/{domain}/messages`).
2. Mailgun delivers the mail via SMTP to the hotel's front-desk Outlook inbox.
3. The front desk sees a normal email from `ai@<hotel>.com` (DKIM/SPF-signed via Mailgun).

## Consequences

- **Mental model:** Mailgun is not a mailbox and not a forwarder — it's a protocol bridge. Email never sits anywhere on our infrastructure; it is parsed and immediately POSTed.
- **Per-hotel routing key:** the recipient address (`<hotel>@inbound.hospitalityai.com`) identifies the hotel. Multi-tenant routing in the application layer keys off `recipient` from the Mailgun payload.
- **DNS surface:** one MX record on the inbound subdomain, plus DKIM + SPF on the outbound sending domain. Both are configured in Mailgun and added to DNS once per domain.
- **No IMAP, no polling, no mailbox state on our side.** Outlook is the only mailbox in the picture.
- **Outlook setup constraint:** Microsoft 365 blocks external auto-forwarding by default. The hotel's tenant admin must allow it (or whitelist the Mailgun-hosted domain). Use **Redirect**, not **Forward**, so the original `From:` header is preserved for agency identification.
- **Failure surface:** (a) Outlook redirect rule disabled silently → no email arrives; (b) Mailgun route misconfigured → 4xx/5xx visible in Mailgun logs; (c) DKIM/SPF missing on outbound → mails to front desk land in spam. Worth monitoring all three during pilot.
- **Webhook authentication:** Mailgun signs every inbound POST with `timestamp` + `token` + `signature` (HMAC-SHA256 of `timestamp+token` keyed by the Mailgun signing key). `/webhook/inbound-email` should verify this before processing. Currently not implemented — tracked as a follow-up.
- ADR-0008 is marked Superseded; the technology choice (Mailgun) is unchanged, but this ADR is the canonical description of how it is wired.
