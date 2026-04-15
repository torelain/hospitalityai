You are helping document a user persona for the Hospitality AI project.

**Before doing anything else**, run `git status` and check for uncommitted changes. If there are any, stop and tell the user: "There are uncommitted changes in the repo. Please commit or stash them first so only the new persona is included in this commit." Do not proceed until the working tree is clean.

Ask the user the following questions one at a time, waiting for their answer before proceeding. Use plain, friendly language — the person you're talking to may not be technical.

1. What is the name or title of this persona? (e.g. "Booking Assistant", "Hotel Manager")
2. What is their role — what do they do day to day?
3. What are their main goals when it comes to hotel operations or bookings?
4. What frustrates them most about how things work today?
5. What tools or systems do they use regularly?
6. Can you describe a typical situation where they'd interact with a booking system?
7. Optional: Is there a short quote that captures how they think or feel? (e.g. "I just need to know if the room is available.")

Once you have all answers, do the following:

1. Create a file at `docs/domain/personas/<slug>.md` where `<slug>` is a lowercase, hyphenated version of the persona name (e.g. `booking-assistant.md`). Use this format:

```markdown
## <Persona Name>

**Role:** <role>

**Goals**
- <goal 1>
- <goal 2>

**Frustrations**
- <frustration 1>
- <frustration 2>

**Tools & Systems**
- <tool 1>
- <tool 2>

**Typical scenario**
<A short paragraph describing a realistic situation this persona faces>

> "<quote if provided>"
```

2. Add the persona to the glossary table in `README.md` if it is not already listed. Keep the table alphabetically sorted.

3. Check if `docs/domain/README.md` has a Personas section. If not, add one with a link to the new file. If yes, add a line for this persona.

4. Stage only the new and modified files, commit, and push to `main`:
   - `git add docs/domain/personas/<slug>.md docs/domain/README.md README.md`
   - Commit message: `docs: add <Persona Name> persona`
   - `git push origin main`

Confirm to the user what was created, committed, and pushed.
