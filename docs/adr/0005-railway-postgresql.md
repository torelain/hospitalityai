# ADR-0005: Use Railway for Hosting with PostgreSQL Plugin

**Status:** Accepted  
**Date:** 2026-04-15

## Context

The application needs a hosting platform and a relational database. Two options were considered for the database:

- **Railway PostgreSQL plugin** — provisioned directly inside the Railway project, same dashboard and billing
- **Supabase** — dedicated managed Postgres with additional features (auth, realtime, REST API)

## Decision

Use **Railway** for hosting the application with the **Railway PostgreSQL plugin** for the database. Supabase is not used.

The application is deployed as a single service on Railway. PostgreSQL is added as a plugin within the same Railway project.

## Consequences

- Everything lives in one dashboard — app, database, environment variables, logs
- No separate Supabase account or API keys to manage
- Railway Postgres is production-viable — not just a hackathon shortcut
- Supabase features (built-in auth, realtime subscriptions, auto-generated REST API) are not needed for the MVP and would add unnecessary complexity
- If Supabase features become relevant later, migration is straightforward — both use standard PostgreSQL
