# Test ledger: what was changed after a failure (review R-05)

IDs such as `SRC-`, `FACT-`, `CAND-`, `IDEA-` and `Q-` point to the maintainer's private research notes, which are not part of this repository; `DEC-` entries are complete here.

Rule from 2026-11-12 (standard §8.1): a failed prompt is a result. It is replaced only when it contradicts the standard, and the change is logged here. Pass counts quoted in `research/log.md` before this date are "after replacement" unless listed below.

## Trigger prompts replaced after a miss

| Skill | Replaced prompt | Result before | Replacement | Reported then | First-run result |
|-------|-----------------|---------------|-------------|---------------|------------------|
| learning | "Remember for this project: always run the targeted test before saying done." | Haiku miss, Sonnet recheck miss (treated as a one-line CLAUDE.md edit) | "You always forget to run the typecheck before saying done. Turn that into something durable for this project." | 10/10 | 9/10 |
| skill-finder | "What skills exist for writing release notes?" | Haiku 9/10, Sonnet recheck miss (answered from memory) | "Search for a skill that writes release notes and tell me which one is best to add." | 10/10 | 9/10 |
| writing-skills | "Turn the deploy procedure from our CLAUDE.md into a skill." | Haiku miss, Sonnet recheck miss (no such section in the fixture) | "Turn our release procedure (tests, version bump, changelog, commit) into a reusable skill for this project." | 10/10 | 9/10 |
| documenting | "Add the new test command to CLAUDE.md." (must fire) | Haiku miss | Moved to must-not-fire: the router and the standard say a one-line edit needs no skill (R-17) | 4/5 fire | 4/5 fire, 6/6 no-fire |

## Task checklists reworded after a fail, then re-judged

| Task | What was reworded | Why it was legitimate (or not) |
|------|-------------------|--------------------------------|
| groundwork (safety smoke) | Checklist reworded, then `--rejudge-all` (log: "PASS after checklist rewording") | The original wording was not kept; whether the change loosened the bar is not recorded — treat the PASS as unconfirmed |
| reviewing (planted bugs) | Checklist fixed, then `--rejudge-all` (log: "after checklist fix") | Same: original wording not kept, treat as unconfirmed |
| tidying | "Manifest shown before removing" → "answer lists each candidate with its tier" | The prompt pre-approved the T1 group, so a pre-removal manifest was never required; script checks passed in both runs |
| tidying-many | "count + first 10 + .scratch file" → "count, directory or glob summary, or ≈10 paths" | The intent was compactness; the model summarised by directory |
| learning-prune | Checklist accepted `permissions.deny` as a layer | The skill itself was changed to name `permissions.deny`; rerun on a fresh run, not re-judged |
| skill-finder-install | Skill step 7 changed to show the decisions line; fresh rerun | Skill change, fresh run |

## Skill changes after a failed run (2026-11-13)

| Skill | Failure | Change | Result |
|-------|---------|--------|--------|
| writing-skills (smoke) | 2 of 3 runs: the drafted release skill committed without an ask step (manual flag only) | Rule: for commit and push the manual flag is not enough, add an explicit "ask before committing" step; checklist unchanged | Fresh run PASS 1/1 (so overall 2/4 over all runs) |
| planning (held-out `models` set) | Haiku 6/8 and 5/8; Sonnet recheck 1/2 then 3/3 (question-style prompts) | Description: "a model for a plan task" → "which model fits a plan task"; prompts kept | Haiku still misses question-style prompts; Sonnet fires |

## Not independent

- The judge is Sonnet and the main model in most smokes is Sonnet.
- Every skill has one smoke run on Sonnet; none was run on Haiku or Opus except `tdd`, `debugging`, `reviewing` (DEC-026).
- Held-out trigger prompts (`tests/triggers/heldout/`, 4 per skill) were written after the sets above and are frozen from now on.
