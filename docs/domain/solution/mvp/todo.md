# Todo — Before MVP

## Tech

| # | Task | Owner | Status | Notes |
|---|---|---|---|---|
| 1 | How to host the application | Tobias | Done | Railway — app + PostgreSQL plugin |
| 2 | Simple solution design | Tobias | Done | Hexagonal — inbound email port, domain core, Mews + email outbound ports |
| 3 | Choose technologies | Tobias | Done | Python, Postmark inbound webhook, Mews Connector API |
| 4 | Define basic ADR framework | Tobias | Done | ADRs in docs/adr/ — see ADR-0002 through ADR-0006 |
| 5 | Set up Mews access for development | Tobias | Open | Email sent to Mews team — awaiting dedicated demo credentials |
| 6 | Set up Postmark account | Tobias | Open | Create account, get inbound email address |
| 7 | Configure email forwarding to Postmark | Tobias | Open | Add forwarding rule from hotel inbox to Postmark inbound address |
| 8 | Provision Railway project | Tobias | Open | Create project, add PostgreSQL plugin, set env vars |
| 9 | Get Anthropic API key | Tobias | Open | Required for Claude-based classifier and extractor |
| 10 | Set up project repo structure | Tobias | Open | Scaffold hexagonal layout: domain/, adapters/, tests/ (unit, adapters, e2e, evals) |
| 11 | Write MewsClient wrapper | Tobias | Open | Thin Python HTTP client — credentials + POST helper |
| 12 | Collect eval fixtures | Tobias | Open | 10–20 real booking agency emails with labelled expected output for LLM accuracy testing |
