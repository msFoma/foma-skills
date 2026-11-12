# One-line rules block (opt-in)

Offer only on request or as an explicit choice. Helps weaker models (Haiku); strong models follow these without it. Put under `## Workflow` inside the marked block; the user may drop any line.

- Small change: just do it. Change only what the task needs; mention unrelated issues, don't fix them.
- Run the tests before saying done; report failures as they are.
- When debugging: reproduce the bug first, fix the root cause, add a regression test (full procedure: `/foma-skills:debugging`).
- New idea: `/foma-skills:shaping`. UI look: `/foma-skills:design-interview`. Plan exists: `/foma-skills:executing`.
- Scratch goes to `.claude/.scratch/`; never create `_old`, `_v2` or `.bak` copies, edit in place and commit before risky edits.
