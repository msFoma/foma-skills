# Setup details

## Choices (recommended first)
| Choice | Options |
|--------|---------|
| Docs home | `docs/` / `.claude/docs/` / custom |
| Decision log | `docs/decisions.md` / `docs/decisions/NNNN-*.md` / none |
| Specs and plans | `docs/specs` + `docs/plans` / none |
| Subagents | none / `implementer`, `reviewer`, `explorer` (propose only those the project signals justify, 0-4) |
| Other AI tools | none / AGENTS.md as source / sync tool (ruler, rulesync) |
| Existing CLAUDE.md | audit + marked block / leave as is |
| Optional | one-line rules block, `.gitignore` block |

Opt-in hooks are not offered in this version.

## New root CLAUDE.md
Sections in this order, drop empty ones; fill from manifests, ask for what cannot be found:
1. Purpose: one line, only if not obvious.
2. `## Commands`: only non-standard build / test / lint / run / typecheck, with a single-test form. Verify each command runs.
3. Conventions: only those that differ from defaults.
4. Claude gets this wrong: leave the heading out until there are real lines.
5. `## Where things live`: backticked paths for the chosen docs home, decisions, specs, plans (archive under `plans/archive/`), design, rules, scratch (`.scratch/`), trash (`.trash/`).
6. `## Workflow`: verifiable rules; the one-line block only if chosen.

Wrap the contract sections in the marked block, first line `<!-- foma-skills contract v1 -->`.

## Skeleton
Create only the chosen paths. Decision log entry: `| DEC-NNN | date | Decision | Alternatives | Reason | Status: accepted / superseded by DEC-MMM / rejected |`.

## Multi-tool and monorepo
- Several AI tools: write AGENTS.md as the one source; CLAUDE.md = `@AGENTS.md` plus Claude-only lines.
- Monorepo: root holds shared rules; package rules in `<package>/CLAUDE.md`; `claudeMdExcludes` only in user/local settings.

## .gitignore block (opt-in)
```
# foma-skills
CLAUDE.local.md
.claude/settings.local.json
.scratch/
.trash/
tmpclaude-*-cwd
.DS_Store
Thumbs.db
```
Never ignore the whole `.claude/`. Put the block between `# foma-skills:start` and `# foma-skills:end` comments; replace on rerun.
