Use for large or risky diffs. Same order as step 5 of the skill.

## What to look for, per level
1. **Correctness:** wrong result, crash, missed edge case (empty, zero, last item, rounding, time zones), a caller broken by the change, a fix applied in one caller while the shared function stays broken, errors swallowed, writes in the wrong order, no transaction.
2. **Security:** injection, secrets, weak randomness, missing checks on user input or permissions, data exposure.
3. **Scale** (state the assumed load, taken from README or deploy config): check-then-write races, the same work in every process, lists or memory that only grow, a query per item, O(n^2) on big input, per-process state that must be shared. A big slowdown is a finding; a small speed-up is nice-to-have.
4. **Compatibility:** migration strategy when the schema changes, public API and backward compatibility, docs for changed behaviour.
5. **Spec fit:** requirements missing or partial, behaviour nobody asked for, requirements that look done but are wrong. Quote the spec line. Where the spec is silent, judge by what a reasonable user of the software would expect; silence is not permission.
6. **Tests:** they check real behaviour, not mocks; risky new logic (branch, parser, money, security, data write, bug fix) has one good test; edge cases that matter. Not coverage for its own sake.
7. **Simplicity:** dead code, unused options, speculative abstraction with one implementation, a new dependency for a few lines where the stdlib does it, near-copies that must change together, one function doing unrelated jobs (split by job, never by line count). Name the existing helper's path when suggesting reuse.

## Smell baseline (judgement calls, never hard violations; the project's documented standard overrides)
Duplicated code in several hunks; feature envy (method uses another object's data more than its own); data clumps (same fields travel together); primitive obsession; the same switch repeated; shotgun surgery (one change forces edits in many files); divergent change (a file edited for unrelated reasons); speculative generality; message chains; middle man; mysterious names. Label each "possible X"; skip anything tooling enforces.

## Severity
- Must-fix: bug, security hole, data loss, breaks at the expected load, spec not met, failing check.
- Should-fix: risky code without a test, real slowness, a function mixing jobs, code that should not exist.
- Nice-to-have: small speed-ups, shorter forms, naming.
Number findings across groups so the user can say "fix 2 and 5". Fixes that delete code beat fixes that add layers.

## Large diffs
Review in passes by area and say so in the report. List behaviour you considered and set aside as outside the plan or spec, one line each with the reason, so nothing is dropped silently.
