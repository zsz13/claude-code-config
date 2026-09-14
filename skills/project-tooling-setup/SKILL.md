---
name: project-tooling-setup
description: Set up or complete a repository's quality toolchain - Python (uv, Ruff, Pyright, pytest) or TypeScript/React (ESLint typed linting, Prettier, tsc, Vitest, Playwright) - plus pre-commit, pre-push, and CI gates. Use when creating a project, when a repo lacks lint/format/type/test/pre-commit pieces, or when asked to add quality gates.
---

# Project tooling setup

Policy lives in `~/.claude/rules/tooling.md`; this skill is the procedure and the
templates. Templates are starting points: adapt them to the repository, never
paste them over an existing configuration.

## 0. Inspect first (existing repository)

Record before changing: runtime pin (`.python-version`, `requires-python`,
`.nvmrc`, `engines`), package manager and lockfile, formatter, linter, type
checker, test runner, CI workflow, git hooks (`.pre-commit-config.yaml`, husky,
lefthook, `.git/hooks`), and the commands the README or CI actually run. A working
intentional choice is not a gap. List the genuine gaps, then fill only those.

## 1. Versions (new project or deliberate upgrade)

Check *now*, do not recall: `uv python list` for available CPython releases;
Node's release schedule for the current LTS line; the framework's own release
notes. Choose the newest production-ready stable: Python's newest stable minor
whose key dependencies publish wheels (fall back one minor only for a concrete
incompatibility); Node's newest LTS; current stable React/TypeScript. Never
pre-release, never EOL. Applications pin a narrow modern range; libraries pick a
range from consumer compatibility.

## 2. Python (uv + Ruff + Pyright + pytest)

```
uv init --app <name>   # or --lib; or `uv init` in the existing directory
uv python pin <minor>  # writes .python-version
uv add <runtime deps>
uv add --dev ruff pyright pytest pytest-cov   # + pytest-asyncio if async
uv sync                # creates uv.lock and .venv
```

`pyproject.toml` additions (adapt `target-version` and `requires-python` to the
pinned minor):

```toml
[tool.ruff]
line-length = 100
target-version = "py3XX"

[tool.ruff.lint]
select = [
  "E", "W", "F",          # pycodestyle, pyflakes
  "I",                    # isort
  "UP",                   # pyupgrade (modernization)
  "B",                    # bugbear
  "C4", "SIM", "PIE",     # comprehensions, simplify, misc anti-patterns
  "RET", "RSE", "TRY",    # returns, raises, exception handling
  "ASYNC",                # async correctness
  "S",                    # bandit security (fast local feedback only)
  "PERF", "FURB",         # performance, modernization
  "PTH",                  # pathlib
  "ARG", "PL",            # unused args, selected pylint
  "RUF", "TCH", "TID",    # ruff-specific, type-checking imports, tidy imports
  "ANN",                  # annotations on public API (pair with per-file ignores)
]
ignore = [
  "E501",                 # formatter owns line length
  "COM812", "ISC001",     # conflict with the formatter
  "PLR0913", "PLR2004",   # arg count / magic numbers: noise in most code
  "TRY003", "EM101", "EM102",
  "ANN401",               # Any is sometimes the honest type; justify per site instead
]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN", "ARG", "PLR2004"]
"**/migrations/**" = ["E", "F", "I", "UP"]

[tool.ruff.lint.isort]
known-first-party = ["<package>"]

[tool.pyright]
pythonVersion = "3.XX"
venvPath = "."
venv = ".venv"
typeCheckingMode = "standard"   # "strict" for new, fully typed code; tighten legacy code per module via `strict = [...]`
reportMissingTypeStubs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q -ra --tb=short"
xfail_strict = true
# asyncio_mode = "auto"   # with pytest-asyncio
```

Trim the `select` list for an existing codebase to what it can adopt now; grow it
per rule family, fixing as you go. No Black, isort, Flake8, or mypy alongside.
`pip-audit` (installed globally) or `uv pip audit` equivalents belong in CI or
pre-push, not on every commit.

## 3. TypeScript / React (ESLint + Prettier + tsc + Vitest)

Use the repository's package manager; pnpm for new projects without constraints.

```
pnpm add -D eslint @eslint/js typescript-eslint eslint-plugin-react-hooks \
  eslint-plugin-jsx-a11y eslint-config-prettier prettier \
  vitest @testing-library/react @testing-library/jest-dom jsdom   # + @playwright/test for E2E
```

`eslint.config.js` (flat config):

```js
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import jsxA11y from "eslint-plugin-jsx-a11y";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  { ignores: ["dist", "build", "coverage", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,   // strictTypeChecked for greenfield when low-noise
  ...tseslint.configs.stylisticTypeChecked,
  reactHooks.configs.flat.recommended,          // includes compiler diagnostics in current versions
  jsxA11y.flatConfigs.recommended,              // user-facing apps
  {
    languageOptions: { parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname } },
  },
  { files: ["**/*.{js,mjs,cjs}"], ...tseslint.configs.disableTypeChecked },
  prettier,                                     // last: turns off formatting rules
);
```

`.prettierrc` stays minimal (`{ "printWidth": 100 }` or nothing). `tsconfig`:
`strict: true`, `noUncheckedIndexedAccess: true`, `noUnusedLocals`,
`noUnusedParameters`, `noFallthroughCasesInSwitch`, `isolatedModules`,
`verbatimModuleSyntax` where the bundler supports it. Scripts:

```json
"lint": "eslint .", "format": "prettier --write .", "format:check": "prettier --check .",
"typecheck": "tsc -b --noEmit", "test": "vitest run", "test:e2e": "playwright test"
```

Formatting belongs to Prettier only; do not add stylistic ESLint plugins. Biome
is acceptable as the single lint+format owner in a repository that chose it.

## 4. Git quality gates

`.pre-commit-config.yaml`: staged files at commit, expensive checks at push.

```yaml
default_install_hook_types: [pre-commit, pre-push]
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: <current tag>
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  # Python
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: <current tag>
    hooks:
      - id: ruff-check
        args: [--fix]          # safe fixes only
      - id: ruff-format
  - repo: local
    hooks:
      - id: pyright
        name: pyright
        entry: uv run pyright
        language: system
        pass_filenames: false
        stages: [pre-push]
      - id: pytest
        name: pytest
        entry: uv run pytest -q -x
        language: system
        pass_filenames: false
        stages: [pre-push]
  # Frontend (adapt the package-manager prefix)
  - repo: local
    hooks:
      - id: prettier
        name: prettier
        entry: pnpm exec prettier --write
        language: system
        types_or: [ts, tsx, javascript, jsx, json, css, markdown, yaml]
      - id: eslint
        name: eslint
        entry: pnpm exec eslint --fix --max-warnings=0
        language: system
        types_or: [ts, tsx, javascript, jsx]
      - id: typecheck
        name: tsc
        entry: pnpm run typecheck
        language: system
        pass_filenames: false
        stages: [pre-push]
```

Resolve `<current tag>` with `pre-commit autoupdate` right after writing the file.
Then, once: `pre-commit install` and `pre-commit run --all-files`; fix or stage
what it changes, rerun until clean. Ordinary commits run only on staged files.
Husky/lefthook already present: extend them instead of adding pre-commit.

## 5. CI is the authoritative gate

Add or extend the workflow so it runs on a clean checkout: format check, full
lint, type check, tests, build, and the deterministic dependency audit
(`pip-audit`, `pnpm audit --prod` or the repo's equivalent). Local hooks are
feedback, not a boundary. Use the `infrastructure-quality` skill for the workflow
file itself (permissions, pinned actions).

## 6. Hand-off

Run the actual gates once (`ruff format --check && ruff check && pyright &&
pytest`, or the frontend scripts), report the counts of remaining findings, and
do not silence them to get green. Route the change through `adversarial-jury` if
it touched more than configuration.
