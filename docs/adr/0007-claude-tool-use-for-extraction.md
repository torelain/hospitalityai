# ADR-0007: Use Claude Tool Use for Structured Email Extraction

**Status:** Accepted  
**Date:** 2026-04-21

## Context

The email processor extracts structured booking data from incoming emails using Claude. The shape of the data that needs to be extracted depends on which downstream system the tenant has configured — each tenant has exactly one downstream integration (e.g. a PMS like Mews), and that system defines which fields are required.

Two approaches were considered for communicating the required field schema to Claude:

- **Prompt-based** — describe the required fields as plain text in the system prompt; ask Claude to return a JSON object conforming to that description
- **Tool use** — define the required fields as a JSON Schema and pass it as a tool definition; instruct Claude to call the tool with extracted values

## Decision

Use **Claude's tool use API** as a structured output mechanism for email extraction.

Each downstream integration adapter declares the fields it needs as a JSON Schema. At extraction time, this schema is passed to the Claude API as a tool definition. Claude is instructed to call the tool with values extracted from the email, and responds with a `tool_use` content block containing the extracted data as a typed dict.

The tool is not a real function — it is never invoked. The mechanism is used purely to obtain output that is guaranteed to conform to the schema.

## Consequences

- The extracted data shape is enforced by the API, not by prompt engineering — no free-form JSON parsing, no format instructions in the prompt
- Each integration adapter owns its data contract (the field schema); the extractor itself is generic and integration-agnostic
- Adding a new downstream integration requires only defining its schema and writing its adapter — the extractor does not change
- Extraction is scoped to exactly what the tenant's downstream system needs — no over-extraction of unused fields
- Ties extraction quality to Claude's tool use capability, which is a stable and well-supported API feature
