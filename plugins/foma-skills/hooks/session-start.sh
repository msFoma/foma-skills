#!/bin/sh
# foma-skills SessionStart: skill router (DEC-027) + handoff + plan progress (DEC-019, IDEA-127).
# POSIX sh, shell builtins only (runs in Git Bash too). Output goes into context.

cat <<'TXT'
foma-skills is active. Before you act on a task, check the foma-skills skills: if one fits the task, call it with the Skill tool first and follow it. It fits when the task matches its "Use when"; for a bug, a failing test or "why" use foma-skills:debugging; for tests-first or a regression test use foma-skills:tdd; for a code review or "ready to merge?" use foma-skills:reviewing; for refactoring, cleanup or restructuring use foma-skills:refactoring; to commit or open a PR use foma-skills:committing; to record a decision or update docs use foma-skills:documenting; to plan a feature or a multi-step change use foma-skills:planning; to carry out an existing plan use foma-skills:executing; to pick a model per plan task use foma-skills:routing. For a new idea or vague feature use foma-skills:shaping; for a new look, UI or game-feel choice use foma-skills:design-interview; when the user wraps up the session use foma-skills:handoff; to clean up junk files use foma-skills:tidying; to set up or audit CLAUDE.md and docs use foma-skills:groundwork. Questions, explanations and one-line edits need no skill.
TXT

if [ -f ".claude/.scratch/handoff.md" ]; then
  read -r first < ".claude/.scratch/handoff.md"
  echo "Handoff note: .claude/.scratch/handoff.md. $first"
fi

# Active plan progress, e.g. "Plan refunds: 2/5 tasks done".
for plan in docs/plans/*/plan.md; do
  [ -f "$plan" ] || continue
  total=0; done_n=0
  while IFS= read -r line; do
    case "$line" in
      "## T"[0-9]*) total=$((total + 1)) ;;
      "Status: done"*) done_n=$((done_n + 1)) ;;
    esac
  done < "$plan"
  [ "$total" -gt 0 ] && [ "$done_n" -lt "$total" ] && d=${plan#docs/plans/}; echo "Plan ${d%/plan.md}: $done_n/$total tasks done."
done
exit 0
