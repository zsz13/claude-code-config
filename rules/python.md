---
paths:
  - "**/*.py"
  - "**/*.pyi"
  - "**/pyproject.toml"
---

# Python

Tool ownership, one owner each: **uv** (interpreter, environment, dependencies,
lockfile), **Ruff** (lint and format), **Pyright** (types), **pytest** (tests).
Respect an established repository's existing choices (Poetry/PDM, mypy, Black);
see `~/.claude/rules/tooling.md` before adding or replacing any tool.

- Use the project's configured commands from `pyproject.toml`, `Makefile`, `tox`,
  `noxfile`, or CI. In a uv project run tools through `uv run`; add dependencies
  with `uv add`/`uv remove`, never by hand-editing `uv.lock` or with bare `pip install`.
- Pyright is available through the `pyright-lsp` plugin: use its diagnostics and
  definition/reference navigation instead of grepping for symbols or re-running a
  full type check after every edit. Run the project's full check once before completion.
- Ruff is the linter and formatter; do not add Black, isort, Flake8, or pycodestyle
  next to it. Apply only safe fixes (`ruff check --fix`); never `--unsafe-fixes`
  by default. Fix a remaining violation deliberately; a `# noqa` is narrow and
  carries a one-line reason.
- Types: annotate new or changed public functions and important internal
  boundaries with modern syntax (`X | None`, builtin generics, `Self`, `TypedDict`,
  `Protocol`); avoid `Any` where a precise type exists. Never add `# type: ignore`,
  `cast`, or `Any` to silence a diagnostic without a one-line reason. Do not turn on
  Pyright strict mode for an untyped legacy codebase wholesale; tighten per module.
- No bare `except:`; catch the narrowest exception that the code can handle. No
  mutable default arguments. Use context managers for files, sockets, locks, and
  database sessions. Library code logs; it does not `print`.
- Async only where I/O concurrency pays for it: network, async DB drivers,
  queues, concurrent API calls, async web frameworks. In an async application
  never block the event loop with sync I/O or CPU work; use async-native clients,
  `asyncio.TaskGroup` over bare `gather`, bounded concurrency (semaphore or a
  fixed worker count) over unbounded fan-out, timeouts and cancellation handling.
  Do not make pure or CPU-bound functions async; CPU work goes to processes or
  native code.
- Tests are pytest (see `tests.md`). Coverage is an indicator, not a target.
