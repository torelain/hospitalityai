# Email Channel — Provider Strategy

Booking agencies deliver mail to whatever inbox the hotel runs — Microsoft 365, Google Workspace, generic IMAP, or a relay like Mailgun. The architecture absorbs this difference by keeping the domain (classify, extract, persist, reply) provider-agnostic and isolating provider quirks in the adapter layer.

## Why this matters

The pilot hotel runs on Microsoft 365, so the first adapter speaks Microsoft Graph. Hotel #2 may not. Without a pluggable boundary we would either lock in to one vendor or rewrite the domain every time a new mailbox provider shows up.

## Current and planned providers

| Adapter | Provider | Status |
|---|---|---|
| `GraphInboundClient` | Microsoft 365 / Outlook (Microsoft Graph) | Active |
| Gmail API + Pub/Sub | Google Workspace | Planned for the first non-M365 hotel |
| IMAP poller | Any provider with IMAP credentials | Fallback for hotels that cannot grant API access |
| Mailgun relay | SMTP redirect to a webhook | Removed (see ADR-0009, superseded by ADR-0010); kept as a documented option for hotels that block API integrations entirely |

## Adding a new provider

The inbound responsibility decomposes into the same four steps regardless of provider:

1. Authenticate against the provider (OAuth, API key, IMAP credentials).
2. Receive notification on new mail — push if the provider supports it, polling otherwise.
3. Fetch the full message.
4. Map it to the `InboundEmail` domain object.

The domain — classifier, extractor, ledger, PMS — does not change. Only the adapter does.

## Phase model and providers

The phase model in [`mvp/outlook_integration.md`](mvp/outlook_integration.md) (DB-Ledger → Folder Routing → Outbound) is specific to the Outlook-native experience. Each new provider gets its own equivalent phasing where the capabilities align: Gmail has labels instead of folders, IMAP has limited write semantics, etc. The domain pipeline runs identically across all of them.
