---
name: design-brief
description: Establish a product-specific visual direction before building UI. Use for a new frontend product, a substantial redesign, a visually important new surface, or a project with no established design system.
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

Then stop. Match it. Consistency beats novelty in an established product, and
"improving" a product into a different design language is a defect unless it was
explicitly requested. A partial or inconsistent system means extract what is
real, and note only the specific gaps you must fill.

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
**principles**, not pixels: hierarchy, density, grid, spacing rhythm, type roles,
palette relationships, radius philosophy, border/shadow treatment, motion,
content structure, image treatment.

Use them as calibration. Never clone a third party's site pixel-for-pixel unless
the user owns that design and explicitly asks for reproduction.

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
