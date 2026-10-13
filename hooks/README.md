# `hooks/` — what executes on your machine

⚠️ **Read every one of these before installing them.** A hook runs arbitrary
local code on every matching tool call. This is the highest-privilege extension
point in the whole setup.

Register them in `settings.json` — see
[`config/settings.example.json`](../config/settings.example.json).

| File | Event | Blocks? | Needs |
|---|---|---|---|
| `block-destructive-iac.sh` | PreToolUse(Bash) | **yes** | `python3` |
| `block-git-no-verify.sh` + `.py` | PreToolUse(Bash) | **yes** | `python3` |
| `local-ci-gate.sh` + `.py` | PreToolUse(Bash) | **yes** | `python3`, `git`, `../bin/local-ci`, `skill-install-guard.py` |
| `local-ci-auto.sh` | SessionStart, PreToolUse(Edit\|Write\|MultiEdit\|NotebookEdit), Stop | holds a stop once | `python3`, `git`, `../bin/local-ci` |
| `skill-install-guard.sh` + `.py` | PreToolUse(Bash\|Write\|Edit\|MultiEdit\|NotebookEdit) | **asks** | `python3` |
| `large-output-advisor.sh` + `.py` | PreToolUse(Bash) | no | `python3` |
| `read-budget-advisor.sh` + `.py` | Pre+PostToolUse(Read\|Bash) | no | `python3` |
| `read-budget-reset.sh` | SessionStart(compact\|clear) | no | `jq` optional |
| `graphify-lazy-init.py` | PreToolUse(Grep\|Glob\|Bash) | no | `graphify`, `git` |
| `ponytail-guard.sh` | Stop, SessionEnd | no | `bash` |

## The three that block

**`block-destructive-iac.sh`** denies `terraform`/`tofu` `apply`, `destroy`,
`import`, `taint`, `untaint`, `force-unlock`, and `state mv|rm|push|replace-provider`
— including path-qualified binaries, global flags like `-chdir=`, and occurrences
anywhere in a compound command. Read-only operations (`init`, `plan`, `validate`,
`fmt`, `show`, `output`, `graph`, `state list|show|pull`) are never blocked.

**`block-git-no-verify.sh` + `.py`** denies `--no-verify` on
`commit`/`push`/`merge`/`rebase`/`am`/`cherry-pick`/`revert`, `commit -n` (and
bundled short flags containing `n`), `-c core.hooksPath=`, and `git config
core.hooksPath <value>`. Commands are parsed with `shlex` per shell segment, so
`-n` inside a quoted commit message is not treated as a flag. `--get`/`--unset`/
`--list` on that key are allowed.

**`local-ci-gate.sh` + `.py`** denies a command that publishes work or starts
remote CI — `git push`, `gh pr create`, `gh pr ready`, `gh pr update-branch`,
`gh workflow run`, `gh run rerun`, `gh release create`, `gh api …/dispatches` —
until every required check of the validation plan recorded by
[`bin/local-ci`](../bin/local-ci) for the content it would publish has passed. It asks `local-ci gate` about the refs the
push sends (its source refs, every branch for `--all`, `--mirror` or the
matching refspec `:`, every tag for `--tags`; default `HEAD`), in the directory
`-C`, `--git-dir`, `cd` or `pushd` names; when a `cd` sits in a subshell or is
undone by `popd`, the session's own directory is checked as well. Evidence is keyed by the
committed tree's content, so a check that passed before the last edit does not
count, a failure blocks until that same check passes, and a pass of some other
check never stands in for a required one. `git push --dry-run`,
deletion-only pushes, `gh pr ready --undo` and anything outside a git work tree
pass. It reads shell text with `skill-install-guard.py`'s
scanner (here-docs and comments are data; `sh -c`, `$(…)`, `cd`, `git -C` and
wrappers are looked through), so both files must be installed together. When
the push is allowed but some checks were recorded unsupported, it adds one line
naming them, so the report cannot drop them. If it cannot load the scanner or
find `local-ci`, it allows the command and says so in one line. For pushes the text never shows (a
script, an alias), `local-ci hook install` adds a git `pre-push` hook to a
repository that has none, enforced only in agent sessions; it never replaces a
hook or `core.hooksPath`. Rationale:
[docs/why-this-setup.md](../docs/why-this-setup.md#why-local-first-ci-and-what-is-actually-enforced).

**`local-ci-auto.sh`** is what makes local validation happen without anyone
asking for it. On `SessionStart` it records the content of the repository the
session starts in (`local-ci session start`), and before the first file-tool
edit of any other repository it records that one too (`touch`: one fingerprint,
no check). On `Stop` — the agent finishing a turn — it compares: if the session
changed a repository's content and the content has no complete validation, it
holds the stop with the instruction to run `local-ci auto`, which derives the
validation plan and runs it. A repository first seen at a stop only gets a
baseline (the session may have only read it), and content already on a remote
branch is never held. It
never runs a check itself (so it cannot recurse or slow every turn), it holds a
stop at most once per content state (the second stop for unchanged content
passes, with one line telling the user the push stays blocked) and at most
three times in a row within one user turn (content a check rewrites on every
run cannot loop), and a turn that changed nothing is never held. Claude Code labels any held stop "Stop hook error" in its
notification line; the text that follows is the hook's instruction, not a fault.
`LOCAL_CI_AUTO=0` in the environment turns it off; the push gate stays on.

All three explain themselves in the denial message and say how to remove them. They
are **not a sandbox**: they match command text, so an indirect invocation (a
shell function, a script file, a command built from a variable) will not match.
They stop the obvious mistake, not a determined bypass. Neither knows about
`pulumi`, `cdk deploy`, `kubectl delete`, `aws` CLI mutations, or `helm
uninstall` — extend them if you use those.

## The one that asks

**`skill-install-guard.sh` + `.py`** returns `permissionDecision: "ask"`: the
action waits for the user's answer in the normal permission prompt. It fires
before any persistent skill or plugin change:

- `skills add`/`update`/`remove`/`experimental_install`/`experimental_sync`,
  bare or through `npx`, `bunx`, `pnpm dlx` or `npm exec`, and `add-skill`;
- `claude plugin install`/`update`/`uninstall`/`enable`/`disable`/`init`/`prune`
  and `claude plugin marketplace add`/`remove`/`update`;
- `Write`/`Edit`/`MultiEdit`/`NotebookEdit` of a file under `.claude/skills`,
  `.agents/skills`, `.codex/skills`, `.claude/commands` or `.claude/plugins`, at
  any depth and in any letter case, in a project or in your home directory, and
  of a Claude Code `settings.json` when the new text sets `enabledPlugins` or
  `extraKnownMarketplaces`;
- a shell command that writes there: `cp`/`mv`/`ln`/`rsync`/`scp`/`degit` into
  it (including `cp -r skills ~/.claude/`), `mkdir`/`rm`/`tee`/`unzip`/`curl -o`
  on it, `tar -x`, `git clone`/`pull`, `gh repo clone`, `sed -i`, `find -delete`
  or `-exec`, a `>` redirection, or any of those after a `cd` into one. Line
  continuations, shell keywords (`for … do`, `if … then`), wrappers (`sudo`,
  `env`, `timeout`, `xargs`) and `sh -c` strings are looked through.

Text that only mentions a command is data, as it is to the shell. Examples are a
PR or issue body, a commit message, a document written by a here-doc, `echo`
text, or a comment. A here-doc fed to a shell (`bash <<EOF`, `ssh host <<EOF`) is
a script and is checked. `$(…)` or backticks outside single quotes are run, so
they are checked too, including inside double quotes and unquoted here-docs.

The prompt says what would be installed and where; for `skills add -g` that is
every detected agent's skill directory, `~/.claude/skills` included. A refused
install recreated by hand (the Write tool, `cp`, `mkdir`) is asked about again,
and the policy in `CLAUDE.md` says not to try. Never asked about:
`skills find`, `skills use` (prints a skill without installing it), `skills add
--list`, `claude plugin list`, reading any of those directories, and this
repository's own `skills/` (no leading dot). It asks rather than denies because
an install the user wants is legitimate; the rationale is in
[docs/why-this-setup.md](../docs/why-this-setup.md#why-skills-are-used-on-demand-and-installed-by-decision).
The same "not a sandbox" limit applies. It reads command text, so a path built
at run time (a variable, a glob, `$(…)`), a script file, an interpreter
(`python -c`, `node -e`, or a here-doc fed to one), `jq` rewriting
`settings.json`, or a download tool it does not know is not caught. Every form
it was tested on, ask or not, is a row
in [`scripts/test_skill_install_guard.py`](../scripts/test_skill_install_guard.py),
which `scripts/verify.sh` runs.

## The five that advise

They inject at most one line of text and never block, never rewrite a command,
and exit 0 on any error, timeout, or parse failure. Each shell wrapper has a
cheap `case` fast path so the Python classifier only runs when the payload could
possibly match.

- **`large-output-advisor`** — hints when a command is about to dump a large
  deterministic output (unbounded `git diff`/`log`, verbose test runners, builds,
  `docker logs`, `terraform plan`, dependency trees, recursive listings,
  whole-tree searches). At most once per session per command class. It never
  suggests `| head` on a search, because that hides matches.
- **`read-budget-advisor`** — two hints: a re-read of a file already read in this
  context and unchanged on disk, and a whole-file read of a large file (≥16 KB
  and ≥400 lines) where locating the target first would be cheaper. State is
  keyed by session **and** agent id, so a subagent's reads never count as the
  parent's.
- **`read-budget-reset`** — clears that state on `compact`/`clear`, so reads
  after compaction are never wrongly flagged as re-reads.
- **`graphify-lazy-init`** — builds a code knowledge graph once, lazily: only on
  a broad search, only inside a git repo, only above 50 tracked source files or
  10k LOC, skipping repos above 6000 files and any repo with a GitNexus index
  (`.gitnexus/`), which gets a one-time pointer to GitNexus instead. Strips LLM
  API keys from the environment first; guards against recursion with an env
  flag, a command-name check and a per-repo lock; caches its decision; deletes a
  partial build it created if the build fails.
- **`ponytail-guard`** — `status`/`clear`/`force` for the ponytail plugin's
  machine-global mode flag. `clear` removes only a `review` flag and leaves a
  deliberately-set `lite`/`full`/`ultra` alone. Wired to `Stop` and `SessionEnd`
  so an interrupted review still cleans up. Details:
  [docs/security.md](../docs/security.md#the-ponytail-flag-leak).

## State they write

Under `~/.cache/claude-hooks/`: `read-budget/` (per-session read records),
`large-output/` (per-session hint markers), `graphify/` (per-repo decisions), and
`captures/` (written by `bin/run-captured`, not by a hook). All are cleaned up on
an age policy by the component that writes them. Nothing is written into any
repository you work on.

Failure modes for each are tabulated in
[docs/security.md](../docs/security.md#part-3--failure-modes-and-risks).
