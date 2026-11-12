#!/bin/sh
# foma-skills PostToolUse(Skill): local fire counter (IDEA-128). Appends skill name, UTC time and session id
# to .scratch/fires.jsonl in the project. Nothing leaves the machine; no prompt text is read or stored.
# POSIX sh, no jq. Output is empty (nothing enters the context).

payload=""
[ -t 0 ] || read -r payload

# Value of a top-level-looking string key: field <key>
field() {
  rest=${payload#*\"$1\"}
  [ "$rest" = "$payload" ] && return
  rest=${rest#*\"}
  printf '%s' "${rest%%\"*}"
}

skill=$(field skill)
session=$(field session_id)
case "$skill" in ""|*[!A-Za-z0-9:_-]*) exit 0 ;; esac
case "$session" in *[!A-Za-z0-9_-]*) session="" ;; esac

mkdir -p .scratch 2>/dev/null || exit 0
printf '{"t":"%s","skill":"%s","session":"%s"}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$skill" "$session" >> .scratch/fires.jsonl 2>/dev/null
exit 0
