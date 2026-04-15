# Hospitality AI — Claude Context

## What is this project?

Hospitality AI is an operating system for hotels. It centralizes hotel operations, starting with the booking process. The goal is a single platform that manages all booking channels, guest interactions, and hotel operations.

## Current focus

Booking process — integrating all incoming booking channels into one system.

## Domain

### Personas
- **Hotel Guest** — books rooms, manages their stay
- **Booking Assistant** — hotel staff who process and manage incoming bookings
- **Hotel Manager** — oversees hotel operations and performance

### Booking channels
| Channel | Integration method |
|---|---|
| Hotel Website | Direct API |
| Booking Agencies (e.g. travel agents) | Email (parsed, AI-powered) |
| Booking Portals (e.g. booking.com) | API via Channel Manager |

### External systems
- **Channel Manager** — third-party system that manages availability and rates across booking portals. Currently the only external system in production.

## Documentation conventions

- The **top-level `README.md` is the single entry point** for the project — it contains the doc index and glossary
- When adding or changing anything in `docs/`, update `README.md` to reflect it at an appropriate level of abstraction
- New terms introduced in domain or architecture docs should be added to the glossary in `README.md`

## Domain flow documentation

Domain flows live in `docs/domain/` as `flow_<name>.md` files (e.g. `flow_booking_phone.md`).

Each flow uses a Mermaid `sequenceDiagram` with these conventions:
- `actor` for humans, `participant` for systems — with short aliases and descriptive labels
- `note over` at the top for assumptions, spanning the relevant participants
- Each logical path wrapped in a `rect` block with a label: `Note over <first>,<last>: <Path Name>`
- Colors cycle through: `rgb(235, 245, 255)` → `rgb(235, 255, 240)` → `rgb(255, 245, 235)` → `rgb(250, 235, 255)` → `rgb(235, 255, 255)`

Use the `/new-flow` command to create a new flow — it guides you through the process and handles formatting automatically.

## Personas

Personas live in `docs/domain/personas/` as `<slug>.md` files.

Use the `/new-persona` command to create a new persona. Completed personas should be linked from `docs/domain/README.md`.

## Architecture documentation

- We use **Mermaid + C4 model** for all architecture diagrams
- Diagrams live in `docs/architecture/README.md` as Mermaid fenced code blocks
- They render natively on GitHub — no CI or build step needed
- C4 levels in use: C1 (Context), C2 (Container), C3 (Component) where needed

## Repo structure (planned)

```
apps/          # User-facing applications (web, dashboard, api)
services/      # Backend services (booking, channel-integration, email-parser)
packages/      # Shared code (types, utilities)
ai/            # Agents, prompt templates, evaluations
infrastructure/ # Terraform, Docker
docs/
  architecture/ # PlantUML C4 diagrams
  adr/          # Architecture Decision Records
  domain/       # Business rules, glossary
.claude/
  CLAUDE.md     # This file
```

## Conventions

- Monorepo — code and docs live together
- Architecture diagrams: PlantUML + C4, stored as `.puml`, rendered to `.svg` via CI
- ADRs for significant architecture decisions (see `docs/adr/`)
- AI-first development: prompts are versioned in `ai/prompts/`, agents in `ai/agents/`
