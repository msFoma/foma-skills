## What and why

<!-- One skill or one topic per pull request. Link the issue or the DEC/FACT IDs your change relies on. -->

## Checklist

- [ ] `claude plugin validate . --strict` and `claude plugin validate plugins/foma-skills --strict` pass
- [ ] `python3 scripts/check_skills.py` and `python3 -m unittest scripts/test_check_skills.py scripts/test_harness.py` pass
- [ ] New or changed skill: trigger test (`python3 scripts/trigger_test.py <skill>`) and a smoke run described below
- [ ] Adapted someone else's work: row in `plugins/foma-skills/CREDITS.md` and the licence text in `plugins/foma-skills/licenses/`
- [ ] User-visible change: `README.md` **and** the Russian pages (`README.ru.md`, `docs/ru/`) updated, or noted here that the Russian side needs an update

## How I tested it

<!-- Trigger prompts that fired / did not fire, the task you ran, the result. Failures count: do not hide them. -->
