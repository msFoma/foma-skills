# Junk patterns

Match by name only; confirm with the checks in the steps. Patterns that apply to this project's stack only.

## T1: safe to remove
- OS and editor: `.DS_Store`, `._*`, `Thumbs.db`, `desktop.ini`, `*~`, `*.swp`, `*.swo`, `.#*`.
- Backup and merge: `*.bak`, `*.orig`, `*.rej`, `*.old`, `*.tmp`; a file named `<x>_old`, `<x>_backup`, `<x>_copy`, `<x>_v2`, `<x>_final`, `<x>_new`, `<x> copy.<ext>` sitting next to its original `<x>`.
- Claude temp: `tmpclaude-*-cwd`, `tmp/attachments`.
- Untracked, not-ignored caches and build output: `__pycache__/`, `*.pyc`, `dist/`, `build/` (already-ignored ones are not reported).
- Zero-byte files that are not `__init__.py`, `.gitkeep`, `.keep`; empty directories.

## T2: look first
- Untracked throwaway-looking files: names like `scratch*`, `debug*`, `tmp*`, `try*`, `test_*.py` outside the tests dir, `*.log`, `*.png`/`*.jpg` outside an assets dir, `*.md` outside the docs home (README, CLAUDE.md, AGENTS.md, CHANGELOG, LICENSE, CONTRIBUTING excepted). An untracked file with a normal source name (`promo.py`) is T3.
- Untracked files over 1 MB.
- Plans in the plans folder whose tasks are all `Status: done`: archive, never delete.
- Unused files: no reference found with `grep -rIl "<name without extension>"` over the project.

## T3: never
`.env`, `.env.*`, `*.pem`, `*.key`, `id_*`, credentials, databases and datasets, `assets/`, saves and game data, lock files, untracked source files that match no T1 pattern, `.git/`, any directory containing its own `.git`.
