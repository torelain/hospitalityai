# ADR-0006: Testing Setup

**Status:** Accepted  
**Date:** 2026-04-16

## Context

The application has three distinct layers (domain core, adapters, end-to-end) plus an LLM-based classification and extraction layer. Each layer has different testing requirements — the domain core is pure Python with no I/O, adapters make HTTP calls, and the AI layer requires evaluation-style testing rather than traditional assertions.

## Decision

Use **pytest** as the single test framework across all layers, with the following structure:

```
tests/
  unit/        # domain core — pure Python, no I/O, fast
  adapters/    # HTTP mocked with respx — no live network
  e2e/         # hits Mews demo API — run manually or on-demand
  evals/       # LLM accuracy benchmarks
    fixtures/  # sample booking emails (.eml or .json) with labelled expected output
```

**Layer-specific approach:**

- **Unit tests** — domain core only. No mocks needed — the core has no external dependencies by design. Test intent classification logic, data extraction, routing decisions.
- **Adapter tests** — use `respx` to intercept HTTP calls and return preset Mews API responses. Verify that adapters correctly map domain objects to API payloads and handle errors.
- **End-to-end tests** — small number of tests hitting `api.mews-demo.com` directly. Not run on every commit — executed manually before releases or major changes.
- **Evals** — 10–20 real booking agency emails with labelled expected outputs (guest name, dates, room type, etc.). Run against the LLM extractor to measure field accuracy. Used to tune prompts, not as a pass/fail gate in CI.

## Consequences

- Domain core is always testable without any live connections
- Adapter behaviour is verified without rate-limiting or network dependency
- LLM quality is tracked empirically rather than asserted deterministically
- Eval set must be maintained as prompts evolve — treat it as a first-class asset
- `respx` adds a test dependency for HTTP mocking
