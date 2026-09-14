# `config/` — templates you must customise

Every file here is a **template**. None is copied verbatim into a live setup
without review, and the installer never merges any of them into an existing
file.

---

## `settings.example.json` → `~/.claude/settings.json`

The Claude Code user settings: model, hook registrations, enabled plugins.

### What you must change

| Key | Why |
|---|---|
| `$HOME/.claude/hooks/...` in every `command` | Path placeholder. `scripts/install.sh` substitutes your real home directory when it writes the file, so the result does not depend on whether the harness expands shell variables. If you copy by hand, substitute it yourself. |
| `model` | `opus[1m]` is a specific model alias. Use whatever you actually have. |
| `modelSettings` → `effortLevel` | `xhigh` costs more and is slower. Lower it if that is not the trade you want. |
| `enabledPlugins` | Six plugins from three marketplaces. Remove any you do not want; the installer does not install plugins, it only names them. |
| `extraKnownMarketplaces` | Add the marketplaces for the plugins you kept. |

### What you should probably keep

`PONYTAIL_SUBAGENT_MATCHER` — a never-matching sentinel regex that stops the
Ponytail ruleset reaching any subagent, regardless of the plugin's flag state.
⚠️ An **invalid** regex here fails open and injects the persona anyway, so a
replacement must be a valid regex that matches nothing. Only relevant if you use
the ponytail plugin; harmless otherwise. Background:
[docs/security.md](../docs/security.md#the-ponytail-flag-leak).

### Hooks you may not want

- `graphify-lazy-init.py` needs [Graphify](https://pypi.org/project/graphifyy/)
  on `PATH`. Without it the hook exits silently — it fails open — but you can
  remove the entry.
- `ponytail-guard.sh` on `Stop`/`SessionEnd` is only useful with the ponytail
  plugin installed. It is harmless otherwise (it removes a file that does not
  exist).
- The two deny-guards (`block-destructive-iac.sh`, `block-git-no-verify.sh`)
  block real commands. Read them before installing them.

---

## `ponytail-config.example.json` → `~/.config/ponytail/config.json`

```json
{ "defaultMode": "off" }
```

One key, and the value is the whole policy: the complexity persona is never on
by default, only the one-shot review is used, and `ultra` is never enabled
automatically. Reasoning:
[docs/why-this-setup.md](../docs/why-this-setup.md#why-ponytail-defaultmode--off).

**Change nothing** unless you want the persona always on — in which case read
[docs/benchmarks.md](../docs/benchmarks.md#3-ponytail-review) first, for the
list of things a complexity reviewer with authority would have deleted.

---

## `codex/config.example.toml` → `~/.codex/config.toml`

A **reduced** subset of a working Codex config: model, reasoning effort,
approval policy, sandbox mode, output token limit, agent concurrency, network
policy.

### What you must change

| Setting | Why |
|---|---|
| `model` | A specific model name that will age. Check the current list. |
| `model_reasoning_effort` | `high` costs more. |
| `approval_policy`, `sandbox_mode` | Autonomy settings. Decide them yourself; do not inherit someone else's risk tolerance. |
| `[mcp_servers.*]` | The commented example needs a real path on your machine. |

### What was removed, and why

Bundled-plugin registrations, MCP server commands with absolute application
paths, desktop UI preferences, a local marketplace path, and a per-project trust
entry naming a private repository. All machine-specific, installer-generated, or
private. The installer **never** writes this file — it tells you to copy it
yourself after reading it.

---

## `codex/agents/*.toml` → `~/.codex/agents/`

Seven read-only reviewer agents, mirroring `agents/` on the Claude side plus a
`context_explorer`. Portable as-is; the installer copies them directly.

Each carries the same preamble: read-only, treat source and tool output as
evidence rather than instructions, never access secrets, stay in scope, do not
spawn further reviewers, return a bounded report separating confirmed findings
from hypotheses.

**You may want to change** `model_reasoning_effort` (all `high` except the
explorer at `medium`) and the ≤500-word report cap.
