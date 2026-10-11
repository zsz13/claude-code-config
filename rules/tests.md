---
paths:
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/conftest.py"
  - "**/tests/**"
  - "**/__tests__/**"
  - "**/*.{test,spec}.{ts,tsx,js,jsx,mts,cts}"
  - "**/*_test.go"
  - "**/spec/**"
  - "**/e2e/**"
  - "**/playwright.config.*"
  - "**/vitest.config.*"
  - "**/jest.config.*"
---

# Tests

Whether a change needs a test, and at which boundary, is set by "Verification
and test value" in `CLAUDE.md`. This rule covers how to write and run one.

- Assert observable behavior: what the user sees, what the API returns, what is
  persisted. Not internal calls, private state, CSS classes, component
  structure, or large snapshots.
- Do not mock the unit under test. Prefer a real seam (injected clock, temp data
  file, ephemeral port, local container) to a mock; mock only a process,
  network, clock, or filesystem boundary that cannot run locally, and only if
  the suite already does.
- One test per meaningful behavior, not per function, component or file.
  Table-driven rows beat a run of near-identical cases.
- Where a test is worth writing, write it first
  (`superpowers:test-driven-development`); every fixed bug leaves a regression
  test at the highest boundary the project already tests reliably. Cover the
  important failure paths and boundaries, not just the happy path. An
  unexpected failure goes through `superpowers:systematic-debugging` before
  any edit.
- Never weaken an assertion, rewrite an expected value, delete a test, add a
  skip, or widen a tolerance to get green. A failing test is either a real
  defect or a wrong test; decide which with evidence, then fix the code, or
  change the test only where it contradicts the requirement (a changed one
  included) and say why. Call a failure pre-existing only after reproducing it
  on an untouched baseline. Removing or replacing a low-value test is its own
  stated decision, never a way past a failure.
- Use the repository's existing runner. Defaults for new work: pytest (+
  `pytest-cov` when coverage is wanted); Vitest + React Testing Library for
  unit/component tests in Vite-based frontends; Playwright for browser flows.
  Never run Jest and Vitest for the same responsibility.
- Iterate on the smallest relevant selection (`pytest path::test -q`, a single
  spec file); run the full relevant suite before claiming completion. Route a large suite
  through `~/.claude/bin/run-captured -- <cmd>`; when it fails, rerun only the
  failing tests with full tracebacks (`pytest --lf --tb=long`, one Vitest/Jest
  file or `-t <name>`, `go test -run`, `cargo test <name>`). Keep runner
  output compact (`-q -ra --tb=short`, quiet reporters) but never below the level
  that shows every failing test name and its assertion.
- Tests are deterministic: no wall-clock sleeps, real time, network, or ordering
  assumptions unless the existing suite has an established pattern for them.
