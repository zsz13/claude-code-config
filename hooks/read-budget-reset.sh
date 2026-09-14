#!/bin/sh
# SessionStart(compact|clear): forget per-context advisor state (main session
# and its subagents) so reads after compaction/clear are never flagged as
# re-reads and one-per-session large-output hints can fire again. Fails open;
# works without jq.
input=$(cat)
if command -v jq >/dev/null 2>&1; then
  sid=$(printf '%s' "$input" | jq -r '.session_id // empty' 2>/dev/null)
else
  sid=$(printf '%s' "$input" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
fi
sid=$(printf '%s' "$sid" | tr -cd 'A-Za-z0-9_-' | cut -c1-40)
[ -n "$sid" ] || exit 0
rm -f "$HOME/.cache/claude-hooks/read-budget/$sid"*.json "$HOME/.cache/claude-hooks/large-output/$sid-"* 2>/dev/null
exit 0
