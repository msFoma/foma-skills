# Audit checklist

Report each item as ok / finding with the exact fix; do not fix before the user's ok.

Contract
- `## Commands` exists; each command runs (try it, or say it was not run).
- `## Where things live` has the fixed keys; every path exists.
- Contract stamp `<!-- foma-skills contract v1 -->` present; stamp date old or missing is a finding.
- Missing lines are filled from the project, not left to defaults when they can be found.

Structure
- Root CLAUDE.md over 200 lines; trees, dependency lists, overviews, README duplicates: propose cuts as diffs.
- Same topic in root, nested CLAUDE.md, rules and skills: send to `/foma-skills:learning`, do not judge it here.
- `MEMORY.md` over 200 lines.
- `.gitignore` lacks personal files (`CLAUDE.local.md`, `.claude/settings.local.json`) or ignores all of `.claude/`.
- Secrets in `.claude/`; symlinked instruction files.
- AGENTS.md together with CLAUDE.md / CLAUDE.local.md that duplicate it.
- Decision log entries without a status.
- Missing agents from `assets/agents/`: offer them (never overwrite existing ones).
- Stray `*.md` outside the docs home, finished plans not archived: send to `/foma-skills:tidying`.

Session-start cost (L0 = loaded every session)
- Count CLAUDE.md, rules without `paths:`, MEMORY.md index, skill and agent descriptions, MCP servers, plugins, SessionStart hook output.
- Suggest: scope rules with `paths:`, move procedures to skills, docs behind backticked links (not `@imports`, which are eager), disable unused MCP servers and plugins.
