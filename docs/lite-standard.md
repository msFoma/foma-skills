# Lite skill standard (v1.2 — approved, DEC-020)

How every foma-skills skill is written. The `rewriter` agent, `writing-skills` and contributors follow it; CI checks the measurable parts (§9).
Evidence IDs refer to `research/`. Graph and levels: `research/graph.md` (v1.1). Target: the Claude Code plugin `foma-skills` — the only supported install (plain-folder installs are not namespaced, FACT-034). claude.ai/API upload is out of scope for v1.

## 1. Files

```
skills/<name>/
├── SKILL.md            # core: frontmatter + body (body cap §5)
├── references/*.md     # branch details, read only on a stated condition (one level deep, FACT-013)
└── assets/             # verbatim files that are copied, never read: templates, hook scripts, agent files, gallery page
```

- Copy assets via `${CLAUDE_SKILL_DIR}/assets/…` (FACT-016); never use `${CLAUDE_PLUGIN_ROOT}` in Bash (FACT-062). Assets don't count toward the token budget.
- `scripts/` that replace prose (to save tokens) only after a before/after test (DEC-014, IDEA-097).
- No README, CHANGELOG or examples folder inside a skill.

## 2. Frontmatter

Model-invoked example:

```yaml
---
name: planning
description: >-
  Breaks a feature into ordered, verifiable tasks. Use when the user asks for a plan, a spec or design is ready to build, or a change spans several files.
license: Apache-2.0
metadata:
  level: "process"
  uses: "routing documenting"
  agents: ""
  tokens: "420"
---
```

Manual example:

```yaml
---
name: tidying
description: Finds junk in the project and removes it reversibly after your ok.
license: Apache-2.0
disable-model-invocation: true
metadata:
  level: "setup"
  uses: ""
  agents: ""
  tokens: "900"
---
```

- Keys: `name`, `description`, `license`, `metadata`, `allowed-tools` (read-only, below); `disable-model-invocation: true` for manual skills (FACT-023); `effort` only after a test shows the need (FACT-077). Never `model` (route via the Agent `model` param, FACT-076, FACT-009), `when_to_use`, `argument-hint`.
- `metadata` values are strings until nested values are verified (stage 6 / scout): `uses` and `agents` = space-separated bare names; `tokens` = number as string. Credits live in `CREDITS.md` / `NOTICE`, never in frontmatter.
- `level` is one of `setup`, `process`, `method`, `atomic`, `meta`. Allowed `uses`: process → method, atomic; method → atomic; setup, atomic, meta → none (graph levels table). Agents may be used by process and method skills.
- `allowed-tools` may list read-only tools only (Read, Grep, Glob). Never `AskUserQuestion` (NOTE-111), never Bash patterns that pre-approve side effects (NOTE-032).
- Names: bare in metadata (`routing`), namespaced in the body (`foma-skills:routing`). Agent names in the body: `foma-skills:<agent>`; whether a project copy overrides it is a stage-6 check (FACT-038).

## 3. Description

- Model-invoked: what it does, then "Use when …" with 2–4 concrete situations in the user's words (NOTE-157, NOTE-138). ≤250 chars (pack choice, §5), no XML (FACT-006).
- Scope by situation, not by caller: atomic skills say "only when the user asks for X directly" rather than naming the skills that load them (DEC-019).
- Manual: one human-facing line; it is not in context (FACT-023).
- Tone (plain vs pushy) is set by trigger tests, not by advice (NOTE-138 vs NOTE-009).

## 4. Body (order fixed, drop empty parts)

1. **Purpose** — first line, plain sentence (no heading).
2. **Uses** — `Uses: foma-skills:tdd (when writing tests), …`; agents too (NOTE-022).
3. **Steps** — numbered, imperative, each verifiable (P6). Read paths and commands from the CLAUDE.md contract; inline the default the skill uses when a line is missing (`docs/golden-structure.md` doesn't ship).
4. **Rules** — hard never/always lines with a short reason when not obvious; no capitals shouting. Text that changes behaviour (e.g. red-flag or rationalisation tables) is kept here, compressed.
5. **Branches** — "If <condition>, read `references/<x>.md`." (FACT-011, FACT-013)
6. **Report** — ≤5-line summary, last line "Not checked: …" (IDEA-044). Decision payloads — question rounds, proposals, manifests — are not the report; long lists go to `.claude/.scratch/` and are linked.
7. **Next** — name the command when the next step is a process or manual skill (those can't be called by skills).

Leave out: rationale, history, evidence, generic advice, anything the model infers from code (NOTE-067). Rationale lives in `research/`.

## 5. Caps per skill

| | Model-invoked | Manual (setup & upkeep, shaping, design-interview, writing-skills) |
|-|---------------|--------------------------------------------------------------------|
| Rules | ≤5 (`coding` ≤9, DEC-012) | ≤8 |
| Core tokens (SKILL.md body) | target 300–500, cap 800 (`coding` ≈700 approved, DEC-012) | cap 1,200 (no listing cost, rarely run, FACT-023) |
| Each reference file | ≤600 target, cap 1,000 | same |

Pack always-on (all model-invoked descriptions): ≈0.9k target, 1.2k cap.

## 6. Behaviour rules every skill follows

Apply by context: a skill writes a line only for what it does (asks, delegates, causes a side effect); that line counts toward its caps.

- **Side effect** = changing git history, settings or hooks, installing, deleting or moving files (outside `docs/plans` lifecycle), network calls. Normal working-tree edits are not. Side effects need a manual skill or an explicit confirm step; push is never automatic (NOTE-032, DEC-019).
- **`$ARGUMENTS`** is a hint, never a command: re-confirm before any side effect (NOTE-032).
- **Questions:** decision questions in rounds of ≤4 (AskUserQuestion limit, NOTE-109), recommended answer first, worded so "yes" accepts (NOTE-145); one context line before the dialog; plain-text fallback (NOTE-110..113).
- **Subagents:** model passed per call, self-contained brief, fresh context, answer ≤10 lines; never implement a delegated task yourself (NOTE-156, NOTE-183).
- **Token hygiene:** grep before read, read ranges, don't re-read; show only failing output (DEC-013).
- **Portability:** POSIX shell that also runs in Git Bash; no symlinks (NOTE-042, PROB-011).

## 7. Rewriting an outside skill

- Keep every behaviour-changing line: as Rules up to the cap, then merged lines or Steps; branch-only lines go to a reference. Drop rationale and examples. The PR lists merges.
- Original scripts: drop or summarise as steps; note it in `CREDITS.md`.
- Each rewrite PR lists the dropped behaviours and why.
- If an Apache-2.0 source ships a NOTICE, copy its text into root `NOTICE`.
- Attribution: `CREDITS.md` row with source pinned to a commit sha, license, what was taken. Apache-2.0/MIT/ISC/CC0 fine; CC-BY needs visible credit; no license → ideas only, own wording (DEC-002).

## 8. Definition of done (stage 6)

1. **Trigger set** (model-invoked only): ≥5 must-fire and ≥5 must-not-fire prompts. Must-not-fire includes the must-fire prompts of the nearest in-pack neighbour — pairs: coding/refactoring, coding/tdd, tdd/debugging, reviewing/verifying, documenting/committing, planning/executing, planning/routing — and of popular third-party packs (code-review, debug, documentation, skill-creator).
2. **Firing detection:** `claude -p --output-format stream-json --verbose` + grep for the Skill tool call (verify in stage 6).
3. **Task check:** one task with pass/fail. Interactive skills (shaping, design-interview, groundwork): a scripted-answer prompt, or a manual checklist when the dialog can't run headless (NOTE-110).
4. **Baselines:** no skill and a plain one-line instruction (IDEA-045), 3 runs each, compare pass counts; keep the skill only if it wins or ties at lower tokens (IDEA-100). A change that raises tokens needs the same proof.
5. **Cost cap:** re-run only changed skills; ≤60 runs per stage-6 session.

## 9. CI checks (static, free)

- Frontmatter key allowlist (§2); YAML parses (FACT-010); `name` = folder name; description ≤250 chars (pack choice, §5), no XML (FACT-006).
- Every file in `references/` is linked by an "If …" line; no reference links another reference.
- `metadata.uses` / `agents` targets exist; levels only point down; no cycles (IDEA-020).
- Token count = SKILL.md body chars ÷ 4, frontmatter excluded (descriptions count only in the pack total): fail above the cap (§5) or when `metadata.tokens` drifts >10%.
- Pack always-on total ≤1.2k.
- `claude plugin validate . --strict` (FACT-029).

## Template

```markdown
---
name: <name>
description: >-
  <What it does>. Use when <situation 1>, <situation 2>, or <situation 3>.
license: Apache-2.0
metadata:
  level: "<level>"
  uses: ""
  agents: ""
  tokens: "0"
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

Next: <command, if the next step is a process or manual skill>
```
