# claude-code-config

A working configuration for AI coding agents — **Claude Code** primarily, with a
matching **Codex** reviewer set — built around one idea:

> An agent's context window is a budget. Spend it on the code, not on
> instructions about how to read the code.

Everything here is either (a) always-on policy compressed to the minimum that is
true everywhere, (b) guidance that loads only when it is relevant, or (c) a hook
that executes without entering context at all.

This is not a dotfiles backup. Every component is documented with what it does,
why it exists, what was considered instead, and how it fails.

**Start here:** [docs/why-this-setup.md](docs/why-this-setup.md) explains the
non-obvious decisions. [docs/benchmarks.md](docs/benchmarks.md) is honest about
which claims are measured and which are not.

---

## What is in here

| Directory | What it is | Loads |
|---|---|---|
| [`rules/`](rules/) | 7 path-scoped rules (Python, TypeScript, frontend, tests, tooling, infra, migrations) | Only when a matching file path is touched |
| [`skills/`](skills/) | 10 procedures the model invokes by name | On invocation |
| [`agents/`](agents/) | 7 reviewer subagent definitions | Inside their own subagent |
| [`hooks/`](hooks/) | 2 deny-guards + 5 advisors | Executed, never loaded |
| [`bin/`](bin/) | `run-captured` — large command output kept on disk | Run as a command |
| [`config/`](config/) | Sanitized `settings.json`, Ponytail and Codex templates | — |
| [`examples/`](examples/) | `CLAUDE.md` templates (global, directory-scoped, Codex) | — |
| [`workflows/`](workflows/) | The review pipeline and when each stage fires | — |
| [`docs/`](docs/) | Architecture, rationale, alternatives, security, evidence | — |
| [`scripts/`](scripts/) | Installer (dry-run by default) and verifier | — |

## The idea in one diagram

```
ALWAYS LOADED       CLAUDE.md (~185 lines of universal policy)
                    settings.json
     │
CONDITIONAL         rules/     → only when a matching file is touched
                    skills/    → only when invoked
                    agents/    → only inside the subagent
     │
NEVER LOADED        hooks/     → executed on tool events; only their output
                    bin/          (one line, or a denial) reaches the context
```

A path-scoped rule beats a skill, a skill beats a line in `CLAUDE.md`, and a
hook that emits one line at the right moment beats all three. Details in
[docs/architecture.md](docs/architecture.md).

## The review pipeline

```
implement → validate → dead-code audit → Ponytail review
          → apply simplifications → re-validate → adversarial jury
```

Each stage has explicit trigger conditions, an explicit authority level, and a
mandatory report. Two of the stages are **instructions, not hooks** — a semantic
trigger ("a new abstraction was introduced") is not something a hook can
evaluate — which means the report is the only evidence they ran, which is why
reporting is required rather than optional.

Full explanation: [workflows/review-pipeline.md](workflows/review-pipeline.md).

## Highlights

**Blind adversarial review.** Six judges — spec, correctness, tests,
architecture, security, and a rendered-interface judge — review a change in
parallel, each in its own context, none seeing the implementer's reasoning or
each other's findings. Conflicts are resolved by an arbiter that ranks evidence
and **never counts votes**, because judges share training data and their
agreement is correlated rather than independent.

**An evidence ladder, written down.**

> reproducible runtime behavior > compiler/build > tests > type checker >
> static/security analysis > lint > concrete source evidence > LLM opinion

Corollaries that are stated explicitly because they are easy to forget:
*agreement among reviewers is not proof*, and *neither is a passing test suite*.

**A dead-code audit that refuses to guess.** "No reference found is not proof of
death." Only *proven dead* code is removed; anything reachable through a
registry, a framework, packaging metadata, config, SQL or another repo is
reported and left alone. An unremoved dead symbol costs a line of report; a
removed live one costs an outage.

**Large output kept out of context without hiding anything.**
[`bin/run-captured`](bin/run-captured) runs a command unchanged, keeps the full
stdout+stderr on disk, propagates the exit status, and surfaces distinct
diagnostic lines with line numbers plus the tail. It never reports success when
the command failed, and small output passes through verbatim. Measured: **92%
less output surfaced** across the invocations large enough to be reduced — with
the caveats in [docs/benchmarks.md](docs/benchmarks.md#1-context-efficiency-layer--run-captured).

**Two things the agent is not allowed to do.** `terraform apply`/`destroy` and
`git commit --no-verify` are denied by hooks, because those are the two commands
where good judgement is not a sufficient safeguard. Both explain themselves and
say how to remove them.

## Install

**Requirements:** bash, Python 3.11+ (for the hooks and `tomllib`), git.
Claude Code for the Claude half; Codex for the Codex half. Optional:
[Graphify](https://pypi.org/project/graphifyy/) for the knowledge-graph hook,
the [ponytail](https://github.com/DietrichGebert/ponytail) plugin for the
complexity review.

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY

# 1. Read the hooks. They execute on your machine on every matching tool call.
less hooks/*.sh hooks/*.py

# 2. See exactly what would change. This is the default — nothing is written.
./scripts/install.sh

# 3. Install. Existing files that differ are reported as conflicts, never
#    silently replaced.
./scripts/install.sh --apply

# 4. Check the result.
./scripts/verify.sh
```

Partial adoption is the expected case:

```bash
./scripts/install.sh --components skills,agents --apply   # just the review layer
./scripts/install.sh --components hooks,bin --apply       # just the guards + helper
./scripts/install.sh --components codex --apply           # just the Codex reviewers
./scripts/install.sh --list                               # what is available
```

### Installer guarantees

- **Dry run is the default.** Nothing is written without `--apply`.
- **Never overwrites silently.** A file that differs is a `CONFLICT`, the
  installer exits 1, and nothing is written. `--force` overwrites — after
  copying the existing file into a timestamped backup directory.
- **Never merges `settings.json`.** If one already exists, the installer writes
  `settings.claude-code-config-proposed.json` beside it and tells you to diff
  them. `--force` does not change this.
- **Idempotent.** A second run reports everything as already identical.
- **`$HOME`-relative.** Honours `$CLAUDE_CONFIG_DIR` and `$CODEX_HOME`;
  `--target` overrides both. Nothing is hard-coded to one machine.
- **Hook paths are rendered.** The template in `config/` uses `$HOME`; the
  installer substitutes the real absolute path when it writes, so the result
  cannot depend on whether the harness expands shell variables.

`./scripts/verify.sh` checks the repository (scripts parse, JSON/TOML parse,
frontmatter present, links resolve, no personal paths) and, if a target is
installed, that every file matches, hooks are executable, and every hook command
in `settings.json` points at a file that exists.

### Manual install

Copy `rules/`, `skills/`, `agents/`, `hooks/`, `bin/` into `~/.claude/`, merge
`config/settings.example.json` into `~/.claude/settings.json` (replacing `$HOME`
with your home directory if your setup does not expand it), and copy
`examples/CLAUDE.example.md` to `~/.claude/CLAUDE.md`. See
[config/README.md](config/README.md) and [examples/README.md](examples/README.md)
for what each template needs customised.

## Before you adopt this

- **Hooks run arbitrary local code on every matching tool call.** Read them.
  That is the highest-privilege extension point here, and "I trusted the README"
  is not a security model.
- **It is opinionated about tooling** — uv, Ruff, Pyright, pytest; ESLint,
  Prettier, tsc, Vitest — with one owner per job. The *policy* (no overlapping
  tools, no global version pins, preserve a working repository's choices)
  generalises; the specific picks may not match yours.
- **Some of it is unmeasured.** [docs/benchmarks.md](docs/benchmarks.md) labels
  every claim as measured, observed, rationale, hypothesis, or not proven. The
  end-to-end question — does this produce better software? — is open.
- **It assumes a capable model.** The semantic triggers and the mandatory
  reporting depend on the model actually evaluating them. Nothing enforces that.

## Documentation

| Document | What it answers |
|---|---|
| [docs/architecture.md](docs/architecture.md) | What each component is, what loads when, how they interact |
| [docs/why-this-setup.md](docs/why-this-setup.md) | Why each non-obvious decision was made |
| [docs/alternatives.md](docs/alternatives.md) | What else was considered, and why it was not chosen |
| [docs/security.md](docs/security.md) | What was excluded from this repo, security properties, failure modes |
| [docs/benchmarks.md](docs/benchmarks.md) | Measured vs observed vs reasoned vs unproven |
| [workflows/review-pipeline.md](workflows/review-pipeline.md) | The pipeline, triggers, and how the review mechanisms differ |

## Third-party components

Referenced and configured here, **not** redistributed — install each from its
own source:

| Component | Licence | Role |
|---|---|---|
| [Superpowers](https://github.com/anthropics/claude-plugins-official) | see project | Process skills: brainstorming, TDD, systematic debugging |
| [ponytail](https://github.com/DietrichGebert/ponytail) | MIT | Complexity review (`/ponytail-review`) |
| [Graphify](https://pypi.org/project/graphifyy/) | Apache-2.0 | Code knowledge graph used by the lazy-init hook |
| frontend-design, playwright, pyright-lsp, typescript-lsp | see projects | Official Claude Code plugins |

One tool used on the source machine is **deliberately absent**: its hook and
skills are licensed PolyForm Noncommercial, so redistributing them from an MIT
repository is not permitted. The corresponding settings entries were removed too,
so nothing here references a file it does not ship. See
[docs/security.md](docs/security.md#never-published--third-party-code-under-a-restrictive-licence).

## Licence

[MIT](LICENSE). The configuration, hooks, scripts and documentation in this
repository only. Third-party tools keep their own licences.
