# foma-skills

Open-source pack of basic, lightweight Claude Code skills (Apache-2.0). Repo content in English.

## Layout
- `research/` — open research history: facts, sources, candidates, ideas, decisions (ADR), questions, log.
- `.claude/agents/` — `scout` (Haiku, web research), `rewriter` (Sonnet, skill rewrites).
- `plugins/foma-skills/` — the plugin users install (`.claude-plugin/plugin.json`, `skills/`, attribution: `CREDITS.md`, `NOTICE`, `LICENSE` copy, `licenses/`); repo root holds the marketplace (`.claude-plugin/marketplace.json`).

## Workflow
- IDs: `SRC-NNN`, `FACT-NNN`, `CAND-NNN`, `IDEA-NNN`, `DEC-NNN`, `Q-NNN`. Cross-link by ID (`CAND-007 ← SRC-003`).
- No conclusion without a source. New ideas go straight to `research/ideas.md`.
- Decisions go only to `research/decisions.md`.
- End every stage with a summary in `research/log.md`.
- Orchestrator does not search the web; delegate to `scout`.

## Checks
- `claude plugin validate . --strict` (marketplace) and `claude plugin validate plugins/foma-skills --strict` (plugin).
- `python3 scripts/check_skills.py` — static skill checks (lite standard §9); its tests: `python3 -m unittest scripts/test_check_skills.py`.
- CI: `.github/workflows/validate.yml` runs all of the above on every push/PR (CLI pinned to 2.1.322).
- Per new/changed skill (DEC-029, costs model usage): `python3 scripts/trigger_test.py <skill>` (Haiku, Sonnet re-checks misses) and a smoke run `python3 scripts/task_test.py <skill> --variants skill --models sonnet --runs 1`.
- Skill vs its one line only on demand (core >800 tokens or a quality claim): `python3 scripts/task_test.py <skill> --models sonnet --runs 5`; re-grade saved runs with `--rejudge` / `--rejudge-all`.
