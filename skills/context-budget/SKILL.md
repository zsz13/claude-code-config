---
name: context-budget
description: Keep Bash and Read results out of the main context without losing information. Reference for the run-captured helper (large command output kept on disk, summary in context), progressive search narrowing, source read ranges, two-pass tests, git diff/log strategy, log and structured-data inspection, judge evidence packets, and phase-boundary checkpoints (/compact vs fresh session). Use before running tests, builds, logs, plans, or diffs expected to be large, before a broad repository search, when a failure summary is not enough to diagnose, and at major phase boundaries of long tasks.
---

# Context budget

Principle: change what enters the main context first and when detail is loaded;
never make relevant information unreachable. Correctness, debugging ability,
security, and verification outrank token savings. The harness cannot rewrite
tool results, so this is executed by choosing the right command and read.

## 1. Large command output: `run-captured`

```
~/.claude/bin/run-captured [--label NAME] [--tail N] [--max-diag N] [--match REGEX]... -- CMD ARGS...
~/.claude/bin/run-captured 'shell pipeline as one string'      # runs via bash -c
~/.claude/bin/run-captured --list [N]                          # recent captures
```

What it does: runs the command unchanged (stdin inherited, no pipefail, no env
edits), streams stdout+stderr in order to
`~/.cache/claude-hooks/captures/<stamp>-<label>-<pid>.log`
(override with `--dir` or `$CLAUDE_CAPTURE_DIR`), exits with the command's own
status, and prints: the command, `exit=<code> ok|FAILED`, duration, size, the
capture path, distinct error/warning/traceback/summary lines with `L<n>` line
numbers (`[+k similar]` for repeats after number-normalisation), and the tail
(12 lines on success, 40 on failure; a failure with no pattern match also shows
the first 20 lines). Lines naming individual tests are never folded together.
Output of at most 60 lines and 6 KB is printed verbatim, so an unexpectedly
small result costs nothing extra. Options are recognised only before the
command, so the command's own flags (`docker logs --tail 200`) are untouched. Captures older
than 7 days are removed on the next run; `ledger.tsv` in the capture directory
records bytes captured versus bytes surfaced per run (evidence for `/context`).

Use it for: test suites, builds, type check and lint on a dirty tree, docker
build, package installs, terraform/tofu plan, dependency trees, long scripts.
Do not use it for: tiny commands, anything interactive (prompts, passwords,
TUIs), or long-running servers (use the Bash tool's background mode).

Drilling into a capture: `grep -n '<pattern>' <full>`; `sed -n 'A,Bp' <full>`
around an `L<n>` reference; `grep -c` to size a class of errors before reading
them. The capture is the diagnostic source of truth until the task is resolved.

The harness independently saves any single Bash result above ~30k characters to
a file and shows a preview plus the path; treat that path the same way.

## 2. Failure evidence checklist

A failed command is never over-compressed. Keep in context: exact command, exit
status, every distinct error category, failing test or check names, file:line,
the traceback section that matters, important warnings, surrounding lines
needed to understand it. Repeated errors: representative examples plus counts,
then verify that look-alike errors share a root cause (open two or three from
the capture) before fixing them as one.

## 3. Two-pass tests (repository-native options)

| Runner | Quiet full pass | Focused diagnosis pass |
|---|---|---|
| pytest | `-q -ra --tb=short` | `--lf --tb=long` or `path::test -x` |
| Vitest | `--reporter=dot` (or `--silent`) | one file, `-t "<name>"` |
| Jest | `--silent` / `--reporters=summary` | one file, `-t "<name>"` |
| go test | `./...` (quiet by default) | `-run '<Name>' -v ./pkg` |
| cargo test | default | `<name> -- --nocapture` |
| Playwright | `--reporter=line` | `--grep "<title>"`, `--trace on` |

Wrap the quiet full pass in `run-captured` when the suite is large; the
focused pass is small enough to read directly.

## 4. Search: progressive narrowing

1. Known symbol: LSP definition/references. Subsystem or flow question:
   `graphify query|explain|affected|path` when `graphify-out/graph.json` exists.
2. Pattern that may match widely: `rg -c <pat>` or `rg -l <pat>` first (shape and
   file list), scoped by type/path (`-t py`, `-g 'src/**'`, `-g '!**/tests/**'`).
3. `rg -n <pat> <relevant files>` for the actual matches; widen when evidence is
   insufficient.
4. Never `| head` a search. If a result is limited on purpose, keep the total
   count and file list in context and state that not every match was loaded.

## 5. Source reads

- Locate first (LSP, `grep -n`, Graphify `loc=L<n>`), then read the range with
  its enclosing function/class, the imports and types it depends on, and the
  control flow around it. Expand when the fragment does not answer the question;
  do not keep reasoning from a fragment that is too small.
- Whole-file reads are right when the file is small, when global structure or
  cross-section interactions matter (configs, small modules), when a refactor
  touches most of it, or when a safe change cannot be made from parts.
- Re-reads: a hook flags a read of an unchanged file already read this session.
  After an edit, inspect the changed region or `git diff -- <file>`.

## 6. Git, logs, structured data, filesystem

- Diff: `git status --short` -> `git diff --stat` (or `--name-status`) -> `git diff
  -- <path>`. Complete diff only for cross-file review; split it by file or
  subsystem when too large. A reviewer's packet must list every changed file
  (`git diff --name-status BASE..HEAD`) and contain every semantically relevant
  change, split across judges or subagents if needed, never dropped.
- Log: `git log --oneline -n 20 [-- <path>] [--grep=<text>] [--author=<x>]`,
  then `git show <sha>` for the commits that matter.
- Logs: `grep -nE 'error|warn|<request-id>'` or `--since` windows first, then
  expand around matches (`sed -n`, `grep -C`). `tail` alone can miss an earlier
  failure. Timestamp/request-id correlation beats reading everything.
- JSON/YAML: `jq '.path | keys'`, `jq -c '.items[] | {id, status}'`, `yq`,
  `kubectl get -o jsonpath`, `terraform show -json | jq`; open the whole document
  only when its shape is unknown or the whole thing is the subject.
- Filesystem: `git ls-files [dir]`, Glob, `ls <dir>`, `tree -L 2 -I
  'node_modules|.venv|dist|build|.git'`; never dump the tree recursively.

## 7. Subagents and judges

Delegate when the intermediate output would pollute the main context (log or
test-output analysis, broad inventory), never to save a single small read. A
judge packet (see `adversarial-jury`) gets the smallest complete evidence:
requirement, base/head, changed-file manifest, targeted diffs covering every
relevant change, deterministic results; no conversation history.

## 8. Phase boundaries and long sessions

At a major independently verifiable phase (backend green, frontend green,
browser verification done, implementation done before review) write a
checkpoint in the conversation:

```
Checkpoint <phase>
Objective: ...
Done: ...
Changed: <files/subsystems>; migrations: <ids or none>
Gates passing: <tests/lint/types/build with counts>
Unresolved: ...
Next: ...
```

Then, if the context is already very large (about 150k+): `/compact` when the
conversational detail still matters for the next phase; otherwise recommend a
fresh `claude` session with the checkpoint as the continuation prompt (repo and
test state reconstruct the rest). `/clear` mid-task only with a durable
checkpoint; `/clear` is right when an unrelated task starts in the same
process; a new `claude` process needs no `/clear`. Do not repeat this advice
on small tasks.

## 9. Measuring

After a representative long task: `/context` (Bash result tokens, Read result
tokens, MCP and subagent share, cache hit rate) and `/usage`; compare with the
capture ledger (`~/.cache/claude-hooks/captures/ledger.tsv`). Claim savings only
from these numbers.
