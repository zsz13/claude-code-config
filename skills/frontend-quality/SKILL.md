---
name: frontend-quality
description: Routes frontend work by scope and verifies the rendered result in a real browser. Use for any UI change beyond a small fix, and before planning or building substantial frontend work - a new frontend or product, a landing or multi-section marketing page, a dashboard, an ecommerce, catalog or listing page, a new screen, a major redesign, building or restructuring a component system, or a significant UX restructuring - including when only a plan, an outline, or advice on what it should contain is asked for. Not for a small fix or a question about existing code.
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

Never call UI work done without a render you actually looked at.

## Route by scope

Pick the route before planning, not only before building. A request for a plan,
an outline, or advice on what a page should contain takes the route of the work
it plans, up to the plan: research and direction come first, because the plan is
where the structure gets decided. A question about existing code, or a plan for
a small fix, takes the small-fix route.

**Substantial frontend work** is defined here once: a new frontend or product; a
landing or multi-section marketing page; a dashboard; an ecommerce, catalog or
listing page; a new screen; a major redesign; building or restructuring a
component system; or a significant UX restructuring. This skill's description
repeats the list because the description decides whether the skill loads; change
the two together. Every other rule here, in `design-brief` and in
`rules/frontend.md` refers to this definition. Work inside an existing product
takes "New screen or major redesign"; a new product, a landing page or a
component system takes the last route.

**Small UI fix** (spacing or alignment, a color or other token, a copy string,
one broken style, a small bug fix)
→ read the surrounding design, change minimally, one browser check at the
affected viewport. **Do not redesign.** Do not run the review stages or
research.

**New component**
→ find the existing design system and its tokens → build from existing primitives
→ render → check states and both primary viewports.

**New screen or major redesign**
→ `design-brief` if no design system exists, or if "Research" says research runs
→ research (see "Research")
→ `frontend-design` for the aesthetic work
→ compact visual plan → implement → render
→ screenshots at ~375px and ~1280px → `visual-design-judge`
→ UX and accessibility pass → fix what matters → **render again**.

**New product, landing page or component system**
→ `design-brief`
→ establish real content first (for a component system, the screens it serves)
→ research (see "Research"), unless references were given
→ product-specific direction
→ define tokens → `frontend-design` → build → browser iteration
→ `visual-design-judge` → UX and accessibility pass → final responsive check.

Scale the process to the change. Running a five-stage review on a padding fix
wastes context and buries real findings.

## Research

Study how others solved the hard parts before a plan is final.

- **Substantial frontend work:** research is a step, not an option, with one
  exception. In a product with an established design system it runs only when
  the page's structure, an interaction pattern, or the visual direction is
  genuinely open or new; a screen built from the system's existing patterns
  matches the system and gets no outside research. When it does run there, it
  informs structure and behavior, and style only when the visual direction
  itself is what is open. This is the one statement of that rule; `design-brief`
  refers to it.
- **New component outside that work:** only when its behavior is the hard part
  (a command palette, a data table, a dialog).
- **Small UI fix, or a question about existing code:** never.

Use every source that is connected; none waits on another:

- **Screen references:** `design-brief` step 3 (Refero first, then Mobbin).
- **Components (21st.dev):** when `mcp__21st__*` tools are listed (they are
  deferred: load them with ToolSearch, e.g.
  `select:mcp__21st__get_inspiration,mcp__21st__search`), run `get_inspiration`
  once for the product (not for a component system) and `search` for the two to
  four sections or components whose composition or behavior is the hard part
  (hero, gallery, filtering, navigation, detail view, data table). Compare
  several results and keep only what fits the direction. "Component libraries"
  says what may be taken from them.
- **None connected:** do not skip the phase and do not fall back to defaults.
  For substantial work, write `design-brief`'s internal art direction (step 3)
  and state it before the plan. For a new component, build from the system's
  primitives and say that no research tool was available.

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

Minimum for anything beyond a small fix: **~375px (mobile)** and **~1280px
(desktop)**.
Add **~768px (tablet)** and **1440–1600px+ (wide)** when the layout has
breakpoints there or the content is dense.

At each, check: overflow, clipping, wrapping, hierarchy, whitespace, density,
sticky/fixed elements, navigation, tap targets, responsive reflow, text measure,
and content ordering. At the narrow viewport every destination the desktop
navigation offers must still be reachable; hiding the links is not a mobile nav.

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
(shadcn's in a shadcn project, 21st.dev's), or a community snippet. When to
search one is under "Research". Use search and source tools, never a hosted
generator. `get_component` returns React + Tailwind source and, on the free
tier, spends one of two daily retrievals: fetch code only in such a project, and
only for a component you will actually adapt. Add a component to the project
only when this work needs it.
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
