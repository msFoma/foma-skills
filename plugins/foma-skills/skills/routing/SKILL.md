---
name: routing
description: >-
  Assigns a model and effort to each task in a plan. Use when a plan's tasks need a model or effort, or the user asks which model should do a task. Not for writing plans or doing the tasks.
license: Apache-2.0
metadata:
  level: "method"
  uses: ""
  agents: ""
  tokens: "352"
---

Choose model and effort for each task in `docs/plans/<feature>/plan.md` and write its `Model:` line with a one-line reason.

## Steps
1. Read the plan and the project CLAUDE.md. A stated routing preference or model limit (e.g. "no Opus", plan limits) overrides the defaults below.
2. Per task, pick the model by the nature of the work:
   - Opus: complex or non-obvious code, architecture, cross-module changes, security, judgment calls, and all UI or visual design work.
   - Sonnet: routine code from a clear plan.
   - Haiku: search, summaries, mechanical edits (renames, formatting, boilerplate), and code only when tests already pin the behaviour.
3. Pick effort: low for mechanical, medium by default, high for hard reasoning.
4. Write `Model: <model> · effort <level> — <reason>` under each task, replacing any existing line.
5. Show the assignments and apply the user's edits. Three or more tasks: a compact table (task, model, effort, reason). One or two tasks: a single line, no table.

## Rules
- Unsure between two models: pick the stronger.
- Routing applies to delegated agent calls only; never switch the main session's model mid-session (breaks the prompt cache).
- Edit only `Model:` lines in the plan; never write config or agent files.
- Judge the task's nature, not its size: a short security fix is Opus.

## Report
- Assignments (table or line) and the plan path.
- Not checked: <…>
