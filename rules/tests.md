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

- Tests prove behavior at a boundary, not implementation details. Do not mock the
  unit under test; mock only what crosses a process, network, clock, or filesystem
  boundary, and only if the suite already does.
- Never weaken an assertion, delete a test, add a skip, or widen a tolerance to get
  green. A failing test is either a real defect or a wrong test; decide which with
  evidence, then fix the code or report the test as wrong.
- New behavior or a bug fix starts from a failing test
  (`superpowers:test-driven-development`); every fixed bug leaves a regression
  test. An unexpected failure goes through `superpowers:systematic-debugging`
  before any edit. Cover the important failure paths and boundaries, not just the
  happy path. Coverage is an indicator, never the objective; no filler tests.
- Use the repository's existing runner. Defaults for new work: pytest (+
  `pytest-cov` when coverage is wanted); Vitest + React Testing Library for
  unit/component tests in Vite-based frontends; Playwright for the few E2E flows
  that matter. Never run Jest and Vitest for the same responsibility.
- Iterate on the smallest relevant selection (`pytest path::test -q`, a single
  spec file); run the full relevant suite before claiming completion. Route a large suite
  through `~/.claude/bin/run-captured -- <cmd>`; when it fails, rerun only the
  failing tests with full tracebacks (`pytest --lf --tb=long`, one Vitest/Jest
  file or `-t <name>`, `go test -run`, `cargo test <name>`). Keep runner
  output compact (`-q -ra --tb=short`, quiet reporters) but never below the level
  that shows every failing test name and its assertion.
- Tests are deterministic: no wall-clock sleeps, real time, network, or ordering
  assumptions unless the existing suite has an established pattern for them.
