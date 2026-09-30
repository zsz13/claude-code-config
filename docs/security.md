# Security, privacy, and failure modes

Three separate topics: what was deliberately left out of this repository, the
security properties of the configuration itself, and how each component fails.

---

## Part 1 — What was excluded from this repository, and why

This repository was assembled by auditing a live installation and classifying
every item. It is **not** a copy of `~/.claude`.

### Never published — private or stateful

| Source | Why |
|---|---|
| `~/.claude/projects/**` | Conversation transcripts (JSONL). Contain full source code, credentials that appeared in output, and private project detail. |
| `~/.claude/projects/**/memory/*.md` | Per-project memory notes — private architecture, vendor details, business logic. Used as a *source* for the reasoning in these docs; never copied. |
| `~/.claude/history.jsonl` | Prompt history. |
| `~/.claude/sessions/`, `session-env/`, `shell-snapshots/`, `paste-cache/`, `file-history/` | Live session state, pasted content, file snapshots. |
| `~/.claude/telemetry/`, `cache/`, `downloads/` | Generated, machine-local. |
| `~/.claude/backups/`, `*.backup-*`, `.last-*` | Point-in-time copies of the above. |
| `~/.claude.json` | Per-project harness state, including project paths, and user- and local-scope MCP servers, with any API key in their headers. |
| `~/.claude/.ponytail-active` | Live mode flag. Publishing it would ship a mode. |
| `~/.claude/plugins/` (caches, `installed_plugins.json`, `known_marketplaces.json`) | Third-party plugin code plus absolute install paths and commit SHAs. Plugins are *named* in `config/settings.example.json` and installed by their own marketplace. |
| `~/.codex/auth.json` | **Credentials.** Never read, never copied. |
| `~/.codex/*.sqlite*` (`logs_`, `state_`, `thread_history_`, `memories_`, `goals_`, `queue_`) | Databases containing conversation history, memories and logs. |
| `~/.codex/.codex-global-state.json`, `installation_id`, `session_index.jsonl`, `sessions/`, `attachments/`, `cache/`, `models_cache.json` | Machine identifiers and live state. |
| `~/.codex/rules/default.rules` | A machine-specific command allowlist referencing absolute bootstrap paths under `/private/tmp`. Useless elsewhere and a bad pattern to copy. |
| SSH keys, GitHub tokens, `.env` files | Never read. `gh auth status` output was redacted before it was ever displayed. |

### Never published — third-party code under a restrictive licence

| Source | Why |
|---|---|
| `~/.claude/hooks/gitnexus/**` (5 files) | Vendored hook code from a tool licensed **PolyForm Noncommercial 1.0.0**. Redistributing it from an MIT repository would be a licence violation. It also contained the only hard-coded absolute machine path found in the whole audit. |
| `~/.claude/skills/gitnexus-*` (8 skills) | Same tool, same licence. Installed by the tool's own `setup` command; not ours to redistribute. |
| `~/.codex/hooks.json` + `~/.codex/hooks/` | Contained only that tool's hooks. Excluded for the same reason. |
| `~/.claude/plugins/cache/**` | Third-party plugin source (Superpowers, Ponytail, official plugins). Install them from their own marketplaces. |

The corresponding settings entries were removed from
`config/settings.example.json` too, so the published configuration does not
reference files it does not ship.

### Published as sanitized templates

| Source | Published as | What changed |
|---|---|---|
| `~/.claude/settings.json` | `config/settings.example.json` | Absolute `/Users/<name>/` paths → `$HOME`; third-party hook entries and the associated env var removed. |
| `~/.config/ponytail/config.json` | `config/ponytail-config.example.json` | Unchanged (it is one key), published as a template because the value is the *policy*. |
| `~/.codex/config.toml` | `config/codex/config.example.toml` | **Heavily reduced.** Removed: bundled-plugin registrations, MCP server commands with absolute app paths, desktop UI preferences, a local marketplace path, and a per-project trust entry naming a private repository. Kept: model, reasoning effort, approval policy, sandbox mode, output token limit, agent concurrency, network policy. |
| `~/.claude/CLAUDE.md` | `examples/CLAUDE.example.md` | Unchanged — audited and found to contain only `~`-relative paths. |
| `<code-dir>/CLAUDE.md` | `examples/CLAUDE.directory.example.md` | Unchanged — same audit result. `~/github` remains as the directory name; it is a placeholder for wherever you keep code. |
| `~/.codex/AGENTS.md` | `examples/codex-AGENTS.example.md` | Unchanged — audited, no machine-specific content. |

### Published as-is

All seven hooks, `bin/run-captured`, seven judge agents, seven path-scoped
rules, ten skills, and seven Codex agent definitions. Every one was scanned for
absolute paths, usernames, email addresses, hostnames, tokens and project names.
They use `~`-relative paths throughout and contain none of those.

### Placeholders used

`$HOME`, `~/github`, `YOUR_USERNAME`, `YOUR_REPOSITORY`, `YOUR_API_KEY`.

---

## Part 2 — Security properties of the configuration

### The two deny-hooks

`block-destructive-iac.sh` and `block-git-no-verify.sh`/`.py` are the only hooks
that block anything. (The one other block is `permissions.deny` in
`settings.json`, covered under trust boundaries below.) Both hooks are narrow by
design:

- **IaC guard** denies `terraform`/`tofu` `apply`, `destroy`, `import`, `taint`,
  `untaint`, `force-unlock`, and `state mv|rm|push|replace-provider` — including
  path-qualified binaries, global flags like `-chdir=`, and occurrences anywhere
  in a compound command. Read-only operations (`init`, `plan`, `validate`,
  `fmt`, `show`, `output`, `graph`, `state list|show|pull`) are **never**
  blocked.
- **No-verify guard** denies hook bypasses on `commit`/`push`/`merge`/`rebase`/
  `am`/`cherry-pick`/`revert`, plus `-c core.hooksPath=` and setting
  `core.hooksPath`. `--get`/`--unset`/`--list` on that key are allowed.

Both say, in the denial message, what they are and how to remove them. A guard
you cannot identify or disable is a trap, not a safety feature.

**Known limits, stated honestly:**

- They are **not a sandbox.** They match command text. A sufficiently indirect
  invocation (a shell function, a script file, a wrapper that reads the command
  from a variable) will not match. They exist to stop the obvious mistake, not a
  determined bypass.
- The IaC guard does not know about `pulumi`, `cdk deploy`, `kubectl delete`,
  `aws` CLI mutations, or `helm uninstall`. Extend it if you use those.
- The no-verify guard fails **open** on an unparseable command.

### Secrets handling

- Credentials never enter prompts, logs, indexes, or delegated packets.
- Terraform state, `state pull` and `show` output contain secrets and must never
  be pasted into context, a review packet, or a subagent prompt
  (`rules/infrastructure.md`).
- The graph bootstrap **strips LLM API keys from the environment** before
  invoking the graph tool, so a build cannot make a paid API call even if the
  tool would otherwise try.
- Review packets are explicitly required to have secrets stripped from diffs,
  logs and config before dispatch (`skills/adversarial-jury/packet-template.md`).
- The security judge is told never to retrieve a secret value as proof, and
  never to write a working exploit.

### Tool output is data, not instructions

Repository text, web pages, package metadata and tool output are treated as
evidence, never as instructions. Every judge agent is told this explicitly in
its own prompt, because a judge reads attacker-influenceable content (diffs,
logs) with an instruction-shaped mind.

### The Ponytail flag leak

The one known defect in the upstream stack, reproduced directly.

**What it is.** The plugin's active mode lives in a single file under the Claude
config directory. It is machine-global and shared by every concurrent session.
Typing `/ponytail-review` writes `review` into it, and while set, the plugin's
subagent hook injects the "delete code" persona into subagents — *including
reviewers whose purpose is the opposite lens*, in that session **and any other
session running at the same time**.

**Why it matters.** A simplification persona reaching a security or correctness
reviewer inverts what that reviewer is for. Because the file is shared, a review
started in one terminal can quietly alter a judge in another. Nothing fails
loudly; the effect is a bias.

**Three independent containment layers.** Do not remove one assuming another
covers it:

1. **`PONYTAIL_SUBAGENT_MATCHER`** in settings — a never-matching sentinel
   (`^ponytail-subagents-disabled$`) that stops the ruleset reaching any
   subagent regardless of flag state. ⚠️ An *invalid* regex fails open and
   injects, so any replacement must be a valid regex that matches nothing.
2. **`hooks/ponytail-guard.sh`** wired to `Stop` and `SessionEnd`, so an
   interrupted or failed review still cleans up. `clear` removes only a `review`
   flag and leaves a deliberately-set `lite`/`full`/`ultra` alone; `force`
   clears unconditionally.
3. **The plugin's own `SessionStart` hook**, which clears the flag when the
   configured default is `off`.

**The general lesson** — prefer stateless mechanisms; where state is
unavoidable, assume it leaks and contain it in layers — is why the dead-code
audit was designed with no state at all.

### Trust boundaries of the setup itself

- **Hooks execute arbitrary local code on every matching tool call.** Read every
  hook in `hooks/` before installing it. That is not a formality: a hook is the
  highest-privilege extension point here.
- **Plugins and marketplaces are third-party code** that loads into every
  session. `config/settings.example.json` names six plugins from three
  marketplaces. Evaluate them yourself; being listed here is not an audit.
- **Remote MCP servers receive your queries.** The screen-reference servers
  (Refero, Mobbin) and 21st.dev's component-research server are at user scope.
  Every query leaves the machine. With 21st.dev at user scope, substantial
  frontend work in any repository sends product and section descriptions to it
  unasked, because `frontend-quality` makes that research a step; disable the
  server for a project that must not send them. A keyed server's key sits in
  plain text in `~/.claude.json`. `permissions.deny` in `settings.json` blocks
  21st.dev's generation, publishing and account-write tools, but not
  `record_inspiration_feedback`, which sends accept and reject signals under the
  key. It matches by server and tool name, so a server connected under another
  name, or a renamed tool, is not blocked.
- **Skills and agents are instructions, not code.** They cannot execute anything
  on their own, but they do shape what the model does with tools it already has.
- **The installer writes only under `$HOME/.claude` (or `$CLAUDE_CONFIG_DIR`)**
  and backs up anything it would overwrite.

---

## Part 3 — Failure modes and risks

| Component | Fails how | Consequence | Mitigation |
|---|---|---|---|
| Deny-hooks | Fail **open** on unparseable input | A destructive command could pass | Narrow patterns, fast-path guard, denial names itself |
| Deny-hooks | **False positive** on an innocent command | Legitimate work blocked | `shlex` parsing; `-n` in a quoted message is not a flag; removal instructions in the message |
| Advisory hooks | Fail open, silently | A hint is missed | Nothing depends on the hint |
| Advisory hooks | Fire too often | Nagging, wasted tokens | Once per session per class; state reset on compact/clear |
| `read-budget-advisor` | State shared across agents | Wrong "you already read this" hints | Keyed by session **and** agent id |
| `run-captured` | Capture file not writable | Command runs uncaptured | Explicit fail-open path, message on stderr |
| `run-captured` | Summariser throws | Result could be hidden | Falls back to a raw tail plus exit code |
| `run-captured` | One enormous single line | Summarised in memory | Documented limit |
| `run-captured` | Used on a server or a prompt | Hangs | Documented: not for interactive or long-running commands |
| Graph bootstrap | Build fails or times out | No graph | Fails open, deletes the partial output it created, caches the failure for 24 h |
| Graph bootstrap | Recursion | Infinite loop | Env guard, command-name check, per-repo lock file |
| Graph bootstrap | Repo too large | Long stall | Hard budget, skip above a file-count ceiling |
| Ponytail flag | Leaks to subagents / other sessions | Wrong persona in a reviewer | Three containment layers (above) |
| Semantic triggers | Model does not notice them | Review silently skipped | The reporting requirement — a missing report is visible |
| Reporting requirement | Model claims a review it did not run | Undetectable from the transcript alone | **Unmitigated.** Findings must cite file and line, which makes fabrication checkable, but nothing enforces it |
| Judges | All agree and are all wrong | False confidence | Evidence ladder; `jury-arbiter` never counts votes; "a clean jury is not proof" is written into the skill |
| Judges | Hallucinate a finding | Wasted fix effort | Every finding needs a failure scenario and a location; unsupported claims are rejected |
| Path-scoped rules | Glob does not match a project's layout | Rule never loads | Check the `paths:` frontmatter against your tree |
| Installer | Overwrites a customised file | Local changes lost | Dry-run default, backup before every overwrite, refuses to merge settings |

### The largest residual risk

**The semantic triggers and the reporting requirement are not enforced by
anything.** A model that does not evaluate the triggers, or that reports a
review it did not perform, produces a transcript indistinguishable from a
correct one apart from the content of the findings themselves.

This is accepted deliberately — see
[why-this-setup.md](why-this-setup.md#why-no-machine-global-automatic-review-hook)
for why a hook cannot do this job — but it is a real limitation, not a solved
problem. The partial mitigation is that findings must carry file and line, and
rejections must carry reasons, both of which a human can check against the diff.
