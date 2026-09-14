---
paths:
  - "**/*.{ts,tsx,mts,cts}"
  - "**/*.{js,jsx,mjs,cjs}"
---

# TypeScript / JavaScript

Tool ownership, one owner each: the repository's **package manager** (dependencies
and the single lockfile), **ESLint + typescript-eslint + framework plugins**
(semantic linting), **Prettier** (formatting), **tsc** (type checking), one test
runner. Biome may own lint+format in a repository that chose it; never stack it
with ESLint and Prettier for the same job. See `~/.claude/rules/tooling.md`.

- Use the project's `package.json` scripts, `tsconfig.json`, and lint/format config.
  Detect the package manager from the lockfile and use only that one; never create
  a second lockfile or switch managers in an established repository.
- The `typescript-lsp` plugin is available: use its diagnostics and
  definition/reference navigation before searching or reading widely. Type checking
  and linting are separate gates: run `tsc --noEmit` (or the project's `typecheck`
  script) even when typed ESLint rules are on.
- New substantial React or Node code in a TypeScript repository is TypeScript.
  Do not convert a mature JavaScript codebase for fashion.
- No `any`, `@ts-ignore`, `@ts-expect-error`, or non-null `!` to make an error go
  away without a one-line reason. Prefer `unknown` plus narrowing, inference where
  it is clear, explicit types at module and API boundaries, and deliberately
  modelled API response types.
- Formatting is Prettier's job. Do not add ESLint style rules that overlap it, and
  do not hand-format. Apply only ESLint fixes that preserve semantics; fix the
  rest deliberately. Do not disable a rule to get green; a disable comment is
  narrow and justified.
- Match the module system (ESM/CJS), import style, and async conventions already
  in use. Handle promise rejections; no floating promises.
- Do not add a dependency for something the standard library or an existing
  dependency already does.
