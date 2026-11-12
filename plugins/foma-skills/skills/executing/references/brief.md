# Implementer brief

Send as the agent prompt. Self-contained; the agent has no session context. Paste, don't link.

```
Task <Tn — title> of feature <name>. Implement only this task.

<the task block from the plan: Files, Steps, Done when>

Context: <1–2 lines on how it fits; interfaces from earlier tasks that this one uses, with exact names>
Test-first: <yes/no — tdd tasks say yes>
Check: <typecheck command> and <targeted test command> (from CLAUDE.md ## Commands)
Do not commit. Do not run the full suite.
Answer in at most 10 lines: files changed, check result (failing lines only), unrelated issues, Not checked.
```

On a retry add: `Previous attempt failed: <failing lines>. Fix the cause, not the symptom.`
