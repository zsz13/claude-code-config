#!/usr/bin/env bash
# Ponytail leak guard.
#
# Ponytail's active mode lives in $CLAUDE_CONFIG_DIR/.ponytail-active (default
# ~/.claude) — one machine-global file shared by every concurrent session, not
# session state. /ponytail-review writes "review" into it, and while it is set
# the plugin's SubagentStart hook injects the ponytail persona into unrelated
# subagents in this session and any other one running.
#
# "clear" removes only a review flag; a level a human set deliberately
# (lite/full/ultra) is left alone. Run as a Stop/SessionEnd hook so cleanup
# happens even when a review fails or is interrupted.
#
# Usage: ponytail-guard.sh [status|clear|force] [-q]
set -u

FLAG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.ponytail-active"
action="${1:-clear}"
quiet=""
[ "${2:-}" = "-q" ] && quiet=1

say() { [ -n "$quiet" ] || echo "$1"; }

mode="$(cat "$FLAG" 2>/dev/null | tr -d "[:space:]")"

case "$action" in
  status)
    if [ -n "$mode" ]; then say "ponytail: ACTIVE — mode '$mode' ($FLAG)"; else say "ponytail: off (no active flag)"; fi
    ;;
  clear)
    if [ "$mode" = "review" ]; then
      rm -f "$FLAG"; say "ponytail: cleared review flag"
    elif [ -n "$mode" ]; then
      say "ponytail: left deliberate mode '$mode' in place (use 'force' to clear)"
    else
      say "ponytail: off (nothing to clear)"
    fi
    ;;
  force)
    rm -f "$FLAG"; say "ponytail: flag cleared unconditionally"
    ;;
  *)
    echo "usage: ponytail-guard.sh [status|clear|force] [-q]" >&2; exit 2
    ;;
esac
exit 0
