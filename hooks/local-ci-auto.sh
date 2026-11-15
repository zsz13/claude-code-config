#!/bin/sh
# SessionStart / Stop: make local validation automatic. `start` records the content each
# repository has when the session begins; `stop` blocks the end of a turn once per content state
# when the session changed a repository and that content has no complete local validation, with
# the instruction to run `~/.claude/bin/local-ci auto` (which derives and runs the validation plan:
# the repository's own checks, then the affected GitHub Actions jobs under act). The hook never runs
# a check itself, so it cannot recurse, and a stop it already blocked for the same content passes.
# Logic is `local-ci session` (../bin/local-ci). Disable per session with LOCAL_CI_AUTO=0; the
# local-ci-gate push guard stays on either way. Fails open on any error.
lc="${LOCAL_CI_BIN:-$(dirname "$0")/../bin/local-ci}"
[ -f "$lc" ] || exit 0
python3 "$lc" session "${1:-stop}" 2>/dev/null
exit 0
