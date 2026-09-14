#!/bin/sh
# PreToolUse(Bash): deny git commit/push/merge/rebase that bypass hooks (--no-verify,
# commit -n) and hook disabling via core.hooksPath. Classification is in
# block-git-no-verify.py (shlex-based, so "-n" inside a quoted message is not a flag).
# Policy: a failing hook is investigated and fixed; bypass only when the user
# explicitly asks, in which case the user runs the command (or removes this hook
# from ~/.claude/settings.json). Fails open on any error.
input=$(cat)
case "$input" in
  *git*) ;;
  *) exit 0 ;;
esac
printf '%s' "$input" | python3 "$(dirname "$0")/block-git-no-verify.py" 2>/dev/null
exit $?
