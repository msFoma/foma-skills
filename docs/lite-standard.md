# Lite skill standard (draft v1)

How every foma-skills skill is written. The `rewriter` agent and contributors follow it; CI checks the measurable parts.
Evidence IDs refer to `research/`. Graph and levels: `research/graph.md` (v1.1).

## 1. Files

```
skills/<name>/
├── SKILL.md            # core: frontmatter + body
└── references/*.md     # optional: branch details, read only on a stated condition
```

- `scripts/` only after a before/after test proves it helps (DEC-014).
- No README, CHANGELOG or examples folder inside a skill.

## 2. Frontmatter

```yaml
---
name: planning                      # kebab-case, ≤64 chars, = folder name
description: >-                     # ≤250 chars, see §3
  Plans work in proportion to its size. Use when a task needs more than one step, before writing code for a feature, or when the user asks for a plan.
license: Apache-2.0
disable-model-invocation: true      # only for manual skills (graph "manual")
metadata:
  level: process                    # setup | process | method | atomic | meta
  uses: [routing, documenting]      # skills it calls; CI: exist, point down, no cycles
  tokens: 420                       # measured core size; CI fails above budget
  credits:                          # only when adapted from outside
    - source: https://github.com/<owner>/<repo>/blob/<sha>/<path>
      license: MIT
      taken: "frontier rounds with recommended answers"
---
```

- Portable keys only (FACT-003); Claude Code extras (`effort`, `model`) only when a test shows the need (FACT-077, FACT-009).
- Never list `AskUserQuestion` in `allowed-tools` (NOTE-111).

## 3. Description

- Model-invoked: lead with what it does, then "Use when …" with 2–4 concrete situations in the user's words (NOTE-157, NOTE-138). Scope it so neighbours don't compete: atomic skills say "used by executing and implementer; directly only when …" (DEC-019).
- Manual: one human-facing line; it is not in context anyway (FACT-023).
- Tone (plain vs pushy) is set by trigger tests, not by advice (NOTE-138 vs NOTE-009).

## 4. Body (order fixed, drop empty parts)

1. **Purpose** — one line.
2. **Uses** — `Uses: foma-skills:tdd, foma-skills:verifying` + where each applies (NOTE-022).
3. **Steps** — numbered, imperative, each verifiable (P6). Read paths and commands from the CLAUDE.md contract; missing → golden default.
4. **Rules** — ≤5 hard lines: never / always, each with a 5-word reason when not obvious. No capitals shouting.
5. **Branches** — "If <condition>, read `references/<x>.md`." (FACT-011)
6. **Report** — fixed ≤5 lines; last line "Not checked: …" (IDEA-044, IDEA-099).
7. **Next** — hand-off line for manual skills ("next: `/foma-skills:planning`").

Leave out: rationale, history, evidence, generic advice, anything the model infers from code (NOTE-067). Rationale lives in `research/`.

## 5. Budgets

| Part | Target | Hard cap |
|------|--------|----------|
| Description | ≤200 chars | 250 |
| Core (SKILL.md body) | 300–500 tokens | 800 |
| Each reference file | ≤600 tokens | 1,000 |
| Pack always-on (all model-invoked descriptions) | ≈0.9k | 1.2k |

Measured by CI (`metadata.tokens`); a change that raises tokens must show an equal-or-better result (IDEA-100).

## 6. Behaviour rules every skill follows

- **Side effects** (write config, delete, install, push): manual skill or an explicit confirm step; push never automatic (NOTE-032, DEC-019).
- **Questions:** decision questions in rounds of ≤4, recommended answer first, worded so "yes" accepts (NOTE-145); one context line before the dialog; plain-text fallback (NOTE-110..113).
- **Subagents:** model passed per call, self-contained brief, fresh context, answer ≤10 lines; never implement a delegated task yourself (NOTE-156, NOTE-183).
- **Token hygiene:** grep before read, read ranges, don't re-read; show only failing output (DEC-013).
- **Portability:** POSIX shell that also runs in Git Bash; no symlinks (NOTE-042, PROB-011).

## 7. Attribution

- Adapted text: `metadata.credits` + a `CREDITS.md` row (source, license, what was taken). Apache-2.0/MIT/ISC/CC0 fine; CC-BY needs visible credit; no license → ideas only, own wording (DEC-002).

## 8. Definition of done (stage 6)

1. Trigger set: ≥5 prompts that must fire, ≥5 that must not (model-invoked only), incl. neighbours from popular third-party packs (DEC-019).
2. One task check with a pass/fail result.
3. Tokens per run from `claude -p --output-format json`.
4. Baselines: no skill, plain one-line instruction (IDEA-045); keep the skill only if it wins or ties at lower cost (IDEA-100).

## Template

```markdown
---
name: <name>
description: >-
  <What it does>. Use when <situation 1>, <situation 2>, or <situation 3>.
license: Apache-2.0
metadata:
  level: <level>
  uses: []
  tokens: 0
---

<One-line purpose.>

Uses: <foma-skills:x — when>.

## Steps
1. <Verifiable step.>

## Rules
- Never <x> — <reason>.

## Report
- <≤5 lines>
- Not checked: <…>
```
