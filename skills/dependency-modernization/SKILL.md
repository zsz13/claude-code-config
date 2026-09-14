---
name: dependency-modernization
description: Audit and upgrade a repository's runtime, dependencies, and toolchain safely - detect EOL or unmaintained pieces, plan patch/minor vs major upgrades, run deterministic vulnerability checks, and validate migrations. Use when asked to upgrade, modernize, audit dependencies, or when an old runtime or library is noticed during other work.
---

# Dependency and runtime modernization

Notice obsolescence during any task; *act* on it only when the task authorizes
it or the upgrade is clearly in scope. Otherwise report it with impact and stop.

## 1. Inventory (read-only)

- Runtime: `.python-version` / `requires-python` / `.nvmrc` / `engines`; compare
  with current support windows (`uv python list`, Node release schedule,
  endoflife.date). Mark EOL and soon-EOL.
- Dependency manager and lockfile; whether the lockfile is committed and in sync
  (`uv lock --check`, `pnpm install --frozen-lockfile`, `npm ci`).
- Outdated packages: `uv tree --outdated` / `uv pip list --outdated`,
  `pnpm outdated`, `npm outdated`. Separate patch, minor, major.
- Maintenance status of key libraries (last release, open critical issues,
  deprecation notices, successor projects, e.g. a v2 line that is EOL).
- Vulnerabilities: `pip-audit` (or `uv run pip-audit`), `pnpm audit --prod`,
  `npm audit --omit=dev`. Deterministic scanners belong in CI/pre-push/explicit
  review, not on every commit; this is not a substitute for the `security-judge`.
- Toolchain overlap (see `~/.claude/rules/tooling.md`): duplicated formatters,
  linters, type checkers, test runners, lockfiles.

Report as a short table: item, current, target, class (patch/minor/major/EOL),
risk, blocked-by.

## 2. Decide

- Patch and minor: apply when the lockfile updates cleanly and tests pass; batch
  them in one change with the audit output attached.
- Major (library, framework, runtime): a migration. Read the changelog and
  migration guide, list breaking changes touching this codebase (use Graphify
  `affected` / LSP references to find call sites), estimate scope, and get
  explicit go-ahead unless the task already is the migration.
- Runtime bump: confirm every dependency has wheels/support for the target (uv
  resolves this: `uv lock --python <ver>` or `uv python pin` + `uv sync`), CI
  images and Dockerfiles follow, and the deployment target supports it.
- Unmaintained dependency: prefer the maintained successor or the standard
  library; replacing is a major change.
- Never pre-release versions unless explicitly justified in the change.

## 3. Execute

One class per commit or PR: lockfile-only patch/minor, then each major separately.
Use the manager (`uv add pkg@latest`, `uv lock --upgrade-package pkg`,
`pnpm update --latest pkg`); never edit a lockfile by hand. Keep the old version
reachable (git) and note the rollback.

## 4. Validate

Full gate after each class: format check, lint, type check, full test suite,
build, and the dependency audit again. For a runtime bump also run under the new
interpreter/Node in CI. Deprecation warnings that appear are findings, not noise
to filter. Route framework or runtime migrations through `adversarial-jury`
(high-risk tier if they touch auth, data, or infrastructure).

## 5. Ongoing maintenance

If the repository has neither, propose Dependabot or Renovate (one, not both)
with grouped patch/minor updates and a weekly cadence; keep majors as separate
PRs. Do not add a bot to a repository that already has one.
