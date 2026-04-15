# ADR-0001: Use Conventional Commits

**Status:** Accepted  
**Date:** 2026-04-15

## Context

As the codebase grows with multiple contributors and automated tooling, commit messages need a consistent, machine-readable format. Without a convention, changelogs are hard to generate, release notes require manual curation, and the intent of a change is often unclear from the message alone.

## Decision

All commits in this repository follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`.

## Consequences

- Commit history is human- and machine-readable
- Changelogs and release notes can be generated automatically
- Breaking changes are surfaced explicitly via `BREAKING CHANGE:` footer or `!` suffix
- Contributors must learn the convention — enforced via linting (e.g. commitlint) when tooling is set up
