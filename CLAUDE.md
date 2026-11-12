# foma-skills

Open-source pack of basic, lightweight Claude Code skills (Apache-2.0). Repo content in English.

## Layout
- `research/` — open research history: facts, sources, candidates, ideas, decisions (ADR), questions, log.
- `.claude/agents/` — `scout` (Haiku, web research), `rewriter` (Sonnet, skill rewrites).
- `skills/` — the pack (from stage 5).

## Workflow
- IDs: `SRC-NNN`, `FACT-NNN`, `CAND-NNN`, `IDEA-NNN`, `DEC-NNN`, `Q-NNN`. Cross-link by ID (`CAND-007 ← SRC-003`).
- No conclusion without a source. New ideas go straight to `research/ideas.md`.
- Decisions go only to `research/decisions.md`.
- End every stage with a summary in `research/log.md`.
- Orchestrator does not search the web; delegate to `scout`.

## Checks
None yet (no code). To be defined in stage 6 (trigger tests, Haiku runs, skill-creator evals).
