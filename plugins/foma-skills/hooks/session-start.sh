#!/bin/sh
# foma-skills SessionStart: skill router (DEC-027) + handoff pointer (DEC-019).
# POSIX sh, shell builtins only (runs in Git Bash too). Output goes into context.

cat <<'TXT'
foma-skills is active. Before you act on a task, check the foma-skills skills: if one fits the task, call it with the Skill tool first and follow it. It fits when the task matches its "Use when"; for a bug, a failing test or "why" use foma-skills:debugging; for tests-first or a regression test use foma-skills:tdd; for a code review or "ready to merge?" use foma-skills:reviewing. Questions, explanations and one-line edits need no skill.
TXT

if [ -f ".claude/.scratch/handoff.md" ]; then
  echo "A handoff note from the last session is in .claude/.scratch/handoff.md; read it before you start."
fi
exit 0
