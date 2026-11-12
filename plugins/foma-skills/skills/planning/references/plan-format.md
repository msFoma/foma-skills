# plan.md format

Shared by planning (writes), routing (fills `Model:`), executing (reads, updates `Status:`). Keep the headings and field names exactly.

```markdown
# Plan: <feature>

Spec: <path to docs/specs/<name>.md, or "none — <one-line goal>">
Base commit: <short sha from git rev-parse --short HEAD>
Constraints: <project-wide limits copied verbatim from the spec, one line; omit if none>

## T1 — <title: the behaviour this slice delivers>
Files: <real paths, `path:lines` for edits; mark new files "(new)">
Steps:
1. <one action with a checkable result>
2. <...>
Done when: <command to run and the output that passes, or an observable check>
Blocked by: <T-ids, or "none">
Model: <opus|sonnet|haiku> · effort <low|medium|high> — <one-line reason>
Status: todo

## T2 — <title>
...
```

Fields
- `Status:` is one of `todo`, `doing`, `done`, `blocked`. Executing changes it in place; add `— <reason>` after `blocked`.
- `Done when:` names the project's real command (from `## Commands`), scoped to the task's tests.
- `Model:` is chosen with foma-skills:routing; planning only writes the line.
- Steps name files, signatures and test names. No code bodies, no restating the spec.
- Order tasks so every `Blocked by:` points to an earlier task. A task that cannot be verified alone is merged into its neighbour.
- Extra tasks found during execution are appended as the next `T<n>`; existing ids never change.
