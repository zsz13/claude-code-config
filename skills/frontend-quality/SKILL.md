---
name: frontend-quality
description: Routes frontend work by scope and verifies the rendered result in a real browser. Use for UI changes beyond a trivial fix, and whenever visual quality or responsive behavior matters.
---

# Frontend quality

Routing and verification for frontend work. This skill does **not** teach design —
the `frontend-design` skill owns aesthetics and `design-brief` owns product
direction. This one decides how much process a change deserves, and enforces that
the result was actually looked at.

## The rule this exists to enforce

```
write JSX/CSS -> read the source -> declare it polished
```

is not verification. Source-code aesthetics are not evidence. A screenshot is.

```
PLAN -> BUILD -> RENDER -> LOOK -> CRITIQUE -> FIX -> RENDER AGAIN
```

Never call substantial UI work done without a render you actually looked at.

## Route by scope

**Small UI fix** (spacing, a color token, a copy string, one broken style)
→ read the surrounding design, change minimally, one browser check at the
affected viewport. **Do not redesign.** Do not run the review stages.

**New component**
→ find the existing design system and its tokens → build from existing primitives
→ render → check states and both primary viewports.

**New screen or major redesign**
→ `design-brief` if no system exists or the direction is genuinely open
→ if the screen's structure is open, invoke `design-brief` for its reference
  research (step 3), even in an established system
→ `frontend-design` for the aesthetic work
→ compact visual plan → implement → render
→ screenshots at ~375px and ~1280px → `visual-design-judge`
→ UX and accessibility pass → fix what matters → **render again**.

**New product or landing page**
→ `design-brief`, with its reference research unless references were given
→ establish real content first
→ product-specific direction
→ define tokens → `frontend-design` → build → browser iteration
→ `visual-design-judge` → UX and accessibility pass → final responsive check.

Scale the process to the change. Running a five-stage review on a padding fix
wastes context and buries real findings.

## Render it

Use the Playwright MCP browser (`mcp__plugin_playwright_playwright__*`).

1. Start the app with its **real documented dev command** — from the README,
   `package.json` scripts, Makefile, or Taskfile. Do not invent one.
2. Navigate to the affected route.
3. `browser_snapshot` for the DOM/accessibility tree where structure matters.
4. `browser_resize` + `browser_take_screenshot` per viewport.
5. Look at the screenshots. Critique. Fix. Render again.

Screenshots land in the MCP's output directory, `.playwright-mcp/` under the
workspace root by default. Current versions refuse paths outside the workspace,
so do not pass a temp path. That directory is not product source: keep it out of
commits (`.git/info/exclude` if the project does not already ignore it), and
never write screenshots into product source folders unless the repository
intentionally keeps visual snapshots under version control.

## Viewports

Minimum for substantial UI work: **~375px (mobile)** and **~1280px (desktop)**.
Add **~768px (tablet)** and **1440–1600px+ (wide)** when the layout has
breakpoints there or the content is dense.

At each, check: overflow, clipping, wrapping, hierarchy, whitespace, density,
sticky/fixed elements, navigation, tap targets, responsive reflow, text measure,
and content ordering.

A UI that only holds up at one viewport is not done. These are *review*
viewports — do not hardcode them into product CSS.

## Real content, not filler

Use realistic product-specific content from the first render. Copy is part of the
visual system, and filler makes a design look templated no matter how it is set.

Avoid: "Welcome to our platform", "Unlock your potential", "Transform your
workflow", lorem ipsum, invented metrics with no relationship to the product,
and generic testimonial cards.

- Buttons name the actual action, not "Submit" / "Continue" by default.
- Errors say what happened and offer a recovery path.
- Empty states help the user take the next step.

## Accessibility floor

Not optional, not decorative. For meaningful interactive UI, verify what applies:

semantic HTML · accessible names · full keyboard operation · **visible** focus ·
sensible focus order · labelled form controls · errors associated with their
inputs · contrast · touch-target size · `prefers-reduced-motion` respected ·
status never conveyed by color alone · zoom not disabled · text and inputs that
survive reflow.

Tab-walk the page in the browser and watch the focus ring — that is the check,
not a source read. If the project already has axe-core or another a11y suite,
**reuse it**. Recommend adding one at project scope where it earns its place;
never install a11y tooling globally on spec.

For a fuller UX pass, fetch the current guidelines rather than relying on a cached
copy — they change:
`WebFetch https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/AGENTS.md`
Treat its framework-independent guidance (keyboard, focus, touch targets,
responsive behavior, content states, forms, animation, performance) as the useful
part, and its copywriting and branding preferences as Vercel-specific, not law.

## Motion

Motion needs a job: hierarchy, continuity, spatial relationship, feedback, or one
deliberate memorable moment. One orchestrated transition beats twenty unrelated
micro-animations.

Avoid every-element fade-up, animation on every card, parallax for its own sake,
springs with no reason, and animation that exists because a library is installed.
Prefer transform and opacity. Honor `prefers-reduced-motion`.

Reach for Motion (`motion/react`) only for what the platform does not do
cleanly: layout and shared-element transitions across re-renders, exit
choreography, drag and gesture physics, interruptible springs. Adding it is a
project decision, not a side effect of one component. Where it is already a
dependency, check its current API at motion.dev/docs; it changes between majors,
and memory lags.

## Component libraries

Respect the existing stack. Do not mandate shadcn/ui, MUI, Chakra, Tailwind, or
anything else globally.

If the project uses shadcn/ui, its components are **implementation
infrastructure, not art direction** — use them for behavior and accessibility,
then customize tokens and composition so the product does not look like every
other shadcn app. Preserve the accessibility behavior you inherit.

The same holds for any component source: a registry, a component-search MCP
(shadcn's in a shadcn project, 21st.dev's in a React and Tailwind one), or a
community snippet. Look there when a specific element is the hard part: its
behavior (a command palette, a data table, a dialog) or its composition (a
pricing section, a hero, a card). Use search and source tools, never a hosted
generator, and add a component to the project only when this work needs it.
Keep the behavior and accessibility, and restyle it to the project's tokens,
type roles, spacing, radius, density, and interaction model. A demo's palette,
radius, or type never becomes the product's; its composition is a reference to
adapt, not a layout to paste.

## Performance

Visual polish does not license a slow page. Watch for oversized images,
unnecessary animation libraries, layout thrashing, excessive client JS, and
decorative canvas/WebGL the design does not require. Prefer CSS and platform
capability when it achieves the design cleanly.

## Review integration

Frontend review is split on purpose:

- **`visual-design-judge`** — rendered visual quality. Give it the product
  context, the brief or the established design system, what data the product
  already holds for these screens, the routes, and the screenshots. Withhold
  your reasoning and your confidence, as with any judge.
- **Engineering judges** (`adversarial-jury`) — correctness, tests, types,
  runtime behavior. Add `security-judge` or `architecture-judge` only if the
  change actually touches those.

Do not ask five engineering judges to vote on whether a page is beautiful, and do
not ask the visual judge about test coverage.

## Established products

In a mature product, infer and match the existing tokens, spacing, typography,
primitives, radii, shadows, color usage, and interaction patterns. Consistency
outranks novelty here. Distinctiveness is the goal for greenfield and redesign
work — not for a new button in a product that already has one.
