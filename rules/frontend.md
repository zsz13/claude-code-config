---
paths:
  - "**/*.{tsx,jsx,vue,svelte,astro}"
  - "**/*.{css,scss,sass,less}"
  - "**/*.html"
  - "**/tailwind.config.*"
---

# Frontend

- For UI work beyond a small fix, use the `frontend-quality` skill: it picks the
  route, decides when research and `design-brief` run (including in an
  established design system), and requires a real browser render. Source code is
  not visual evidence; a screenshot is.
- Preserve an existing design system. Match its tokens, primitives, spacing, and
  interaction patterns; consistency outranks novelty in an established product.
  `frontend-quality`'s "Research" says when a request opens any of that up.
- There is no global house style, only a default register. A product's
  direction comes from `design-brief` and `frontend-design`, in the order
  `frontend-quality`'s routes give. Where substantial work leaves the visual
  register open, the owner's default taste is expressive but controlled
  (`design-brief` step 2); a small fix never changes the register. Where
  `frontend-quality`'s "Direction gate" applies, production UI code waits for
  that gate. Wherever the pre-build check runs (same section), no product UI
  file is written before this task's `.design/prebuild.md` exists.
- Accessibility is part of done: semantic elements, labelled controls, keyboard
  operation, visible focus, contrast, and no status conveyed by color alone.
  Keep `eslint-plugin-jsx-a11y` (or the framework equivalent) enabled in
  user-facing apps.
- React: follow the Rules of React and Rules of Hooks (official
  `eslint-plugin-react-hooks` recommended config, which includes the compiler
  diagnostics). Pure components, immutable props and state, correct effect
  dependencies, error boundaries around risky subtrees, predictable state
  ownership, Strict Mode where the architecture allows. No memoization by habit:
  measure or let the compiler handle it. No legacy APIs (class components for new
  code, legacy context, string refs, `findDOMNode`) when a modern one exists.
