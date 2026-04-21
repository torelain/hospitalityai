# ADR-0007: Use Claude Tool Use for Structured Email Extraction

**Status:** Accepted  
**Date:** 2026-04-21

## Context

The email processor extracts structured booking data from incoming emails using Claude. Two approaches were considered for communicating the required field schema to Claude:

- **Prompt-based** — describe the required fields as plain text in the system prompt; ask Claude to return a JSON object conforming to that description
- **Tool use** — define the required fields as a JSON Schema and pass it as a tool definition; instruct Claude to call the tool with extracted values

The field schema is derived from the domain model (`BookingData`), which represents what a booking confirmation semantically contains. This is independent of any downstream system — adapters map outward from `BookingData` to whatever their system needs, not the other way around. If a new integration requires a field not currently in `BookingData`, the question to ask is whether that field is a meaningful domain concept; if yes, it belongs in the domain model.

## Decision

Use **Claude's tool use API** as a structured output mechanism for email extraction, with the schema derived from the domain model.

At extraction time, the `BookingData` schema is passed to the Claude API as a tool definition. Claude is instructed to call the tool with values extracted from the email, and responds with a `tool_use` content block containing the extracted data as a typed dict.

The tool is not a real function — it is never invoked. The mechanism is used purely to obtain output that is guaranteed to conform to the schema.

## Consequences

- The extracted data shape is enforced by the API, not by prompt engineering — no free-form JSON parsing, no format instructions in the prompt
- The domain model is the single source of truth for the extraction schema — adapters depend on the domain, not the reverse
- Adding a new downstream integration requires only writing an adapter that maps from `BookingData` — the extractor does not change
- Ties extraction quality to Claude's tool use capability, which is a stable and well-supported API feature
