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

Decide the route, and whether research runs, from what the user asked for and
from requirements the product already has (its brief, design system, specs),
before planning. A feature, page or interaction pattern you think of adding
while planning changes neither: offer it as optional, without research, and
research it only if the user takes it up.

**Substantial frontend work** is defined here once: a new frontend or product; a
landing or multi-section marketing page; a dashboard; an ecommerce, catalog or
listing page; a new screen; a major redesign; building or restructuring a
component system; or a significant UX restructuring. This skill's description
repeats the list because the description decides whether the skill loads; change
the two together. Every other rule here, in `design-brief` and in
`rules/frontend.md` refers to this definition. Work on a component system itself,
new or reworked, takes "Component system", which wins when a request matches
more than one route; a screen built with the system still takes the screen
route. Other work inside an existing product takes "New screen or major
redesign"; a new product or a landing page takes "New product or landing page".

**Small UI fix** (spacing or alignment, a color or other token, a copy string,
one broken style, a small bug fix)
→ read the surrounding design, change minimally, one browser check at the
affected viewport. **Do not redesign.** Do not run the review stages or
research.

**New component**
→ find the existing design system and its tokens → research only if "Research"
allows it → build from existing primitives → render → check states and both
primary viewports.

**New screen or major redesign**
→ `design-brief` if no design system exists, or if "Research" says research runs
→ research (see "Research")
→ when the direction is open, three directions and **stop** for the user's
  choice (see "Direction gate")
→ `frontend-design` for the aesthetic work
→ compact visual plan (→ pre-build AI-slop and visual-energy check, when this
  work sets a new direction)
→ implement → render
→ screenshots at ~375px and ~1280px → `visual-design-judge`
→ UX and accessibility pass → fix what matters → **render again**.

**New product or landing page**
→ `design-brief`
→ establish real content first
→ research (see "Research"), unless references were given
→ product-specific direction: when the direction is open, three directions and
  **stop** for the user's choice (see "Direction gate")
→ `frontend-design` → compact visual plan with its tokens (→ pre-build AI-slop
  and visual-energy check, when this work sets a new direction)
→ define tokens → build → browser iteration
→ `visual-design-judge` → UX and accessibility pass → final responsive check.

**Component system** (a new one, or a cleanup or rework of an existing one)
→ inventory the existing tokens and primitives and where each is used
→ `design-brief` for the system's direction when the product has no visual
  language yet, or when the request asks to change it; otherwise keep the
  existing visual language
→ research (see "Research"): only for components whose behavior is the hard
  part, and for the look when the direction is open
→ when the direction is open, three directions and **stop** for the user's
  choice (see "Direction gate"), then the pre-build AI-slop and visual-energy
  check on the plan
→ define or consolidate tokens and primitives → migrate the call sites
→ render the screens that use them at both primary viewports, before and after;
  a visual change the request did not ask for is a defect
→ `visual-design-judge` when the look was meant to change → accessibility pass.

Scale the process to the change. Running a five-stage review on a padding fix
wastes context and buries real findings.

## Research

Study how others solved the hard parts before a plan is final. This section is
the one statement of when research runs, what it may inform, and what replaces
it when no tool is connected; `design-brief` and `rules/frontend.md` refer here.
Eligibility comes from the request and the product's existing requirements,
never from what you might add while planning (see "Route by scope").

- **Substantial frontend work, no established design system:** research is a
  step, not an option. It may inform structure, behavior and style.
- **Substantial frontend work in an established design system:** research runs
  only when the request itself introduces a page structure, an interaction
  pattern, or a visual direction the product does not have. A page that shows a
  subset or another view of what the product already shows (a saved list, a
  filtered list, an account page built from existing parts) introduces none.
  When research runs here, it informs the new structure and behavior, and style
  only when the request asks for a new visual direction.
- **Component system:** only for components whose behavior is the hard part;
  no `get_inspiration`. Its look comes from `design-brief` when it has none
  yet, and changes only when the request asks for a new one. In those two
  cases the direction gate applies, and research covers the look as it would
  for a major redesign, `get_inspiration` included.
- **New component:** only when its behavior is the hard part (a command
  palette, a data table, a dialog).
- **Small UI fix, or a question about existing code:** never.

Use every source that is connected; none waits on another:

- **Screen references:** `design-brief` step 3 (Refero first, then Mobbin).
- **Components (21st.dev):** when `mcp__21st__*` tools are listed (they are
  deferred: load them with ToolSearch, e.g.
  `select:mcp__21st__get_inspiration,mcp__21st__search`), run `get_inspiration`
  once for the product (substantial work only) and `search` for the two to four
  sections or components whose composition or behavior is the hard part (hero,
  gallery, filtering, navigation, detail view, data table). Compare several
  results and keep only what fits the direction, and among those the visually
  strongest (`design-brief` step 3). "Component libraries" says what may be
  taken from them.
- **Look at the previews.** A title, tag or description is not a visual
  reference. Open a result's screenshot or preview image (save it under the
  job's or system temp directory and Read it, or open it in the browser) before
  keeping it. Keep its URL, its video URL when it has one, and the saved file,
  to show the user and to give `visual-design-judge` after the build. Never
  mock up or build alternatives to stand in for references: the shipped
  screens and component previews already show them.
- **Enough, not exhaustive:** one broad query, then focused searches for the
  visually important parts, until there is enough to support the direction (or
  the three directions of "Direction gate"). Quality of inspection beats the
  number of calls.
- **None connected:** when research would have run, do not skip it and do not
  fall back to defaults. Write `design-brief`'s internal art direction (step 3)
  and state it before the plan. It covers exactly what research could have
  informed above: structure and behavior always, style only where style is open.
  When research would not have run, there is nothing to replace; match the
  system.

## Direction gate

The one statement of when the user chooses the direction. It applies to
substantial frontend work whose **visual direction is open**: a new product or
frontend, a major redesign, or a request for a new visual direction (a
component system's included). It does not apply when the request names the
direction or its references, when an existing brief does and the request does
not ask to change it, to work that keeps an established system's look, or to
anything that is not substantial work.

```
RESEARCH -> 3 DIRECTIONS -> USER SELECTS -> PLAN
         -> PRE-BUILD AI-SLOP + VISUAL-ENERGY CHECK -> .design/prebuild.md
         -> BUILD -> RENDER -> FINAL REFERENCE-AWARE VISUAL REVIEW
```

- After research, propose exactly three directions (`design-brief` step 4):
  each scored for visual energy, density, motion and reference fidelity, no two
  at the same energy level, and at least one reference-led. Unless
  `design-brief` step 2 says the register is not open, the owner's default
  taste applies: expressive but controlled, energies 2, 3 and 4, and the
  reference-led direction at 3 or 4. Then **stop**.
  Until the user picks A, B, C or a mix ("A's composition with C's
  visual language"), write no production UI code: no components, pages,
  styles or tokens in the product. A request for a plan stops here too; the
  plan depends on the choice.
- Choose yourself only when the user said to (choose autonomously, continue
  without approval). Then take the strongest direction and record which one
  and why at the top of the plan. Under the default taste, the strongest is
  expressive but controlled, not the safest. "Build it" alone asks for the
  result, not for skipping the choice. In a run nobody can answer (headless,
  CI), the three directions are the run's output; a prompt for such a run that
  wants a build says to choose.
- After the choice, the plan turns the selected references into constraints,
  and the pre-build AI-slop and visual-energy check runs on it (`design-brief`
  step 5). A failed check revises the composition before any code is written.
  The check also runs when the request itself named the new direction or its
  references, because the user has chosen them there. Save a preview of each
  reference the user gave (their image, or a screenshot of the page), as
  research would have, for the final review.
- A selected reference with meaningful motion or motion-led interaction is
  inspected in motion (its video, live demo or source), not from its
  screenshot alone, and the plan gets its behavior note (`design-brief`
  step 5).
- The check is written to `.design/prebuild.md` (`design-brief` step 5).
  **No product UI file may be written before that file exists**, in
  autonomous and headless runs too; an announced check leaves no evidence.
- The rendered review checks drift from the chosen direction and, where it used
  references, from them; it is not where the direction gets decided.

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

Where the visual register is open (`design-brief` step 2), the default is not
a static screen. Move what changes, each motion with one of the jobs above:
state transitions, filtering and sorting, reveals, progress along a timeline,
cards that move, emphasis on what just changed, hover. Once a direction is
selected, its Motion score sets how much moves. Take the motion language from
the selected references when they have one. Under reduced motion, an instant
or cross-faded change replaces the movement; the default is still designed to
move.

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
tier, spends one of two daily retrievals: fetch code only in a React project,
and only for a component you will actually adapt. In a project without
Tailwind, do not add Tailwind for it: port its composition, behavior,
interaction logic, motion and accessibility behavior into the project's
existing styling. Add a component to the project only when this work needs it.
Keep the behavior and accessibility, and restyle it to the project's tokens,
type roles, spacing, radius, density, and interaction model, and to the chosen
direction. A demo's palette, radius, or type never becomes the product's; its
composition is a reference to adapt, not a layout to paste.

## Performance

Visual polish does not license a slow page. Watch for oversized images,
unnecessary animation libraries, layout thrashing, excessive client JS, and
decorative canvas/WebGL the design does not require. Prefer CSS and platform
capability when it achieves the design cleanly.

## Review integration

Frontend review is split on purpose:

- **`visual-design-judge`** — rendered visual quality. Give it the product
  context, the brief or the established design system, the chosen direction
  when the pre-build check ran (its scores and the product-specific decisions
  the check named), the preview images of the references it used (selected at
  the gate or given by the user), what data the product already holds for
  these screens, the routes, and the final screenshots. Withhold your reasoning
  and your confidence, as with any judge.

  For a reference-led direction, add its Adapts entries and the changes made
  on purpose, each with its reason (decisions, like the direction), but not
  your own verdict on what was preserved or lost. For a motion-led reference,
  add its behavior note and frames, and the build's same behavior captured as
  frames at ~1280 and ~375 from the same trigger (a screen recording, such as
  Playwright's `recordVideo`, or screenshots in quick sequence); the judge
  cannot record motion. Where the reference's motion could not be inspected,
  the packet says so. The judge reports each adapted aspect as preserved,
  intentionally changed or lost, and motion and interaction fidelity at
  desktop and at mobile separately. The final report sets its verdicts beside
  your fidelity ledger (`design-brief` step 5); where they differ, look at the
  render again and say which holds.
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
