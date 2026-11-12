#!/bin/sh
# foma-skills SessionStart: skill router (DEC-027) + fresh handoff note + plan progress (DEC-019, IDEA-127).
# POSIX sh (runs in Git Bash too). Output goes into context.

payload=""
[ -t 0 ] || read -r payload

cat <<'TXT'
foma-skills is active. Before you act on a task, if a foma-skills skill matches it, call it with the Skill tool first and follow it. Plain questions, explanations and one-line edits need no skill; questions about models for plan tasks do.
TXT

# Handoff note: only a fresh one (24 h), never after compaction (the context is still there).
case "$payload" in
  *'"source":"compact"'*|*'"source": "compact"'*) ;;
  *)
    if [ -f ".scratch/handoff.md" ] && [ -n "$(find .scratch/handoff.md -mmin -1440 2>/dev/null)" ]; then
      read -r first < ".scratch/handoff.md"
      echo "Handoff note: .scratch/handoff.md. $first"
    fi ;;
esac

# Active plan progress, e.g. "Plan refunds: 2/5 tasks done." (default path docs/plans).
for plan in docs/plans/*/plan.md; do
  [ -f "$plan" ] || continue
  total=0; done_n=0
  while IFS= read -r line; do
    case "$line" in
      "## T"[0-9]*) total=$((total + 1)) ;;
      "Status: done"*) done_n=$((done_n + 1)) ;;
    esac
  done < "$plan"
  d=${plan#docs/plans/}
  [ "$total" -gt 0 ] && [ "$done_n" -lt "$total" ] && echo "Plan ${d%/plan.md}: $done_n/$total tasks done."
done
exit 0
