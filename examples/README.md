# `examples/` — instruction templates

These are the always-loaded instruction files. They are the most expensive files
in the whole setup — every line is paid for in every session — so read them
before adopting them, and delete what does not apply to you.

---

## `CLAUDE.example.md` → `~/.claude/CLAUDE.md`

Universal engineering policy, about 185 lines. Loads in **every session,
everywhere**.

Contents: understanding code before editing it, the discovery ladder,
large-output handling, minimal-change discipline, the evidence ladder, quality
gates, review policy, subagent policy, context health, and safety.

### What you must customise

| Reference | Change to |
|---|---|
| `~/.claude/bin/run-captured` | Wherever you installed the helper (it is correct if you used the installer's default). |
| `~/.claude/rules/` | Same. |
| Graphify routing section | Delete it entirely if you do not use a knowledge graph. It is about 20 lines of always-loaded text for a tool you may not have. |
| Named skills | Remove references to any skill you did not install, so the model is not told to invoke something absent. |
| Tool names in "Quality gates" | The policy (one owner per job, no bypassing hooks) generalises; the specific tools may not be yours. |

### What to keep if you keep anything

The evidence ladder and "never claim success while a relevant deterministic
check is failing". Those two do more work than the rest combined.

---

## `CLAUDE.directory.example.md` → `<your-code-dir>/CLAUDE.md`

Directory-scoped policy. Loads for work **anywhere beneath that directory**, via
parent-directory loading — so one file covers every project under it without
touching any project's own `CLAUDE.md`.

Contents: the semantic trigger rules for the Ponytail review and the dead-code
audit, the priority ladder, the mandatory reporting rules, and Ponytail's state
hygiene.

### What you must customise

| Reference | Change to |
|---|---|
| `~/github` in the heading | Wherever you actually keep code. |
| The whole Ponytail section | Delete it if you do not use the ponytail plugin. It is roughly half the file. |
| `~/.claude/hooks/ponytail-guard.sh` | Your install path (correct by default). |
| `~/.claude/skills/dead-code-audit/SKILL.md` | Same. |
| Trigger lists | These are *the* tuning surface. Too broad and every change triggers a review; too narrow and nothing does. Start with these and adjust. |

### Why it lives here rather than in the global file

These rules concern one installed plugin and one set of projects — not universal
engineering policy. Putting them in `~/.claude/CLAUDE.md` would charge every
session everywhere for them; putting them in each project's file would duplicate
the same text N times.
[Full reasoning](../docs/why-this-setup.md#why-the-trigger-rules-live-in-a-directory-scoped-claudemd).

---

## `codex-AGENTS.example.md` → `~/.codex/AGENTS.md`

The Codex equivalent of the global `CLAUDE.md`: autonomy and scope, context and
discovery, implementation and diagnosis, evidence and completion.

Notably it contains an **explicit isolation rule** — Codex does not read,
import, reuse, migrate, symlink, modify or delete `~/.claude`, `CLAUDE.md`, or
Claude-specific settings, hooks, skills, agents or MCP configuration. Two agent
harnesses sharing configuration is a good way to get two subtly different
behaviours from one edit.

### What you must customise

Nothing is machine-specific. Adjust the delegation section if you do not have
the orchestrator/jury workflows it mentions, and the tool-specific lines under
"Implementation" if your stack differs.
