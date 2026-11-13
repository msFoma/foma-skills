# foma-skills

Open-source pack of basic, lightweight Claude Code skills (Apache-2.0). Repo content in English, except the user-facing docs that are also kept in Russian: `README.ru.md` and `docs/ru/` (DEC-037); change `README.md` and the Russian pages together.

## Layout
- `plugins/foma-skills/` — the plugin users install (`.claude-plugin/plugin.json`, `skills/`, `hooks/`, attribution: `CREDITS.md`, `NOTICE`, `LICENSE` copy, `licenses/`); repo root holds the marketplace (`.claude-plugin/marketplace.json`).
- `docs/` — user docs: `lite-standard.md`, `golden-structure.md`, `ru/` (Russian pages), `engineering/` (decisions `DEC-NNN` and the test ledger), `assets/` (generated art), `graph.html` (generated live skill map, served by GitHub Pages).
- `tests/` — trigger prompt sets, task fixtures, saved runs (`tests/.runs/`, ignored).
- `scripts/` — static checks, the test harness and the art generators `make_*.py`.

## Decisions
- Decisions go only to `docs/engineering/decisions.md` (`DEC-NNN`, newest last).

## Checks
- `claude plugin validate . --strict` (marketplace) and `claude plugin validate plugins/foma-skills --strict` (plugin).
- `python3 scripts/check_skills.py` — static skill checks (lite standard §9); its tests and the harness tests: `python3 -m unittest scripts/test_check_skills.py scripts/test_harness.py`.
- `python3 plugins/foma-skills/skills/tuning/scripts/fires.py [log ...] [--days N]` (the `tuning` skill's script) — free: fire counts per pack skill from `.scratch/fires.jsonl` (written by `hooks/fire-log.sh`), unfired skills listed last. Test batches end with a cost line (list-price USD, tokens) and append it to `tests/.runs/cost.jsonl`; the harness sets `FOMA_FIRE_LOG=off`.
- `python3 scripts/assets/make_charts.py` — redraws the README infographics in `docs/assets/charts/` (EN+RU SVGs, stdlib only); after skills change run `python3 scripts/assets/make_charts.py --refresh <project with the plugin installed>` first to re-capture the token numbers from `claude plugin details`.
- `python3 scripts/assets/make_header.py` — redraws the README header SVGs (stats strip, nav and language pills) in `docs/assets/header/`; `python3 scripts/assets/make_install.py` — the three install step bars (`docs/assets/install/`); `python3 scripts/assets/make_graph_preview.py` — the live-map teaser cards `docs/assets/graph-teaser.{en,ru}.svg` (headless Chrome screenshot of `docs/graph.html`, needs Chrome and macOS `sips`; rerun only when the page changes visibly: the screenshot is not byte-reproducible); `python3 scripts/assets/make_card.py` — project banner cards for the GitHub profile from `docs/assets/cards/cards.json` (one object per project; see the script's docstring); `python3 scripts/assets/make_terminal.py` — redraws the animated "first 5 minutes" terminal card (`docs/assets/charts/first-5-minutes.{en,ru}.svg`). Both are stdlib only and reuse `make_charts.py`; icons come from `make_icons.py`.
- `python3 scripts/assets/make_graph.py` — regenerates `docs/graph.html` (the live skill map, served by GitHub Pages from `/docs`) from the `SKILL.md` frontmatter and `docs/assets/charts/tokens.json`; it exits if a skill lacks EN or RU copy. Rerun it after any skill change.
- CI: `.github/workflows/validate.yml` runs both plugin validations, the unit tests and `check_skills.py` on every push/PR (CLI pinned to 2.1.322). Generators and model-backed tests are run by hand.
- Per new/changed skill (DEC-029, costs model usage): `python3 scripts/trigger_test.py <skill>` (Haiku, Sonnet re-checks misses) and a smoke run `python3 scripts/task_test.py <skill> --variants skill --models sonnet --runs 1` (a FAIL is retried twice, majority decides, `--retries 0` off; a usage-limit notice stops the batch with exit code 2 and is never scored).
- Skill vs its one line only on demand (core >800 tokens or a quality claim): `python3 scripts/task_test.py <skill> --models sonnet --runs 5`; re-grade saved runs with `--rejudge` / `--rejudge-all`.
