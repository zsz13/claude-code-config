#!/bin/sh
# PreToolUse(Bash): block state-mutating / destructive Terraform & OpenTofu commands.
# Guidance lives in ~/.claude/skills/infrastructure-quality; this is the enforcement.
# Read-only operations (init/plan/validate/fmt/show/output/graph/state list|show|pull)
# are never blocked. Remove the PreToolUse entry in ~/.claude/settings.json to disable.

input=$(cat)

# Fast path: only pay for parsing when the payload mentions terraform/tofu at all.
case "$input" in
  *terraform*|*tofu*) ;;
  *) exit 0 ;;
esac

cmd=$(printf '%s' "$input" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null)

[ -z "$cmd" ] && exit 0

# Match `terraform`/`tofu` (optionally path-qualified, with global flags like
# -chdir=DIR) followed by a destructive subcommand, anywhere in a compound command.
pattern='(^|[;&|(]|&&|\|\||[[:space:]])(/[^[:space:]]*/)?(terraform|tofu)([[:space:]]+-[^[:space:]]+)*[[:space:]]+(apply|destroy|import|taint|untaint|force-unlock|state[[:space:]]+(mv|rm|push|replace-provider))([[:space:]]|$)'

if printf '%s' "$cmd" | grep -Eq "$pattern"; then
  sub=$(printf '%s' "$cmd" | grep -Eo '(terraform|tofu)([[:space:]]+-[^[:space:]]+)*[[:space:]]+(apply|destroy|import|taint|untaint|force-unlock|state[[:space:]]+(mv|rm|push|replace-provider))' | head -1)
  cat <<JSON
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Blocked by the infrastructure-quality guard: '$sub' mutates real infrastructure or Terraform state. Run plan/validate and show the user the plan output instead. If the user has explicitly approved this exact operation, they must run it themselves, or temporarily remove the PreToolUse hook in ~/.claude/settings.json."}}
JSON
  exit 2
fi
exit 0
