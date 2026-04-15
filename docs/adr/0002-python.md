# ADR-0002: Use Python as Primary Language

**Status:** Accepted  
**Date:** 2026-04-15

## Context

The MVP is AI-first — its core logic involves email classification and data extraction via Claude, plus HTTP integration with the Mews Connector API. Language choice needs to support fast iteration (hackathon context), strong AI/LLM tooling, and straightforward HTTP clients.

## Decision

Python is the primary language for all backend services.

## Consequences

- Anthropic Python SDK is first-class — prompt engineering and model calls require minimal boilerplate
- Rich ecosystem for email parsing (`imaplib`, `email`, `mailparser`) and HTTP (`httpx`, `requests`)
- Fast iteration speed suits the hackathon timeline
- Typing via `mypy` and `pydantic` keeps the codebase maintainable as it grows
- Python is not the fastest runtime — acceptable for this workload (IO-bound, not CPU-bound)
