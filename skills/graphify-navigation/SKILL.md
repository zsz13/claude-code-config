---
name: graphify-navigation
description: Route code-graph questions to the one graph a repository has - GitNexus where it has a .gitnexus/ index, Graphify otherwise - to understand architecture, dependencies, call and data flow, and change impact before reading source. Use when a repo has .gitnexus/ or graphify-out/graph.json, when a graph hook reports one, or when a task needs cross-cutting understanding of an unfamiliar codebase.
---

# Code-graph navigation

A repository gets one knowledge graph. **GitNexus** (MCP server, symbol-level
call graph with impact analysis) when the repo has a `.gitnexus/` index;
**Graphify** (`graphify` CLI, offline tree-sitter extraction) otherwise. The
graph answers *where* and *how things connect*; LSP answers *exactly which
symbol*; targeted reads answer *what the code does*. Use them in that order and
do not stack overlapping tools (the other graph, Serena, Repomix, broad `rg`) on
the same question unless the first answer is insufficient.

## When to reach for it

Architecture discovery, dependency analysis, call-flow or data-flow tracing,
impact analysis, cross-layer request tracing, refactors spanning subsystems,
orienting in an unfamiliar codebase. Not for: a known function in a known file,
a trivial edit, a literal string search.

## GitNexus (repository has `.gitnexus/`)

The MCP tools are deferred; load the ones you need with one ToolSearch
(`select:mcp__gitnexus__context,mcp__gitnexus__impact`). Pass `repo` (the
directory name, unless `gitnexus list` shows an alias) and skip the
`list_repos` and `gitnexus://` resource reads the tool's own skills open with:
they cost calls and return nothing a direct query does not.

| Question | Tool | Keep it small with |
|---|---|---|
| Who calls this, what does it call | `context` (`name`, `file_path` if ambiguous) | `maxTokens` |
| What breaks if I change it | `impact` (`direction: "upstream"`) | `maxDepth: 2`, `limit`, `summaryOnly` for a hub |
| What my diff touches | `detect_changes` | — |
| Where a concept lives | `query` | `limit: 3`, `max_symbols` |
| How A reaches B | `trace` | — |

Read only the line ranges the result names. Read `epistemic`: `exact` is the
whole caller set, `lower-bound` or risk `UNKNOWN` means callers exist that the
graph cannot see (dynamic dispatch, framework injection), so search for the name
before deleting or renaming. The `gitnexus-impact-analysis`,
`gitnexus-refactoring` and `gitnexus-debugging` skills hold the tool's longer
workflows; use them for a rename or a risky refactor, not for one lookup.

**Freshness.** `gitnexus status` in the repo prints the indexed and current
commit. The tool's PostToolUse hook also reports a stale index after a commit.
Reindex only when the change you are reasoning about is not in the index:
`gitnexus analyze --index-only` (incremental). Without `--index-only`, `analyze`
writes a GitNexus section into the repository's `CLAUDE.md`/`AGENTS.md` and
skills into its `.claude/skills`. Never run `gitnexus setup`, and do not index a
new repository unless asked.

**Degraded search.** An empty `query` carrying a `FTS extension failed to load`
warning is a broken index, not an absence of code: do not retry it. Use
`context` on a name you know, or a targeted search, and tell the user that
`gitnexus doctor` shows the missing extension. Repairing it
(`GITNEXUS_LBUG_EXTENSION_INSTALL=auto gitnexus analyze --repair-fts --index-only`)
downloads the extension, so it is the user's decision.

## Graphify commands (run from the repository root)

```
graphify query "<focused question>" [--budget 1500] [--context call]
graphify explain "<Symbol or file>"        # node + neighbors in plain language
graphify affected "<Symbol>" [--depth 2]   # reverse traversal: what breaks if this changes
graphify path "<A>" "<B>"                  # shortest connection between two entities
graphify god-nodes --top 10                # architectural hubs
```

Ask one focused question at a time; a `query` truncated by its token budget is a
signal to narrow, not to raise the budget without thought. `query` returns node
ids with `src=<file> loc=L<n>`: read those ranges, not whole files. Do not read
`GRAPH_REPORT.md` wholesale; `god-nodes` and `query` give the same orientation in
a fraction of the tokens.

## Building and refreshing Graphify

A global PreToolUse hook (`~/.claude/hooks/graphify-lazy-init.py`) initializes a
graph automatically when a broad repository search is about to run in a git repo
with roughly 50+ tracked source files or 10k+ source lines, then installs
Graphify's incremental git hooks. It skips a repository with a GitNexus index.
It fails open and never blocks. To build by
hand (offline, no API key, no visualization):

```
graphify extract . --code-only --no-viz
graphify cluster-only . --no-label --no-viz   # writes GRAPH_REPORT.md
graphify hook install                         # post-commit / post-checkout incremental rebuilds
```

The git hooks keep the graph current for committed changes. Do **not** rebuild
after every edit. Refresh manually only when substantial *uncommitted* changes
make the graph stale **and** the task needs accurate dependency or impact
reasoning for the final analysis:

```
graphify update . --no-cluster     # or: graphify extract . --code-only --no-viz
```

Ignore rules live in `.graphifyignore` (gitignore syntax; `.gitignore` is already
respected). Never use `.claudeignore`; it is not a Claude Code mechanism. Do not
create `.graphifyignore` unless the default excludes are provably wrong for that
repository.

`graphify-out/` is excluded locally (`.git/info/exclude`) when the hook builds
it. Do not commit it unless the project already tracks it. Never run
`graphify claude install --strict`: it rewrites Claude Code behavior and blocks
raw file reads.

## Division of responsibility

| Need | Tool |
|---|---|
| Callers, callees, blast radius, diff-to-symbol mapping | GitNexus where indexed, else Graphify |
| Subsystem map, hubs, dependency graph | Graphify (GitNexus `query`/`cypher` where indexed) |
| Definition, references, implementations, diagnostics, call hierarchy | LSP (`pyright-lsp`, `typescript-lsp`) |
| Actual implementation details | targeted `Read` of the ranges Graphify/LSP pointed to |
| Literal string, config key, error message | targeted `Grep` |
| Packaging a repo for an external model or reviewer | Repomix, on demand only |
