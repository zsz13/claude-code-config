---
name: graphify-navigation
description: Use Graphify's code knowledge graph to understand architecture, dependencies, call and data flow, and change impact before reading source. Use when a repo has graphify-out/graph.json, when the graphify hook reports a graph, or when a task needs cross-cutting understanding of an unfamiliar codebase.
---

# Graphify navigation

Graphify (`graphify` CLI, offline tree-sitter extraction) is the primary
knowledge-graph layer. It answers *where* and *how things connect*; LSP answers
*exactly which symbol*; targeted reads answer *what the code does*. Use them in
that order and do not stack overlapping tools (GitNexus, Serena, Repomix, broad
`rg`) on the same question unless Graphify's answer is insufficient.

## When to reach for it

Architecture discovery, dependency analysis, call-flow or data-flow tracing,
impact analysis, cross-layer request tracing, refactors spanning subsystems,
orienting in an unfamiliar codebase. Not for: a known function in a known file,
a trivial edit, a literal string search.

## Commands (run from the repository root)

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

## Building and refreshing

A global PreToolUse hook (`~/.claude/hooks/graphify-lazy-init.py`) initializes a
graph automatically when a broad repository search is about to run in a git repo
with roughly 50+ tracked source files or 10k+ source lines, then installs
Graphify's incremental git hooks. It fails open and never blocks. To build by
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
| Subsystem map, hubs, dependency graph, blast radius | Graphify |
| Definition, references, implementations, diagnostics, call hierarchy | LSP (`pyright-lsp`, `typescript-lsp`) |
| Actual implementation details | targeted `Read` of the ranges Graphify/LSP pointed to |
| Literal string, config key, error message | targeted `Grep` |
| Packaging a repo for an external model or reviewer | Repomix, on demand only |
