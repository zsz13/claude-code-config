#!/bin/sh
# PreToolUse(Bash|Write|Edit|MultiEdit|NotebookEdit): ask the user before a persistent
# skill or plugin change — `skills add/update/remove`, `claude plugin install/update/...`,
# and any write into .claude/skills, .agents/skills, .codex/skills, .claude/commands or
# .claude/plugins. Discovery (`skills find`), one-off use (`skills use`) and reads are
# never asked about. Classification is in skill-install-guard.py.
# Policy: skills are searched for and used on demand; keeping one is the user's decision.
# It asks, never denies: approving the prompt lets the action run. Remove this hook from
# ~/.claude/settings.json to disable it. Fails open on any error.
input=$(cat)
case $(printf '%s' "$input" | tr '[:upper:]' '[:lower:]') in
  *skill*|*plugin*|*marketplace*|*/commands*) ;;
  *) exit 0 ;;
esac
printf '%s' "$input" | python3 "$(dirname "$0")/skill-install-guard.py" 2>/dev/null
exit 0
