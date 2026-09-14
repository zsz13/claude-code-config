#!/bin/sh
# PreToolUse(Bash): advisory only, never blocks, never rewrites the command.
# When a command is about to dump a large deterministic output (unbounded git
# diff/log, verbose test runners, builds, docker logs, terraform plan, dependency
# listings, recursive listings, whole-tree searches), inject a one-line hint on
# how to keep the result compact WITHOUT hiding exit status, failures, errors, or
# search matches (capture helper: ~/.claude/bin/run-captured).
# Emitted at most once per session per command class. Fails open on any error.
input=$(cat)

# Fast path: only pay for parsing when a relevant token is present at all.
case "$input" in
  *git*|*test*|*pytest*|*jest*|*vitest*|*docker*|*terraform*|*tofu*|*"pip "*|*"npm "*|*pnpm*|*yarn*|*"bun "*|*cargo*|*"go "*|*mvn*|*gradle*|*"ls "*|*tree*|*find*|*"rg "*|*grep*|*build*|*install*) ;;
  *) exit 0 ;;
esac

printf '%s' "$input" | python3 "$(dirname "$0")/large-output-advisor.py" 2>/dev/null
exit 0
