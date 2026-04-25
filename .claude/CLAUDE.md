# Hospitality AI — Claude Context

## What is this project?

Hospitality AI is an operating system for hotels. It centralizes hotel operations, starting with the booking process. The goal is a single platform that manages all booking channels, guest interactions, and hotel operations.

## Current focus

Booking process — integrating all incoming booking channels into one system.

## Domain quick reference

Personas:
- **Hotel Guest** — books rooms, manages their stay
- **Booking Assistant** — hotel staff who process and manage incoming bookings
- **Hotel Manager** — oversees hotel operations and performance

Booking channels: Hotel Website (direct API), Booking Agencies (email, parsed), Booking Portals (API via Channel Manager). The Channel Manager is the only external system currently in production.

## Where things live

- **Project entry point** — top-level [`README.md`](../README.md): doc index and glossary
- **Domain conventions** (flows, event storming, personas) — [`docs/domain/README.md`](../docs/domain/README.md)
- **Architecture conventions** (C4, Mermaid, repo structure) — [`docs/architecture/README.md`](../docs/architecture/README.md)
- **Decisions** — [`docs/adr/README.md`](../docs/adr/README.md)

When you add or change anything in `docs/`, update the top-level `README.md` to reflect it at an appropriate level of abstraction. New domain or architecture terms go in the README glossary.

## Working style

- Tobi is the technical person on the team; teammates are non-technical
- Treat me as a sparring partner: challenge findings, propose alternatives, point out blind spots — don't just execute
- Document the *why* alongside the *what*

## Why this file is small

This file is loaded into context every conversation, so it stays deliberately stable: project purpose, current focus, pointers. Conventions and structure live in the docs above, where they can be edited freely. If you find yourself wanting to edit *this* file to evolve a convention, that convention probably belongs in `docs/` instead.
