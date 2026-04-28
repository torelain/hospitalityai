# Todo — Before MVP

## Tech

| # | Task | Owner | Status | Notes |
|---|---|---|---|---|
| 1 | How to host the application | Tobias | Done | Railway — app + PostgreSQL plugin |
| 2 | Simple solution design | Tobias | Done | Hexagonal — inbound email port, domain core, PMS + ledger outbound ports |
| 3 | Choose technologies | Tobias | Done | Python, Microsoft Graph for inbound + outbound (see ADR-0010), Mews Connector API for PMS (deferred) |
| 4 | Define basic ADR framework | Tobias | Done | ADRs in docs/adr/ — see ADR-0002 through ADR-0010 |
| 5 | Set up Mews access for development | Tobias | Open | Email sent to Mews team — awaiting dedicated demo credentials |
| 6 | Provision Railway project | Tobias | Open | Create project, add PostgreSQL plugin, set env vars |
| 7 | Get Anthropic API key | Tobias | Done | Set in `services/tujur/.env` |
| 8 | Set up project repo structure | Tobias | Done | Hexagonal layout in place: `domain/`, `adapters/{claude,db,graph,mews}/`, `tests/{unit,adapters,e2e,evals}` |
| 9 | Write MewsClient wrapper | Tobias | Done | Implemented in `services/tujur/adapters/mews/client.py` |
