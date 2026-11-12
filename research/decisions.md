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
| DEC-007 | 2026-11-12 | Workspace passport = `## Where things live` section in root CLAUDE.md with fixed English keys; consumers read it, missing keys fall back to golden defaults | Separate `.claude/groundwork.json` | Already in L0 (no extra read, no extra file); user delegated the choice. Revisit if the section grows |
