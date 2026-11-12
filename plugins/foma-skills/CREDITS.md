# Credits

foma-skills rewrites ideas and text from other open-source skills into its own lite standard (`docs/lite-standard.md`). Every derived skill has a row here.

Rules (DEC-002): Apache-2.0, MIT, ISC and CC0 sources may be adapted; CC-BY needs visible credit; sources without a license give ideas only, in our own wording. Sources are pinned to a commit sha. The full text of each source's license is in `licenses/<owner>-<repo>.txt`.

| Skill | Source (repo @ commit) | License | What was taken |
|-------|------------------------|---------|----------------|
| agents `implementer`, `reviewer` (was `verifying`) | [obra/superpowers](https://github.com/obra/superpowers) `skills/verification-before-completion` @ `22f0b463e7a5e579904dd6211a520321035526f7` | MIT, © 2025 Jesse Vincent | Core rules: no claim without fresh evidence, partial checks don't count, check agent reports via the diff, red-flag wording, red-green check for regression tests. Compressed and modified; evidence per change type is our own (IDEA-067) |
| tdd | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/tdd` @ `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | MIT, © 2026 Matt Pocock | Seam agreement, vertical slices, independent expected values, public-interface testing; mocking guidance in `references/mocking.md`. Reworded and compressed |
| tdd | [obra/superpowers](https://github.com/obra/superpowers) `skills/test-driven-development` @ `22f0b463e7a5e579904dd6211a520321035526f7` | MIT, © 2025 Jesse Vincent | Red/green verification steps, minimal code, delete code written before its test, real-behaviour assertions, no change detectors. Reworded and compressed |
| debugging | [mattpocock/skills](https://github.com/mattpocock/skills) `skills/engineering/diagnosing-bugs` @ `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | MIT, © 2026 Matt Pocock | Feedback loop first, shrink the repro, falsifiable hypotheses, tagged debug logs, perf baseline, regression test at an honest seam, cleanup, redaction. Script `hitl-loop.template.sh` dropped. Reworded and compressed |
| debugging | [obra/superpowers](https://github.com/obra/superpowers) `skills/systematic-debugging` @ `22f0b463e7a5e579904dd6211a520321035526f7` | MIT, © 2025 Jesse Vincent | No fix without root cause, read the full trace, one change at a time, stop after 3 failed fixes, backward tracing, condition-based waiting (`references/`). Scripts `find-polluter.sh` and the `.ts` example dropped. Reworded and compressed |
