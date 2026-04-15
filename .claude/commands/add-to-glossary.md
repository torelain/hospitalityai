You are helping add a term to the Hospitality AI project glossary.

**Before doing anything else**, run `git status` and check for uncommitted changes. If there are any, stop and tell the user: "There are uncommitted changes in the repo. Please commit or stash them first so only the glossary update is included in this commit." Do not proceed until the working tree is clean.

If the user provided a term and definition as arguments, use those. Otherwise ask:

1. What is the term you want to add?
2. How would you describe it in one sentence — in plain language, as if explaining it to a new team member?

Then do the following:

1. Open `README.md` and find the Glossary table.
2. Add a new row with the term in bold: `| **<Term>** | <Definition> |`
3. Keep the table alphabetically sorted by term.
4. If the term already exists, ask the user if they want to update the existing definition.

4. Stage, commit, and push to `main`:
   - `git add README.md`
   - Commit message: `docs: add "<Term>" to glossary`
   - `git push origin main`

Confirm to the user what was added and show them the updated glossary row.
