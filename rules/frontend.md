---
paths:
  - "**/*.{tsx,jsx,vue,svelte,astro}"
  - "**/*.{css,scss,sass,less}"
  - "**/*.html"
  - "**/tailwind.config.*"
---

# Frontend

- For UI work beyond a trivial fix, use the `frontend-quality` skill: it scales
  the process to the change and requires a real browser render. Source code is not
  visual evidence; a screenshot is.
- Preserve an existing design system. Match its tokens, primitives, spacing, and
  interaction patterns; consistency outranks novelty in an established product.
- Substantial frontend work, as `frontend-quality` defines it, gets a
  product-specific direction first through that skill's route (research,
  `design-brief`, then `frontend-design`). There is no global house style.
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
