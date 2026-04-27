# ADR-0008: Use Mailgun Inbound Webhook for Email Ingestion

**Status:** Superseded by [ADR-0009](0009-mailgun-email-flow.md) (2026-04-25)
**Date:** 2026-04-25
**Supersedes:** [ADR-0004](0004-postmark-inbound-webhook.md)

## Context

ADR-0004 picked Postmark for email ingestion. Working on real-hotel onboarding surfaced a cost concern: Postmark's free tier is 100 emails/month total (inbound + outbound combined), which is exhausted by a single hotel within days. The next tier is $15/month per account.

Mailgun was reconsidered:

- Free tier: 100 emails/day (~3000/month) — sufficient for piloting one or more hotels at no cost
- Same architectural shape: inbound webhook receives parsed payload via HTTP POST
- Custom domain support is equivalent (MX record on a subdomain)
- The hexagonal split means the swap is one inbound adapter file, one outbound adapter file, and DNS — no domain logic changes

Postmark's deliverability and parsed-payload quality remain marginally better, but at MVP scale the difference does not justify the cost barrier during pilot onboarding.

## Decision

Use **Mailgun inbound routes** as the email ingestion method.

A Mailgun route matches incoming mail (e.g. by recipient address on our custom domain) and forwards a parsed payload to our HTTP endpoint. A forwarding rule in the hotel mailbox redirects incoming mail to that Mailgun-managed address.

Outbound (front-desk notifications and pass-through forwards) also moves to Mailgun's messages API.

## Consequences

- Free tier covers pilot volume — no expense conversation needed for hotel #1
- Mailgun posts inbound mail as **`application/x-www-form-urlencoded`**, not JSON. The webhook handler at `/webhook/inbound-email` must accept form data; the parser changes accordingly.
- Mailgun's parsed payload is slightly less polished than Postmark's (e.g. quoted-reply stripping is rougher). Acceptable for MVP; revisit if extraction quality regresses.
- Custom inbound domain (`inbound.hospitalityai.com`) is set up via MX record pointing to `mxa.mailgun.org` / `mxb.mailgun.org`. Per-hotel forwarding addresses (`<hotel>@inbound.hospitalityai.com`) become the routing key.
- Webhook authentication uses Mailgun's HMAC signature (timestamp + token + signature) rather than basic auth.
- Outbound from `noreply@hospitalityai.com` (or per-hotel domain) requires DKIM + SPF DNS records added to Mailgun's verified domain.
- Postmark adapter and `POSTMARK_API_TOKEN` env var are removed. ADR-0004 is marked Superseded.
- Swap can be reversed by reintroducing the Postmark adapter; both implement the same `EmailSenderPort` and a payload-parsing function.
