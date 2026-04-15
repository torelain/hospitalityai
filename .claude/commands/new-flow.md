You are helping document a business process flow for the Hospitality AI project.

Ask the user the following questions one at a time, in plain language. The person you're talking to may not be technical.

1. What is the name of this flow? (e.g. "Phone Booking", "Check-in Process")
2. Who is involved? List the people or systems that play a role. (e.g. "Guest, Front Desk Agent, ERP System")
3. What triggers this flow? What causes it to start?
4. Walk me through the steps in order — what happens first, then next, until it's done?
5. Are there any important assumptions or constraints to note? (e.g. "The agent always checks availability manually")
6. Is this how things work **today** (as-is), or how they **should** work with Hospitality AI (to-be)?

Once you have all answers, do the following:

**1. Generate a Mermaid sequence diagram** following these conventions:
- Use `sequenceDiagram`
- Declare `actor` for human participants, `participant` for systems
- Use short aliases with descriptive labels: `participant CM as Channel Manager`
- Add a `note over` annotation at the top for any assumptions (span the relevant participants)
- Wrap the entire flow in a single `rect` block with a color from the palette below and a label:
  ```
  rect rgb(<color>)
      Note over <first>,<last>: <Flow Name>
      ... steps ...
  end
  ```
- For multi-path flows, use a separate `rect` block per path, each with its own color

**Color palette** (pick the next unused one, cycling through):
- rgb(235, 245, 255) — blue
- rgb(235, 255, 240) — green
- rgb(255, 245, 235) — orange
- rgb(250, 235, 255) — purple
- rgb(235, 255, 255) — cyan

**2. Create the file** at `docs/domain/flow_<slug>.md` where `<slug>` is a lowercase, underscored name (e.g. `flow_checkin_process.md`). Use this structure:

```markdown
## <Flow Name>

```mermaid
...
```
```

**3. Add the flow to `docs/domain/README.md`** — if a section for this type of flow (as-is / to-be) exists, add a link there. If not, create the section.

**4. Update the top-level `README.md`** Documentation table only if a new section was added to `docs/domain/README.md`.

Confirm to the user what was created and where.
