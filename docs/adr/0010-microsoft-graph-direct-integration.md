# ADR-0010: Microsoft Graph Direct Integration for Email

**Status:** Accepted
**Date:** 2026-04-26
**Supersedes:** [ADR-0009](0009-mailgun-email-flow.md)

## Context

ADR-0009 wired the email channel through Mailgun as a bidirectional SMTP↔HTTP relay. That choice optimised for being mailbox-agnostic — any provider that supports external redirect would work.

The pilot hotel runs on Microsoft 365 / Outlook and explicitly wants the integration to live inside Outlook. With a single hotel in scope, the cross-provider flexibility Mailgun bought us is hypothetical, while two of its costs are concrete:

1. **M365 blocks external auto-forwarding by default.** Lifting it requires a tenant-admin policy change — a real onboarding blocker.
2. **Front-desk experience is degraded.** Outbound mail comes from `ai@hospitalityai.com`, sits in no shared mailbox, and lives outside the hotel's normal Outlook workflow. Replies don't appear in "Sent Items"; threads are not stitched together.

A direct Microsoft Graph integration removes both costs. The capabilities we need for the MVP are inbound only:

| Capability | Endpoint | Permission |
|---|---|---|
| Read inbound mail | `GET /users/{id}/messages/{id}` | `Mail.Read` |
| Push notifications | `POST /subscriptions` on the inbox folder → webhook to our app | `Mail.Read` |

Folder routing, outbound replies and front-desk notifications are out of scope for this ADR — they are sequenced as later phases of the Outlook integration. See [`docs/domain/solution/mvp/outlook_integration.md`](../domain/solution/mvp/outlook_integration.md) for the phase model.

YAGNI applies: provider-agnosticism is not a value we need to pay for today. If a future hotel runs Google Workspace, we will add a second adapter behind the same inbound port.

## Decision

Replace the Mailgun relay with a direct **Microsoft Graph** integration for inbound email.

**Inbound path:**
1. Booking agency sends email to the hotel's normal Outlook address — no redirect, no extra DNS.
2. A Graph **subscription** on the hotel mailbox's Inbox folder POSTs a change-notification (containing only the message id) to `https://<our-app>/webhook/outlook-notification`.
3. The app calls `GET /users/{id}/messages/{messageId}` to fetch the message, classifies the intent, extracts booking data, and persists the result.

**Authentication:**
- Azure AD app registration with **Application Permissions**: `Mail.Read`.
- Admin consent granted once per hotel tenant.
- Service authenticates via client-credentials flow; tokens cached and refreshed by the adapter.

**Subscription lifecycle:**
- Graph subscriptions on mail resources have a **maximum lifetime of ~3 days** (4230 minutes). A scheduled job renews active subscriptions before expiry. On startup, the app reconciles: list current subscriptions, recreate any that are missing.
- Notifications include a `clientState` shared secret which the webhook verifies before fetching the message.

**Idempotency:**
- Change notifications can be redelivered. The persistence layer uses a unique key on `(message_id, hotel_mailbox)`, so duplicate notifications collapse into a no-op INSERT.

## Consequences

- **Onboarding flow changes.** Instead of "configure MX + Outlook redirect rule", onboarding becomes "Azure AD admin consent". One ceremony, done by the hotel's IT admin once.
- **Tenant scoping (recommended).** Application Permissions grant access to every mailbox in the tenant by default. Hotels with stricter governance can constrain access to the booking mailbox via an Exchange Online **Application Access Policy** (`New-ApplicationAccessPolicy ...`). This is recommended but not required for the trial customer.
- **Operational state we now own:** subscription IDs (per hotel), token cache, subscription renewal cron, `clientState` secrets. Mailgun had none of this.
- **Webhook validation.** Graph posts a `validationToken` query parameter on subscription creation; the endpoint must echo it back as `text/plain` with 200 within 10 seconds. Standard pattern, but not optional.
- **Provider lock-in is now explicit.** Hotel #2 on Google Workspace = new adapter behind the same inbound port. Acceptable while it remains hypothetical.
- **Mailgun is removed entirely** — no DNS records, no signing-key handling, no `parse_mailgun_payload`. The hexagonal port stays the same; only the adapter swaps.
- **DKIM/SPF/MX surface goes away.** Replaced by Azure AD app-registration management.
- **Permission scope grows in later phases** — see [`outlook_integration.md`](../domain/solution/mvp/outlook_integration.md) for the additive-consent migration to `Mail.ReadWrite` (folder routing) and `Mail.Send` (outbound replies).
- **Failure modes worth monitoring:** (a) subscription renewal job failure → silent stop of inbound; (b) admin-consent revocation → 401 storm.

## Alternatives considered

- **Stay on Mailgun (ADR-0009).** Rejected because the pilot hotel explicitly wants Outlook-native integration and the M365 auto-forward block is a real onboarding hurdle.
- **IMAP polling against the hotel mailbox.** Rejected: latency, no native folder/sent-items semantics, basic-auth deprecated in M365.
- **Delegated Permissions instead of Application.** Rejected: requires a real user account to "own" the integration, with password/MFA lifecycle attached. Application + Access Policy is cleaner for a service.
