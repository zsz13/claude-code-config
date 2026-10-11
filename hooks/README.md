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
| `skill-install-guard.sh` + `.py` | PreToolUse(Bash\|Write\|Edit\|MultiEdit\|NotebookEdit) | **asks** | `python3` |
| `large-output-advisor.sh` + `.py` | PreToolUse(Bash) | no | `python3` |
| `read-budget-advisor.sh` + `.py` | Pre+PostToolUse(Read\|Bash) | no | `python3` |
| `read-budget-reset.sh` | SessionStart(compact\|clear) | no | `jq` optional |
| `graphify-lazy-init.py` | PreToolUse(Grep\|Glob\|Bash) | no | `graphify`, `git` |
| `ponytail-guard.sh` | Stop, SessionEnd | no | `bash` |

## The two that block

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

Both explain themselves in the denial message and say how to remove them. They
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
(`python -c`, `node -e`), `jq` rewriting `settings.json`, or a download tool it
does not know is not caught. Every form it was tested on, ask or not, is a row
in [`scripts/test-skill-install-guard.py`](../scripts/test-skill-install-guard.py),
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
  10k LOC, skipping repos above 6000 files. Strips LLM API keys from the
  environment first; guards against recursion with an env flag, a command-name
  check and a per-repo lock; caches its decision; deletes a partial build it
  created if the build fails.
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
