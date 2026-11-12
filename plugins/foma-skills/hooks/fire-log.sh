#!/bin/sh
# foma-skills local usage log (IDEA-128). Appends one JSON line to .scratch/fires.jsonl in the project:
#   PostToolUse(Skill):  {"t":..., "skill":..., "session":...}      sh fire-log.sh
#   SessionStart:        {"t":..., "event":"start", "session":...}  sh fire-log.sh start   (the denominator)
# Skill name, UTC time and session id only; no prompt text; nothing leaves the machine.
# FOMA_FIRE_LOG=off disables it (the test harness sets it). POSIX sh, no jq. Prints nothing.

[ "$FOMA_FIRE_LOG" = off ] && exit 0

payload=""
[ -t 0 ] || read -r payload

# Value of the first string field named $1 in the payload.
field() {
  rest=${payload#*\"$1\"}
  [ "$rest" = "$payload" ] && return
  rest=${rest#*\"}
  printf '%s' "${rest%%\"*}"
}

session=$(field session_id)
case "$session" in *[!A-Za-z0-9_-]*) session="" ;; esac
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ "$1" = start ]; then
  line=$(printf '{"t":"%s","event":"start","session":"%s"}' "$now" "$session")
else
  skill=$(field skill)
  case "$skill" in ""|*[!A-Za-z0-9:_-]*) exit 0 ;; esac
  line=$(printf '{"t":"%s","skill":"%s","session":"%s"}' "$now" "$skill" "$session")
fi

mkdir -p .scratch 2>/dev/null || exit 0
echo "$line" >> .scratch/fires.jsonl 2>/dev/null
exit 0
