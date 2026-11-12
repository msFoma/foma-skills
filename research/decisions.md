# Decisions (ADR log)

Single decision log for the project.

| ID | Date | Decision | Alternatives | Reason |
|----|------|----------|--------------|--------|
| DEC-001 | 2026-11-12 | Repository name: `foma-skills` | — | User choice |
| DEC-002 | 2026-11-12 | License: Apache-2.0 | MIT | Compatible with Apache-2.0 sources (e.g. anthropics/skills); one license for derived files, attribution via NOTICE/CREDITS |
| DEC-003 | 2026-11-12 | Audience: universal skeleton — skills must fit any user and any project | Solo devs only; teams only | User choice; drives what counts as "basic" |
| DEC-004 | 2026-11-12 | Roles: Opus orchestrates and reviews (no web search itself), Haiku `scout` searches, Sonnet `rewriter` rewrites | Single model for everything | Cost control: cheap models for bulk work, strong model for decisions |
| DEC-005 | 2026-11-12 | Decisions are logged only here, not duplicated in `docs/decisions.md` | Separate `docs/decisions.md` | `research/` ships with the repo as the open decision history |
| DEC-006 | 2026-11-12 | Session bootstrap skill is named `groundwork` | `kickoff`, `project-setup` | User choice (Q-001) |
