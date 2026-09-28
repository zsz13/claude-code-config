# Architecture

How the pieces fit together, what loads when, and what talks to what.

## The layers

```
┌──────────────────────────────────────────────────────────────────────┐
│ ALWAYS LOADED (paid for in every single session)                     │
│   ~/.claude/CLAUDE.md            universal engineering policy        │
│   ~/.claude/settings.json        model, hooks, plugins, deny rules   │
│   <dir>/CLAUDE.md                directory-scoped policy             │
│   plugin + MCP routing descriptions                                  │
├──────────────────────────────────────────────────────────────────────┤
│ CONDITIONALLY LOADED                                                 │
│   rules/*.md      loaded only when a matching file path is touched   │
│   skills/*        loaded only when the model invokes them            │
│   agents/*        loaded only inside the subagent that runs them     │
├──────────────────────────────────────────────────────────────────────┤
│ EXECUTED, NEVER LOADED                                               │
│   hooks/*         run by the harness on tool events; only their      │
│                   output (a line or a denial) reaches the context    │
│   bin/run-captured  run as a command; keeps output on disk           │
└──────────────────────────────────────────────────────────────────────┘
```

The single organising principle is **engineering quality per unit of context**.
Every always-on component is paid for in every session and disturbs the prompt
cache. So the design pushes everything down the list: a path-scoped rule beats a
skill, a skill beats a line in `CLAUDE.md`, and a hook that emits one line beats
all three when the guidance is only needed at the moment of a specific action.

## Component map

### 1. `CLAUDE.md` — universal policy (always loaded)

About 185 lines. Holds only what is true for every language, every repository,
every task: how to understand code before editing it, the discovery ladder
(knowledge graph → symbol lookup → targeted search → targeted reads → whole
files → traversal), large-output handling, minimal-change discipline, the
evidence ladder, quality gates, review policy, subagent policy, context health,
and safety.

Deliberately *not* here: stack-specific conventions, tool commands, per-project
architecture. Those go one layer down.

### 2. Directory-scoped `CLAUDE.md` (loaded for work under that directory)

A `CLAUDE.md` in a parent directory of the working directory loads for
everything beneath it. The example in
[`examples/CLAUDE.directory.example.md`](../examples/CLAUDE.directory.example.md)
sits at the root of a code directory and holds the semantic trigger rules for
the Ponytail review and the dead-code audit, the priority ladder, the reporting
requirement, and Ponytail's state-hygiene rules.

It lives there rather than in the global file because those rules are about a
particular set of projects and a particular installed plugin — not universal
engineering policy — and rather than in four separate project files because
that would duplicate the same text four times.

### 3. `rules/` — path-scoped rules (loaded on matching file paths)

Seven files, each with a `paths:` frontmatter glob list:

| Rule | Loads when touching |
|---|---|
| `python.md` | `*.py`, `*.pyi`, `pyproject.toml` |
| `typescript.md` | `*.ts`, `*.tsx`, `*.js`, `*.jsx`, … |
| `frontend.md` | `*.tsx`, `*.vue`, `*.svelte`, CSS, HTML, tailwind config |
| `tests.md` | test files, `conftest.py`, `e2e/`, runner configs |
| `tooling.md` | lockfiles, lint/format/type configs, CI config, `.pre-commit-config.yaml` |
| `infrastructure.md` | Terraform, Dockerfiles, compose, CI workflows, k8s, helm |
| `migrations.md` | `migrations/`, `alembic/`, `prisma/`, `*.sql` |

**Never put an unscoped rule in `rules/`.** An unscoped rule costs exactly what
`CLAUDE.md` costs, with an extra layer of indirection.

### 4. `skills/` — procedures (loaded on invocation)

Ten skills. Each is a procedure the model reads when it decides the situation
calls for it:

- `adversarial-jury` — blind multi-lens review protocol (+ `packet-template.md`)
- `dead-code-audit` — reachability audit with confidence classification
- `context-budget` — the large-output / search / read playbook
- `frontend-quality` — routes UI work, requires a real browser render
- `design-brief` — establishes a product-specific visual direction
- `infrastructure-quality` — routes IaC work
- `migration-review` — schema/data migration safety review
- `project-tooling-setup` — quality toolchain for a new or incomplete repo
- `dependency-modernization` — runtime/dependency audit and upgrade
- `graphify-navigation` — using a code knowledge graph before reading source

### 5. `agents/` — reviewer lenses (loaded inside their own subagent)

Seven subagent definitions. Six are judges for the adversarial jury; each has
one lens and is explicitly told what its own evidence cannot prove.

| Agent | Lens | Model / effort |
|---|---|---|
| `spec-judge` | Does the change satisfy the original requirement? | opus / high |
| `correctness-adversary` | Actively tries to falsify the implementation | opus / high |
| `test-judge` | What does the test suite fail to prove? | sonnet / high |
| `architecture-judge` | Structural and long-term maintenance cost | opus / high |
| `security-judge` | Trust boundaries and reachable exploit paths | opus / high |
| `jury-arbiter` | Resolves conflicts by evidence, never by vote | opus / xhigh |
| `visual-design-judge` | Judges the *rendered* interface, not the source | opus / high |

All are read-only. `correctness-adversary` may dispatch shallow `Explore`
subagents to verify one candidate finding; none may edit, run commands, or spawn
a reviewer.

`test-judge` runs on a cheaper model deliberately — its lens (what is untested)
is more enumerative than inferential. This is a cost/benefit judgement, not a
measured result.

### 6. `hooks/` — deterministic guards and advisors (executed, never loaded)

Seven user-authored hooks. Two block; five advise. All fail open except the two
guards, which fail open on parse errors but deny on a positive match.

| Hook | Event | Behavior |
|---|---|---|
| `block-destructive-iac.sh` | PreToolUse(Bash) | **Denies** `terraform`/`tofu` apply, destroy, import, taint, force-unlock, `state mv/rm/push`. Read-only operations always pass. |
| `block-git-no-verify.sh` + `.py` | PreToolUse(Bash) | **Denies** `git commit/push/merge/rebase --no-verify`, `commit -n`, `-c core.hooksPath=`, and setting `core.hooksPath`. Parsed with `shlex`, so `-n` inside a quoted commit message is not a flag. |
| `large-output-advisor.sh` + `.py` | PreToolUse(Bash) | One-line hint for a command class about to dump a large deterministic output. At most once per session per class. |
| `read-budget-advisor.sh` + `.py` | PreToolUse + PostToolUse(Read\|Bash) | Hints on re-reading an unchanged file, and on whole-file reads of large files. State keyed by session **and** agent id. |
| `read-budget-reset.sh` | SessionStart(compact\|clear) | Clears that state so post-compaction reads are never flagged as re-reads. |
| `graphify-lazy-init.py` | PreToolUse(Grep\|Glob\|Bash) | Builds a code knowledge graph once, lazily, only for a repo big enough to justify it. |
| `ponytail-guard.sh` | Stop + SessionEnd | Clears a leaked Ponytail `review` flag. Leaves a deliberately-set mode alone. |

Each shell wrapper has a cheap `case` fast path so the Python classifier is only
paid for when the payload could possibly match.

### 7. `bin/run-captured` — large output kept out of context

Runs a command unchanged (stdin inherited, no `pipefail`, no env edits), streams
stdout+stderr in write order to a capture file, exits with the command's own
status, and prints only: the command, `exit=<code> ok|FAILED`, duration, size,
the capture path, distinct diagnostic lines with `L<n>` line numbers, and the
tail (12 lines on success, 40 on failure).

Guarantees that make it safe to use by default:

- it never reports success when the command failed;
- output of ≤60 lines and ≤6 KB is passed through **verbatim**, so an
  unexpectedly small result costs nothing extra;
- lines naming individual tests are keyed verbatim, so `test_x[404]` and
  `test_x[500]` are never folded into one "similar" bucket;
- a failure whose text matches no known pattern also shows the head, so it
  cannot vanish;
- options are only recognised *before* the command, so the command's own flags
  (`docker logs --tail 200`) are never consumed;
- if the summary step itself throws, it falls back to a raw tail rather than
  hiding the result;
- if the capture file cannot be created, it runs the command uncaptured.

`ledger.tsv` in the capture directory records bytes captured versus bytes
surfaced per run — the evidence base for any claim about what this saves.

## How components interact

**The pipeline.** [`workflows/review-pipeline.md`](../workflows/review-pipeline.md)
is the ordering contract: implement → validate → dead-code audit → Ponytail
review → re-validate → adversarial jury.

**Routers must not compete.** There is exactly one workflow router (Superpowers),
one reviewer router (`adversarial-jury`), and one orchestrator (the main model).
A component that wants to be a third router is not installed — see
[alternatives.md](alternatives.md).

**Code intelligence is not stacked.** A knowledge graph answers architecture,
dependencies, call/data flow and impact; LSP answers exact symbols and
diagnostics; reads answer implementation details. Running two graph systems
against the same question costs twice and answers once.

**Hooks never carry policy alone.** The IaC hook enforces what
`rules/infrastructure.md` and `skills/infrastructure-quality` explain. The
no-verify hook enforces what `CLAUDE.md`'s quality-gates section states. A guard
without its written reason is a mystery denial.

**The context-efficiency layer is a loop.** The advisors hint at the moment of
the action; `context-budget` holds the full playbook the hints point at;
`run-captured` makes the compact choice as easy as the expensive one; the ledger
and `/context` measure whether any of it worked.

## Global vs project scope

| Scope | What lives there |
|---|---|
| **Global** (`~/.claude/`) | `CLAUDE.md`, `settings.json`, all seven rules, all ten skills, all seven agents, all hooks, `bin/run-captured`; at user scope in `~/.claude.json`, the screen-reference MCPs (Refero, Mobbin), without their bundled skills |
| **Directory** (`<code-dir>/CLAUDE.md`) | Ponytail and dead-code trigger rules, priority ladder, reporting requirement, Ponytail state hygiene |
| **Project** (`<repo>/CLAUDE.md`, `<repo>/.claude/`) | Architecture, commands, conventions, project-specific plugins |
| **Deliberately not global** | Infrastructure agent packs, design-system/style catalogs, shadcn's, Motion's and 21st.dev's MCPs (per project, where the project uses that stack), any MCP's bundled design skill, any second security reviewer, any version pin |

Precedence runs the other way: a repository's own `CLAUDE.md` wins over the
directory file, which wins over the global one.
