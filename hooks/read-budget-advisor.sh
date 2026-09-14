#!/bin/sh
# PreToolUse(Read|Bash) hint mode, PostToolUse(Read|Bash) with --record.
# Source-read budget advisor. Advisory only, never blocks, never rewrites.
# Cheap fast path: Bash payloads only reach python when the command is a plain
# file read (cat/bat/less/more/sed -n/head). Fails open.
input=$(cat)
case "$input" in
  *'"tool_name":"Read"'*|*'"tool_name": "Read"'*) ;;
  *cat*|*bat*|*less*|*more*|*"sed -n"*|*"head -n"*) ;;
  *) exit 0 ;;
esac
printf '%s' "$input" | python3 "$(dirname "$0")/read-budget-advisor.py" "$@" 2>/dev/null
exit 0
