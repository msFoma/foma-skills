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
| DEC-008 | 2026-11-12 | Skill list v1 approved: groundwork; processes shaping → planning → executing; methods debugging, reviewing, refactoring (candidate); atomic tdd, verifying, committing, documenting, handoff; meta writing-skills. Idea-developer skill named `shaping` | `developing-ideas`, `sparring` | User approval; short name, triggering depends on description (FACT-020) |
| DEC-009 | 2026-11-12 | Model routing: UI and visual-design tasks always go to Opus 5.5 | Route UI by task size; Fable 5.2 | User rule (clarified same day); weak support NOTE-186; Fable access on Pro unclear (FACT-080) | Status: accepted |
| DEC-010 | 2026-11-12 | Skill list v2 = v1 (DEC-008) + three skills (working names, fixed in stage 3): `skill-finder` (find, vet, install, register a skill), `routing` (assign model + effort per plan task and create subagents with them — one skill, not two), `design-interview` (question the user about the look, show 2–4 variants side by side in the browser, store in `docs/design/`; web, game and mobile screens; runs on Opus 5.5 per DEC-009) | Separate agent-builder skill | User approval; routing and agent creation are one decision, two skills would double description cost | Status: accepted |
| DEC-011 | 2026-11-12 | Plugin name `foma-skills` (commands `/foma-skills:<skill>`) | `foma` (shorter) | User choice | Status: accepted |
