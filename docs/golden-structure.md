# Golden structure (draft v1)

How to lay out a project so an AI agent orients fast, pays as few tokens as possible, and the setup does not rot.
Every rule cites evidence IDs (`FACT-*`, `NOTE-*`, `PROB-*`) from the maintainer's private research notes, which are not part of this repository.
This document is the spec that `groundwork` implements.

## Principles

| # | Principle | Evidence |
|---|-----------|----------|
| P1 | **Pay always only for what the agent can't infer.** Non-standard conventions, gotchas, non-functional requirements. No overviews, trees, dependency lists, README duplicates. | NOTE-067, NOTE-068, FACT-050 |
| P2 | **Load lazily.** Small always-loaded layer; everything else behind lazy mechanisms. | FACT-043, FACT-044, FACT-047, FACT-011 |
| P3 | **Index, don't inline.** The root file points to deeper docs by backticked path. `@imports` are eager — use them only for content that must load anyway (e.g. AGENTS.md). | FACT-045, NOTE-071, PROB-005 |
| P4 | **Procedures are skills; area rules are path-scoped.** | FACT-049, FACT-047 |
| P5 | **Prose advises, hooks enforce.** A rule that must never be broken and can be checked mechanically becomes a hook. | FACT-051, PROB-001, PROB-002 |
| P6 | **Instructions are verifiable.** "Run `npm test` before committing", not "test your changes". | FACT-049 |
| P7 | **One home per fact, one rule per topic.** Files are concatenated, not overridden; conflicts resolve arbitrarily. | FACT-043, PROB-003 |
| P8 | **Every artifact has a home and a lifecycle.** Docs live in one place; plans get archived; decisions carry a status. | PROB-012, PROB-013, PROB-014 |
| P9 | **Shared vs personal is explicit.** Commit what the team needs; gitignore only personal files. | FACT-063, FACT-064, PROB-017, PROB-018 |
| P10 | **Trust before setup.** In an existing repo, inspect what runs automatically before changing anything. | PROB-027 |

## Loading layers

| Layer | When it loads | What lives here | Budget |
|-------|---------------|-----------------|--------|
| L0 always | Every session start | Root `CLAUDE.md`, `.claude/rules/*.md` without `paths:`, `MEMORY.md` index, skill/agent descriptions, SessionStart hook output | Root CLAUDE.md ≤200 lines (ceiling, FACT-048); target to be measured (IDEA-027). `MEMORY.md` ≤200 lines (PROB-009) |
| L1 by path | First touch of a file in that area | `<area>/CLAUDE.md`, `.claude/rules/*.md` with `paths:` | Only where an area differs |
| L2 by invocation | Skill or agent invoked | `.claude/skills/*`, `.claude/agents/*` | Skill body <5k tokens (FACT-011) |
| L3 by reading | Agent opens it | `docs/` (decisions, specs, plans), README | Unlimited; linked from L0 |

## Layout

```
project/
├── CLAUDE.md                  # L0 — non-inferable facts + index of docs
├── AGENTS.md                  # only if other AI tools are used; then CLAUDE.md = `@AGENTS.md` + Claude-only lines
├── .gitignore                 # + CLAUDE.local.md, .claude/settings.local.json (NOT the whole .claude/)
├── .claude/
│   ├── settings.json          # committed: permissions, opt-in hooks
│   ├── settings.local.json    # personal, gitignored
│   ├── rules/                 # L1 — path-scoped rules
│   ├── skills/                # L2 — project procedures
│   └── agents/                # L2 — 0–4 subagents, only when warranted
├── docs/                      # the ONLY home for generated docs (P8)
│   ├── decisions.md           # one log with status per entry (or decisions/NNNN-*.md for big projects)
│   ├── specs/<feature>.md
│   └── plans/<feature>/NN-<task>.md  → plans/archive/YYYY-MM-<feature>/ when done
└── <area>/CLAUDE.md           # L1 — only where this area has its own rules
```

No secrets anywhere under `.claude/` (PROB-029). No symlinks or junctions for instruction files (PROB-011, PROB-026).

## Root CLAUDE.md template

Sections in this order; drop empty ones.

1. **Purpose** — one line, only if not obvious from the repo.
2. **Commands** — build / test / lint / run, only non-standard ones (NOTE-070).
3. **Conventions** — only those that differ from defaults.
4. **Claude gets this wrong** — "don't X → do Y" lines learned from real mistakes (PROB-005).
5. **Where things live** — backticked paths: docs home, decisions, specs, plans, rules (P3).
6. **Workflow** — verifiable rules: how to verify, commit style, when to ask. `groundwork` offers the pack's line block (DEC-025, DEC-026), one line per skill core, e.g. "Change only what the task needs; mention unrelated issues, don't fix them.", "Run the tests before saying done; report failures as they are.", "When debugging: reproduce the bug first, fix the root cause, add a regression test." (full procedure: `/foma-skills:debugging`).

Never include: directory trees, dependency lists, architecture overviews, generic advice, README/config duplicates.
Maintainer notes and `<!-- verified YYYY-MM-DD -->` stamps go in HTML comments — free (FACT-046, PROB-004).

## Decision log entry

```
| DEC-NNN | YYYY-MM-DD | Decision | Alternatives | Reason | Status: accepted / superseded by DEC-MMM / rejected |
```

A conclusion that changes how code is written also becomes a line in CLAUDE.md or a rule; the log keeps the rationale (PROB-014).

## Enforcement (opt-in hooks)

| Hook | Event | Purpose | Evidence |
|------|-------|---------|----------|
| Re-inject critical rules (≤10 lines) | `SessionStart`, matcher `compact` | Rules survive compaction | PROB-002, FACT-057 |
| Block stray docs | `PreToolUse` on Write | No new `*.md` outside the docs home (allowlist README, CLAUDE, AGENTS, CHANGELOG) | PROB-012 |
| Block critical commands | `PreToolUse` on Bash | Hard stops the user names (e.g. force-push) | PROB-001, PROB-028 |
| Test-gaming guard | `PreToolUse` on Edit/Write | Ask when an edit adds skip/xit/@ts-ignore/eslint-disable/`type: ignore` | NOTE-214, NOTE-220 |
| Swallowed-error guard | `PreToolUse` on Edit/Write | Warn on empty catch, `except: pass`, `\|\| true` | NOTE-216, NOTE-220 |

Hooks use shell builtins only and are tested on Git Bash (NOTE-042). Off by default; `groundwork` offers them, copies the scripts into `.claude/hooks/` and registers them in `.claude/settings.json` (plugin hooks are always on, FACT-056; plugin paths change on update, FACT-062). Bash hooks block; Write/Edit hooks only warn until live-tested (FACT-105).

## Special cases

- **Multiple AI tools:** one authored file (AGENTS.md); CLAUDE.md imports it. For many tools suggest a sync tool (ruler, rulesync — MIT) rather than hand-sync (PROB-024..026).
- **Monorepo:** root CLAUDE.md holds shared rules only; package rules in `<package>/CLAUDE.md`; `claudeMdExcludes` in user/local settings, never in committed root settings (PROB-021, PROB-022).
- **Worktrees / parallel sessions:** per-session values only in local settings or env (PROB-019, PROB-020).
- **Empty repo:** interview the user for intent first, then write files (PROB-031).

## groundwork: choices it asks (default first)

| Choice | Options | Why ask |
|--------|---------|---------|
| Docs home | `docs/` · `.claude/docs/` · custom | Repo conventions differ |
| Decision log | `docs/decisions.md` · `docs/decisions/NNNN-*.md` · none | Small vs large (NOTE-073) |
| Specs and plans | `docs/specs` + `docs/plans` · none | Not every project plans in files |
| Subagents | none · 1–4 proposed from project signals | Restraint (NOTE-061) |
| Other AI tools | none · AGENTS.md as source · sync tool | PROB-024 |
| Opt-in hooks | none · pick from the enforcement table | Cost and OS risk (NOTE-042) |
| Existing CLAUDE.md | audit + append delimited block · leave as is | Never overwrite (NOTE-059) |

## groundwork audit checklist

`groundwork` owns safety, contract and structure. Rule content (stale, duplicate, contradicting rules) belongs to `learning`; junk files, stray `*.md` and leftover plans belong to `tidying` — the audit hands off to them (DEC-019).

Safety first (read-only, reported before any write):
- [ ] `.claude/settings*.json` hooks, `env` (esp. `ANTHROPIC_BASE_URL`), `enableAllProjectMcpServers`, `.mcp.json` servers — listed for the user (PROB-027).

Structure:
- [ ] Root CLAUDE.md ≤200 lines; no trees, dependency lists, overviews, duplicates (P1).
- [ ] Commands run; referenced paths exist.
- → `learning`: contradictions between root, nested CLAUDE.md, rules, skills (PROB-003, PROB-022).
- → `learning`: old `verified` stamps / rules naming removed tools (PROB-004).
- [ ] `MEMORY.md` ≤200 lines (PROB-009).
- [ ] `.gitignore` has personal files and does not ignore all of `.claude/` (PROB-017, PROB-018).
- [ ] No secrets in `.claude/`; no symlinked instruction files (PROB-029, PROB-011).
- [ ] AGENTS.md + CLAUDE.md/CLAUDE.local.md trap (PROB-025).
- → `tidying`: stray `*.md` outside the docs home; finished plans not archived (PROB-012, PROB-013).
- [ ] Decisions without status (PROB-014).

## Open points

- L0 size target — measure with an A/B in stage 6 (IDEA-027); ETH found no length effect (NOTE-069), Anthropic ties length to adherence (FACT-048).
- Passport file for other skills (IDEA-029) — format and location pending user decision.
- ETH evidence is from Python repos; generalisation assumed.
