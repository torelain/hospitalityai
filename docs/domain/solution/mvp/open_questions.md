# Open Questions

| # | Question | Phase | Raised | Status |
|---|---|---|---|---|
| 1 | Should a confirmation email also be sent to the booking agency after a successful auto-booking, in addition to any in-folder visibility for the front desk? | Phase 3 (outbound) | 2026-04-15 | Open |
| 2 | Path 2 delivery format: when a mail is moved to `AI/Needs-Review`, what additional context (extraction summary, AI explanation) should accompany it? Currently the assumption is "folder move only, body unchanged"; confirm whether a structured summary block is needed. | Phase 2 (folder routing) | 2026-04-15 | Open |
| 3 | Worth exploring richer formats for agency replies later — HTML, deep links into Mews, threaded replies, action buttons (confirm/reject)? | Phase 3 (outbound) | 2026-04-25 | Open |
| 4 | Async webhook uses FastAPI BackgroundTasks — runs in the same process as the API. Acceptable for pilot; revisit with a real job queue (Redis + RQ, Cloud Tasks, etc.) before onboarding a second hotel or any real volume. | Ongoing | 2026-04-25 | Open |
