#!/bin/sh
# PreToolUse(Bash): deny `git push`, `gh pr create|ready|update-branch`, `gh workflow run`,
# `gh run rerun`, `gh release create` and dispatch API calls while the content they would
# publish has no passing local validation recorded by ~/.claude/bin/local-ci. Evidence is
# keyed by tree content, so a later edit makes it stale. Classification is in
# local-ci-gate.py (it reuses skill-install-guard.py's shell scanner).
# Policy: validate locally, use remote CI as final verification. If the user explicitly
# wants to publish unvalidated work, the user runs the command (or removes this hook from
# ~/.claude/settings.json). Fails open on any error.
input=$(cat)
case "$input" in
  *push*|*gh\ *|*gh\\t*) ;;
  *) exit 0 ;;
esac
printf '%s' "$input" | python3 "$(dirname "$0")/local-ci-gate.py" 2>/dev/null
exit 0
