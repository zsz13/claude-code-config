---
name: design-brief
description: Establish a product-specific visual direction before planning or building UI. Use for substantial frontend work (the list in frontend-quality's description) when frontend-quality's routes call for it, which always includes a new product or a project with no design system.
---

# Design brief

A design direction comes from the product, not from a default. This skill
produces the inputs that make the `frontend-design` skill's aesthetic work
specific to *this* product instead of interchangeable with any other.

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
than a proposal the user can correct. Proposing a concrete direction and asking
"is this right?" beats interrogating.

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

## 3. Handling references

When given screenshots, Figma files, URLs, or named references, extract
**principles**, not pixels: information hierarchy, composition, content density,
what sits above the fold, navigation model, grid and spacing rhythm, type roles,
interaction patterns, empty/loading/error handling, responsive behavior, palette
relationships, radius philosophy, border/shadow treatment, motion, image
treatment.

Use them as calibration. Never clone a third party's site pixel-for-pixel unless
the user owns that design and explicitly asks for reproduction.

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
- Pick two or three references because they solved a similar problem (the
  same user job, a similar data shape, similar constraints), never because
  the company is famous.
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
- **Signature element** (*style*): the one memorable move (step 4).

If the direction that comes out is a default card grid, a large empty hero,
decorative metrics, gradient or glass surfaces, or AI purple, it came from
defaults, not from the product or its references. Go back to the product.

**Compose the page, do not stack it.** A page with several jobs gives each
section the structure its job needs (scale, density, alignment, surface,
imagery), and adjacent sections contrast. Hero, one repeated grid, footer, or a
heading over identical items in every section, is the default arrangement, not
a composition. Keep rounded cards for things that behave as objects (something
opened, saved, or compared), pills for removable filter state, and let radius
and surface change with hierarchy rather than repeat everywhere.

## 4. Write it down — only when it will be reused

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
```

**Signature element** is the one memorable move this product owns. One. A
signature on every component is not a signature.

**Anti-goals** are what this product is deliberately not — more useful than
another list of adjectives it is.

## 5. Tokens

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
*what it should look like*. Do not restate its guidance here.
