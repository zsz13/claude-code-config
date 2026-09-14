---
paths:
  - "**/pyproject.toml"
  - "**/ruff.toml"
  - "**/.ruff.toml"
  - "**/pyrightconfig.json"
  - "**/mypy.ini"
  - "**/setup.cfg"
  - "**/tox.ini"
  - "**/noxfile.py"
  - "**/.python-version"
  - "**/uv.lock"
  - "**/poetry.lock"
  - "**/requirements*.txt"
  - "**/package.json"
  - "**/pnpm-lock.yaml"
  - "**/package-lock.json"
  - "**/yarn.lock"
  - "**/bun.lock*"
  - "**/tsconfig*.json"
  - "**/eslint.config.*"
  - "**/.eslintrc*"
  - "**/.prettierrc*"
  - "**/prettier.config.*"
  - "**/biome.json*"
  - "**/.pre-commit-config.yaml"
  - "**/.nvmrc"
  - "**/.node-version"
  - "**/.tool-versions"
  - "**/renovate.json*"
  - "**/.github/dependabot.yml"
---

# Tooling, versions, and quality gates

Detailed templates and the new-project checklist live in the
`project-tooling-setup` skill; upgrade and audit workflows in
`dependency-modernization`. This rule is the policy.

**Smallest non-overlapping toolset.** One owner per job. Never introduce: Black,
isort, or Flake8 beside Ruff; mypy beside Pyright (or the reverse) without a
concrete need; Pylint for rules Ruff already covers; Prettier beside Biome's
formatter; Jest beside Vitest for the same tests; a second package manager or
lockfile. If an existing repo has an overlap, name it and propose removing the
redundant half; do not add to it.

**Existing repository: inspect, then preserve intentional choices.** Read the
runtime pin, formatter, linter, type checker, package manager, CI, and git hooks
before changing anything. Poetry, PDM, mypy, Jest, npm, or Biome that work are not
gaps. Modernize only where the benefit exceeds migration risk, and never as a
side effect of an unrelated task; flag EOL runtimes and unmaintained dependencies
instead of silently migrating.

**Versions are chosen at project creation or deliberate upgrade, never from
habit.** Check the current stable/LTS status at that moment (`uv python list`,
Node release schedule, the framework's release notes; endoflife.date). Prefer the
newest production-ready stable release the ecosystem supports: Python's newest
stable minor whose dependencies have wheels; Node's newest LTS, not Current;
current stable React and TypeScript. Never a beta, RC, nightly, or EOL release
for production. No permanent version pins live in global config.

**Dependencies.** Current stable, compatible, maintained, and necessary; prefer
the standard library or an existing dependency when sufficient. Deterministic
lockfiles regenerated only by the package manager. Patch and minor upgrades may
be proactive when compatible; major upgrades are migrations with changelog review,
tests, and validation. One dependency-update bot (Dependabot or Renovate), not two.

**pre-commit runs on staged files.** Do not configure or run
`pre-commit run --all-files` on ordinary commits; use it when pre-commit is first
introduced, after configuration changes, for explicit full validation, before a
release, in CI, or after a repository-wide change. Commit-stage hooks are fast
and apply only safe deterministic fixes (Ruff format and safe fixes, Prettier,
whitespace/EOF). Push-stage hooks carry the expensive checks: full type check,
full lint, important tests, build. If a hook modifies files: inspect, stage,
rerun, and commit only after a clean pass.

**Ruff configuration.** Central in `pyproject.toml`; a curated set (correctness,
bugs, imports, modernization, security, async, exceptions, typing, performance,
anti-patterns) rather than `ALL`; disable rules that fight the formatter
(`COM812`, `ISC001`, `E501` when the formatter owns line length); no unsafe fixes
by default.

**ESLint configuration.** Flat config, current stable ESLint, typescript-eslint
with at least `recommendedTypeChecked` (stricter presets when they stay
low-noise), `eslint-plugin-react-hooks` recommended, `jsx-a11y` for user-facing
apps, `eslint-config-prettier` to hand formatting to Prettier. Run `tsc --noEmit`
as its own gate.
