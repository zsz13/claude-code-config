---
name: dead-code-audit
description: Use when a refactor, feature removal, library migration, flag retirement, or consolidation has finished and may have orphaned code - unused functions, exports, imports, branches, routes, components, CSS, adapters, or dependencies - and when asked to find dead code, unused code, or what can be deleted from a repository.
---

# Dead-code audit

**No reference found is not proof of death.** Static analysis and search tell you
where references are *visible*. Registries, string dispatch, framework
discovery, config, SQL, templates, CI, and external clients are all invisible to
them. Deletion requires positive evidence that nothing calls the code, not the
absence of evidence that something does.

Everything below serves one rule: **never remove a candidate because a search
came back empty.** Report it instead. An unremoved dead symbol costs a line of
report; a removed live one costs an outage.

## 1. Scope before searching

Audit the **blast radius of the change**: files the change touched, the symbols
it stopped calling, and the reverse dependencies of both. A repo-wide sweep is a
separate, explicitly requested job (`ponytail-audit` covers over-engineering;
this covers reachability).

Establish the baseline first — `git diff --name-status <base>` — so "what this
change orphaned" is a decidable question rather than a vibe.

## 2. Run the repository's own tools first

Prefer what the repo already has. Adding a dead-code tool as a dependency needs
the same justification as any dependency (`~/.claude/rules/tooling.md`); an
ephemeral `uvx`/`pnpm dlx` run adds nothing to the lockfile — use that, and ask
before the first one (it fetches from the network).

| Target | Python | TypeScript / React |
|---|---|---|
| Unused imports, locals, args | `ruff check --select F401,F811,F841,ARG,ERA` | `tsc --noEmit` with `noUnusedLocals`/`noUnusedParameters`; `eslint` `no-unused-vars` |
| Unreachable branches, impossible conditions | `ruff --select SIM,RET,PLR`; Pyright unreachable-code hints | `tsc` narrowing (`never`), `eslint no-constant-condition` |
| Unused module-level symbols, exports, files | no stock tool — §3 evidence; `uvx vulture <pkg> --min-confidence 80` as a *candidate generator* only | `pnpm dlx knip` (unused files, exports, deps) as a *candidate generator* only |
| Unused dependencies | `uvx deptry .` | `pnpm dlx knip` |
| Last reference in history | `git log -S'<symbol>' --oneline -- <paths>` | same |

Where a knowledge graph exists (`graphify-out/graph.json`, GitNexus index), use
`graphify affected "<Symbol>"` / impact queries for callers before reading
source — it answers reachability directly. LSP "find references" is the exact
answer for static symbols; it does not see dynamic access.

Vulture and knip produce **candidates, never verdicts**. Both are confidently
wrong about exactly the classes in §4.

## 3. Build reference evidence

For each candidate, search the **whole repository, not just source**:

```
rg -n --hidden -g '!.git' -g '!node_modules' -g '!.venv' -- '<symbol>'
```

Then search for the ways it could be reached without its name appearing:

| Reached by | Look for |
|---|---|
| Reflection / dynamic import | `getattr`, `globals()[`, `importlib`, `import()`, `require(`, `React.lazy`, string-keyed registries and factories |
| Framework discovery | Next.js `page/route/layout/middleware` files, FastAPI routers, Django app configs, Celery task names, pytest `conftest` fixtures, `__init_subclass__` / metaclass / decorator registration |
| Packaging | `[project.scripts]`, `entry_points`, `bin` in `package.json`, plugin manifests, `__all__`, barrel re-exports |
| Configuration | env vars, YAML/TOML/JSON settings, feature-flag stores, Docker `CMD`, cron, CI workflows, Terraform |
| Data & text | SQL, migrations, templates, i18n keys, class names built by template literal or `clsx`, Tailwind `content` globs, `public/` assets referenced from CSS/HTML |
| Outside the repo | other repos in the workspace, deployed clients, OpenAPI/SDK consumers, webhooks, docs and runbooks |

Then date it: `git log -S` gives the commit that removed the last caller. A
symbol orphaned by *this* change is a different finding from one orphaned two
years ago, and a symbol added last week and never called is probably an
unfinished feature, not dead code — check before deleting someone's in-flight work.

## 4. Classify by confidence

| Class | Criteria | Action |
|---|---|---|
| **Proven dead** | Zero references across every file type in §3; not in any never-remove class below; no import side effect; the change that orphaned it is identified; removal leaves the repo's gates green | Remove |
| **Likely dead** | No references found, but at least one uncertainty remains — dynamic access possible, external consumer possible, added recently, crosses a process or repo boundary | Report with the uncertainty named. Do not remove |
| **Intentionally retained** | Matches a class below, or has a stated reason | Report once; leave a plain comment at the symbol saying why, so the next audit does not re-litigate it |

**Never remove on an audit's own authority** (report, ask, or leave):

- public API surface — anything exported by a published package, a documented
  endpoint, or a cross-service contract; unused internally ≠ unused;
- reflection and dynamic-import targets, and anything in a registry keyed by string;
- framework-discovered code — route files, hooks, lifecycle entry points, DI providers;
- CLI entry points and scripts;
- database migrations — they are history, not code; a merged migration is never dead;
- test fixtures, factories, and `conftest` helpers;
- plugin and adapter registration, including imports whose only job is the side effect;
- compatibility shims still inside their stated support window;
- anything under `app/models/__init__.py`-style aggregation that a mapper,
  autogenerate step, or serializer discovers by import.

A symbol used **only by tests** is a finding, not a licence: either the feature
is dead (remove code and tests together) or the test is the last user of live
behavior (keep both). Decide with `git log`, then say which you concluded.

## 5. Remove, if and only if proven dead

- Remove the symbol **and** what it orphans: imports, its tests, fixtures, mocks,
  config entries, and docs references. A deletion that leaves a dangling import
  or a test for nothing is half a change.
- Deletions go in their **own commit**, separate from behavior changes, so a
  revert is surgical and a bisect is readable.
- Before deleting a module or an import, ask what its import *did*. Registration,
  signal wiring, monkey-patching, and mapper configuration all happen at import
  time and leave no call site.
- Never delete to "see if anything breaks" across a process, network, or repo
  boundary. That experiment runs in production.
- Removing a flag means removing the dead branch **and** the flag's config,
  defaults, and documentation — after confirming the deployed environments no
  longer set it.

## 6. Validate

Run the repository's own gates for what you touched — formatter, lint, type
check, affected tests, and the build where deletion could change bundling or
imports. Deleting code can only be verified by the suite that would have used
it, so a full-suite run is usually the right proportion here, not a targeted one.
Never report a removal while a relevant check is failing.

## 7. Report (required, every automatic run)

Nothing executes this audit and nothing marks it: the report is the only
evidence it ran. Emit it in the transcript:

```
**Dead-code audit** — scope: <files/subsystem>, tools: <what actually ran>

Removed (proven dead):
- <path>:<line> <symbol> — <evidence: refs searched, orphaning commit, gate result>

Retained (likely dead):
- <path>:<line> <symbol> — <the uncertainty that blocks removal>

Retained (by class):
- <path>:<line> <symbol> — <public API | framework | CLI | migration | fixture | registration | dynamic>

Validation: <commands> → <result>
```

Empty sections stay, marked "none". "Nothing found" is a result worth stating.

## Rationalizations

| Excuse | Reality |
|---|---|
| "`rg` found zero hits, so it's dead" | `rg` searched text you thought to search. Registries, config, SQL, CI, and other repos were not in it. |
| "The tests still pass" | A suite is not a caller census. It covers what someone wrote a test for. |
| "It's only used by tests" | A finding, not a licence. Decide whether the *feature* is dead, then remove both or neither. |
| "It's obviously legacy" | Then date it with `git log -S` and say the date. "Obviously" is not evidence. |
| "The type checker flagged it unused" | `noUnusedLocals` is file-scoped and `F401` is import-scoped. Neither knows who imports this module. |
| "knip/vulture reported it with high confidence" | Both are candidate generators that cannot see dynamic access. Confidence is their heuristic, not your evidence. |
| "I'll delete it and see what breaks" | Fine inside one process with a full suite. Never across a network, a client, or another repo. |
| "It's small, deleting is low risk" | Size is unrelated to reachability. A four-line module can be the one that registers every adapter. |
| "I'll clean it up while I'm in here" | Deletions belong in their own commit, after the change that orphaned them is green. |

## Red flags — stop

- About to delete something whose only evidence of death is an empty search.
- About to delete a migration, a route file, an entry point, or an `__init__` import.
- About to delete mid-refactor, before the refactor's own gates are green.
- About to mix a deletion into a behavior-change commit.
- Reporting a removal without naming the check that proved behavior unchanged.
