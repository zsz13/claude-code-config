---
name: design-brief
description: Establish a product-specific visual direction before planning or building UI. Use for substantial frontend work (the list in frontend-quality's description) when frontend-quality's routes call for it, which always includes a new product or a project with no design system.
---

# Design brief

A design direction comes from the product, not from a default look; only how
strongly it speaks has a default, when the request leaves that open (step 2).
This skill produces the inputs that make the `frontend-design` skill's
aesthetic work specific to *this* product instead of interchangeable with any
other.

**Do not invoke this for a CSS bug fix, a copy tweak, or a component that an
existing design system already answers.**

## 1. If a design system already exists, extract it — do not invent

Check first, always. Look for token files, theme config, Tailwind/CSS variables,
a component library, Storybook, existing screens, a brand or style guide.

If one exists and is coherent, your job is **extraction, not authorship**. Record
what it already decided:

- type families, scale, weights, and what each role is used for;
- color roles and how the accent is actually rationed in practice;
- spacing rhythm and the grid in use;
- radius, border, and shadow philosophy;
- component primitives and their state treatments;
- motion patterns;
- copy voice.

Then stop. Match it. (A new screen or a component-system change gets step 3's
research only when `frontend-quality`'s "Research" says research runs, and only
for what that rule allows.) Consistency beats novelty in
an established product, and "improving" a product into a different design
language is a defect unless it was explicitly requested. A partial or
inconsistent system means extract what is real, and note only the specific gaps
you must fill.

## 2. For greenfield or redesign, establish the direction

Determine these from the repository, the content, and the request. **Ask only
what you genuinely cannot determine** — a wall of questions is a worse start
than a proposal the user can correct. Proposing a concrete direction (three,
where step 4 applies) and asking "is this right?" beats interrogating.

1. Product / subject — what is this, concretely?
2. Audience — who uses it, in what context, how often?
3. Primary job of this screen — the one thing it must accomplish.
4. Emotional tone.
5. Existing brand (logo, colors, voice, prior marketing).
6. Existing design system, if any (see step 1).
7. Visual references, if the user has any.
8. Explicit dislikes and an avoid-list.
9. Content density — sparse and editorial, or dense and operational?
10. Accessibility constraints beyond the baseline.
11. Mobile vs desktop priority — which is the real primary?
12. Light, dark, or both.

The subject's own world — its industry, materials, vocabulary, artifacts — is
where distinctive choices come from. A tool for archivists and a tool for
day-traders should not converge.

**Default register: expressive but controlled.** The product decides what the
design is about. When the request leaves open how strongly it speaks, the
owner's default taste answers: a designed, visually strong product, not a
neutral tool. That means:

- a first viewport with one obvious focal point, a visible primary action,
  hierarchy and composition specific to this product, and some drama: depth,
  motion, or a sense that it is ready to be used;
- layered composition, asymmetry where it helps, clear contrast between
  sections, a varied rhythm across them, and hierarchy visible at a glance;
- bold, deliberate typography, and richer cards and sections where the
  content earns them;
- real motion and interaction (`frontend-quality`'s "Motion"), with at least
  one memorable interaction or visual device.

Unless the request asks for them, it rules out restrained enterprise UI, flat
grey dashboards, white cards on a neutral background everywhere, a generic
SaaS template, one spacing and radius on everything, a passive sidebar, a
static layout, a dark technical console, and any design whose identity
disappears with the logo and copy removed. Between safe but bland and
expressive but controlled, take the second.

The register is not open, and this default does not apply, when:

- the request asks for restrained, minimal, calm, subtle, operational,
  utility-first or highly functional design;
- the references the user gave or chose are deliberately minimal;
- the work keeps an established design system's look (step 1); a request
  for a new look in such a product leaves the register open;
- the proposal names a product reason that intensity would harm: a domain
  whose users need sober seriousness, or a cost to accessibility or
  usability. "Safer" is not a reason.

## 3. Handling references

When given screenshots, Figma files, URLs, or named references, extract
**principles**, not pixels: information hierarchy, composition, content density,
what sits above the fold, navigation model, grid and spacing rhythm, type roles,
interaction patterns, empty/loading/error handling, responsive behavior, palette
relationships, radius philosophy, border/shadow treatment, motion, image
treatment.

Use them as calibration, or, in a reference-led direction (step 4), as its
basis. Never clone a third party's site pixel-for-pixel unless the user owns
that design and explicitly asks for reproduction, and never take its
branding, logos, illustrations, photography or copy. Adapt its structure,
interaction patterns, motion ideas, layout, rhythm and overall treatment, and
replace the content and product semantics with this product's.

**Researching references.** For substantial frontend work (as
`frontend-quality` defines it) whose structure is still open, and no references
were given, study how shipped products solved the same problem before choosing a
direction. In an established design system, `frontend-quality`'s "Research"
decides whether this runs and what it may inform.

- Search Refero first. Add Mobbin only when Refero's coverage of that screen
  type is weak, when mobile-app patterns are central, or when a second set
  would change the decision. With neither connected, skip this screen search
  and do not work from memory of famous products. Component research
  (21st.dev, in `frontend-quality`'s "Research") runs alongside and does not
  wait on these.
- Pick references because they solved a similar problem (the same user job, a
  similar data shape, similar constraints), never because the company is
  famous: two or three for one direction, enough for three distinct ones when
  the direction gate applies (step 4). Judge each by its screenshot or preview,
  not its title (`frontend-quality`'s "Research"). Among those that fit,
  prefer the visually excellent: shipped products and components whose
  composition, motion and finish are strong, not merely adequate. Under the
  default register (step 2), a reference that solves the problem blandly, such
  as a plain data table, can calibrate a direction but not lead one. When
  nothing that fits is also strong, widen the search to an adjacent problem
  or component with the same data shape, and say in the proposal that the
  lead reference comes from there.
- Extract the principles above, each with the reason it fits this product.
  Never average several unrelated products into a composite. In an
  established design system, references inform only what `frontend-quality`'s
  "Research" allows.

**With no research tool connected** (no Refero, Mobbin or 21st.dev) and
research due under `frontend-quality`'s "Research", do not skip this step, and
do not fall back to defaults or to memory of famous products. Write an internal
art direction instead, and state it before the plan or any code. It covers what
that rule lets research inform. The items marked *style* apply only where that
rule leaves style open; otherwise match the system's style.

- **References from the subject's own world** (*style*): three to five
  artifacts, documents or materials the product's users already know (for a
  wine shop: a tasting note, a vintage chart, a cellar ledger), and what each
  lends to type, layout, density or texture.
- **Structure per section:** each section's job and the structure that job
  needs, so that adjacent sections differ (see "Compose the page" below).
- **Rejected defaults:** the default arrangements this direction will not use,
  named.
- **Signature element** (*style*): the one memorable move (step 6).

If the direction that comes out leans on the generic defaults listed in step 5,
it came from defaults, not from the product or its references. Go back to the
product.

**Compose the page, do not stack it.** A page with several jobs gives each
section the structure its job needs (scale, density, alignment, surface,
imagery), and adjacent sections contrast. Hero, one repeated grid, footer, or a
heading over identical items in every section, is the default arrangement, not
a composition. Keep rounded cards for things that behave as objects (something
opened, saved, or compared), pills for removable filter state, and let radius
and surface change with hierarchy rather than repeat everywhere.

## 4. Three directions, then stop

When `frontend-quality`'s direction gate applies, propose exactly three
directions from the research, then stop for the user's choice. Each differs
from the others in composition and in visual register (surface, color, type,
imagery), not only in metaphor or palette: "blue, green, dark" is one
direction three times; "editorial evidence workspace, dense investigative
console, visual case-file comparison" is three. One surface treatment under
three metaphors (three muted dashboards, three dark technical consoles, three
paper ledgers) is also one direction three times.

They also differ in **visual energy**, so the user chooses how expressive the
product is, not only its metaphor. No two directions share an energy level.
Under the default register (step 2) they sit at 2, 3 and 4, so two of the
three are visually strong and none is a 1. A 1 appears only when step 2 says
the register is not open, and the proposal then names which condition applies.

**At least one direction is reference-led.** It is built around one or two
strong references from research, not around a verbal concept. Their
composition and interaction model are its starting point, and its reference
fidelity is high. Under the default register it is one of the two strong
directions (Energy 3 or 4), and its references were chosen for their visual
quality as well as their fit (step 3). Show those references themselves
(preview image or URL, when research provided one), and fill its **Adapts**
field below.

Per direction, a few lines:

- **Name** — its organizing idea, in the product's terms.
- **Scores** — this line, all four filled:
  `Energy n · Density n · Motion n · Fidelity low|medium|high`.
  Energy: 1 restrained, operational; 2 polished product UI; 3 expressive,
  dynamic; 4 experimental, highly visual. A screen whose main unit is rows of
  a table or ledger on a plain surface is a 1, whatever its paper tint or
  typeface. Density: 1 sparse to 4 dense.
  Motion: 1 state feedback only, to 4 motion that carries the experience.
  Fidelity: low, references calibrate; medium, their principles are adopted;
  high, built on their composition and interaction.
- **References** — two to four from research, each with its preview image or
  URL so the user can judge it by eye, and the composition or layout principle
  borrowed from it. The reference-led direction has exactly one or two.
- **Adapts** (reference-led direction only) — six entries, in this order:
  composition, hierarchy, spacing rhythm, interaction model, motion, visual
  treatment. Each says what it takes and from which reference, or "not taken";
  composition and interaction model are never "not taken", and neither is
  motion when a reference has meaningful motion. Hierarchy, spacing rhythm and
  visual treatment are taken unless the entry names a product reason. Visual
  treatment means depth, contrast, surface and richness, never brand assets.
- **Visual character** — first its register in a few words (for example
  "ink on cream paper", "saturated photographic", "bold flat color blocks"),
  then typography, contrast, color use, density, geometry. No two directions
  share a register, however they name it: two paper-and-ink directions (a
  ledger and a printed packet, say) share one.
- **Signature** — one idea specific to this product.
- **Avoids** — what it deliberately does not do.
- **Tradeoff** — its main cost.

Then ask the user to pick A, B, C or a mix. The proposal fits in one response.
Do not mock up, render or build the directions; the references' own previews
show them. With no research tool connected, the references are
subject's-world artifacts as in step 3's fallback, two to four per direction,
and the proposal says no shipped product was inspected. The reference-led
direction is then built on one or two of those artifacts, and the proposal
invites the user to name a product or page they would rather it follow.

## 5. After the choice: references as constraints, then the pre-build check

The selected references stop being inspiration. The plan names which reference
informs the page composition, which the interaction behavior, which the
typography and visual rhythm, and which of their ideas are deliberately not
copied. Adapt each reference closely in what it was named to inform, never
verbatim (step 3), with this product's content and semantics in place of its
own. For a reference-led direction at high fidelity, that means keeping its
references' composition, interaction model, motion language, hierarchy,
rhythm and the richness that made them worth choosing. What it said it
adapts is a constraint: the plan keeps it, or says why not, and "simpler to
build" is not a reason. When that
reference is a 21st.dev component whose composition or interaction is central
to the direction, and its source is available, prefer adapting that source to
rebuilding it from the preview: fetch it with `get_component` where
`frontend-quality`'s "Component libraries" allows (a React project), and port
it as that section says.

**Motion-led references.** When a selected reference includes meaningful
animation, gesture, transition, scrubber, stack behavior, drag or swipe
interaction, or other motion-led behavior, its static screenshot is not
enough: it shows one frame, and can show a state the behavior only passes
through. Before implementation, inspect at least one of:

- its preview video or animation (21st.dev results give a `videoUrl`): save
  it, extract frames, for example
  `ffmpeg -i preview.mp4 -vf "fps=3,scale=480:-1,tile=4x2" frames.png`, and
  Read them;
- its live demo, opened in the browser, with the behavior triggered and
  screenshotted in sequence;
- the retrieved source that defines the motion (`get_component`, above).

Then add a behavior note for that reference to the plan: the trigger; what
moves and how; timing and sequence, where they matter; mobile behavior (the
reference's, or, when it shows none, what this product's version does at
~375px); reduced-motion behavior, if it has one. When none of the three can
be inspected, the note says so and why, rather than reading the behavior off
the still frame, and the ledger and the final review mark that reference's
motion as unverified.

**Fidelity ledger.** For a reference-led direction at high fidelity, each
Adapts entry it took is tracked through implementation as **preserved**,
**intentionally changed** or **lost**, and each change or loss says why. The
final report lists them, and the final review checks them
(`frontend-quality`'s "Review integration").

Then, before any production UI code, answer in the plan:

1. With the logo and product copy removed, would the composition still say
   what domain this is?
2. Which three or more visible decisions are specific to this product rather
   than SaaS defaults? The final review checks that these are visible.
3. Which generic defaults is this plan most at risk of?
4. Is the page composed from the selected direction, or has it drifted back
   to the defaults: a header over a centered container, white cards on gray,
   uniform rounded rectangles, repeated grid sections, a large empty hero,
   decorative metrics, a passive right sidebar, pills everywhere, one accent
   over neutral UI, gradient or glass surfaces, AI purple?
5. Does each major section have the structure its job needs, rather than one
   component pattern reused ("Compose the page" above)?

Then the visual-energy check, against the selected direction (its scores, when
step 4 gave it some) and its references. In a mix, each part keeps the scores
and references of the direction it came from.

6. What is the first viewport's one focal point, and where is its primary
   action?
7. Where does the eye go first, second and third?
8. What moves, and what changes visually as the user progresses?
9. What is the most memorable interaction or visual device?
10. Which region has the strongest visual contrast, and what gives the
    interface its energy?
11. Is the plan noticeably flatter, duller, more static or more generic than
    the selected references (or, with none, than the energy and motion the
    direction calls for)? Does it still read as a designed product, or has it
    collapsed into a dashboard? If either, name the product reason their
    stronger qualities are given up. "Simpler to build" is not a reason.

A weak answer means the composition is revised now, not after the render. So
does a plan with no focal point, the same visual weight everywhere, or
repeated panels or cards. So does a first viewport that reads as a generic
form, card grid or dashboard when the product does not need one. So does a
plan that falls below the selected direction: no meaningful motion where the
direction calls for motion, only one neutral surface with one accent where the
direction or its references have more, or much less visual richness than the
selected references. Choosing a
restrained direction lowers the energy the plan must reach, never its fidelity
to the references the direction adapts.

**Write the check down before any product UI file.** The check leaves one
file, `.design/prebuild.md` at the project root (in a monorepo, the root of
the package whose UI changes), holding only:

- the selected direction: its name, its score line(s) when step 4 gave any,
  and who chose it;
- the selected references, each by URL or name, with its saved preview when
  it has one, and for a motion-led one its behavior note;
- the answers to questions 1 to 11, a line or two each;
- what the check revised in the plan, or "none".

**No product UI file may be written before this file exists**: no component,
page, markup, style, token or theme file. This holds in autonomous and headless
runs too. Announcing the check, or running it only in reasoning, does not
count; the file is the evidence that it ran. It is written in this task,
after this direction was selected: a file left from an earlier direction does
not count, and is replaced. Work that does not run this check writes no such
file.

## 6. Write it down — only when it will be reused

Produce a project `DESIGN-BRIEF.md` when the work spans more than one session or
more than one surface. **Do not create one in every repository**, and do not
create one for a single screen you are about to finish.

Sections, kept short — one to four lines each:

```
# Product          # Audience         # Primary job
# Design principles                   # Visual direction
# Anti-goals       # Typography roles # Color roles
# Spacing / layout rhythm             # Surface, radius, shadow philosophy
# Motion philosophy # Iconography     # Content / copy tone
# Responsive strategy                 # Accessibility baseline
# Signature element
# Selected direction (its scores, and its references as constraints, step 5)
```

**Signature element** is the one memorable move this product owns. One. A
signature on every component is not a signature.

**Anti-goals** are what this product is deliberately not — more useful than
another list of adjectives it is.

## 7. Tokens

Define semantic tokens, not scattered literals:

- **color roles** — surface, text, action, border, status; not `blue-500` at call sites;
- **type roles** — display, heading, body, label, code;
- **spacing scale**;
- **radii**, **borders**, **shadows**;
- **motion** durations and easing.

primitive (`gray-900`, `space-4`) → semantic (`surface-raised`, `text-muted`,
`action-primary`, `border-subtle`) → component tokens **only where they earn it**.

Do not abstract every value, and do not build a token architecture larger than
the product. If a design system already owns these values, use its names and
values — do not mint a parallel vocabulary.

## Then

Hand the brief to the `frontend-design` skill, which owns the aesthetic work
itself. This skill establishes *what is true about the product*; that one decides
*what it should look like*. Do not restate its guidance here. When step 4 ran,
step 5 comes back into play on the resulting plan, before any production UI
code.
