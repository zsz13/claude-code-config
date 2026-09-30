> Published copy. One compound in the original, "AI" hyphenated with
> "generated", is written "AI-built" here, because this repository's verifier
> reserves that compound for authorship claims. Otherwise verbatim.

You are building one side of a controlled A/B frontend experiment. Build it completely and to the best standard you can.

## Ground rules for the experiment

- Work only inside the current directory (~/frontend-21st-ab/21st). Do not read, list, search, or modify any other directory under ~/frontend-21st-ab. In particular, never look at the sibling project; the two builds must stay independent.
- Already set up for you, identically for both sides:
  - Next.js 16 + React + TypeScript + Tailwind CSS v4, scaffolded with create-next-app (App Router, `src/` directory, npm). Choose any additional npm packages you judge worthwhile.
  - Mock data: `src/data/listings.json` (12 vehicles). Use this dataset as the inventory. You may derive TypeScript types from it and add presentational copy, but do not change the vehicles, prices, mileage, years, locations, or specs.
  - Photos: `public/cars/*.jpg` (Wikimedia Commons, freely licensed; attribution data in `public/cars/CREDITS.json`). These are the only vehicle photos. The licenses require credit, so the site must credit the photographers somewhere sensible (for example a credits section or footer link).
- The dev server for this project runs on port 3102: `npm run dev -- -p 3102`. Stop any server you start before you finish.
- No backend, authentication, database or real API. Everything runs on local mock data.

## Common product brief

Build a polished frontend-only premium automotive marketplace website.

This should look like something a serious production design team could plausibly ship, NOT a generic coding-demo landing page.

The marketplace sells interesting used and enthusiast cars.

Required experience:

- visually strong homepage
- navigation
- expressive hero area
- vehicle search
- inventory/listing section
- filtering UI
- visually rich vehicle cards
- price, mileage, year and location
- featured vehicle treatment
- vehicle details preview or modal/drawer interaction
- favorites interaction
- responsive desktop/mobile behavior
- polished footer
- multiple visual sections instead of one repeated card grid

I specifically want the design to avoid generic AI-built frontend patterns.

The visual design should feel editorial, automotive and premium.

Use composition, typography, imagery treatment, spacing, layering, transitions, shape, scale and motion deliberately.

Use asymmetry when useful.

Avoid making every section a centered container containing a heading followed by three identical cards.

Avoid turning every piece of content into a rounded card.

Avoid excessive pills.

Avoid excessive gradients.

Avoid excessive glassmorphism.

Avoid default purple/blue AI color palettes.

Avoid excessive use of the same border radius.

Avoid overly uniform spacing.

Use stronger visual rhythm and contrast between sections.

Motion should be tasteful and functional, including things such as:

- section reveals
- hover transformations
- image transitions
- navigation interactions
- filter transitions
- card interactions
- subtle parallax or depth where appropriate
- microinteractions

Do not add animation merely for decoration.

The result should feel designed rather than generated.

Responsive requirements: it must work well at desktop (~1440px), laptop (~1280px) and mobile (~390px) widths.

## This side: 21ST (use the 21st MCP heavily and meaningfully)

Implement the brief while explicitly using the 21st MCP (tools named `mcp__21st__*`; they are deferred, so load them with ToolSearch first) heavily and meaningfully during the actual design process. Do not make one token call just to satisfy the requirement.

Use the 21st tools that are actually available here where appropriate: component/design search, inspiration discovery (`get_inspiration`), template discovery, component retrieval, themes, and so on.

Account facts, checked just before this run:
- Free tier. Component-code retrieval (`get_component`) is limited to 2 per day, so choose those two deliberately. Metadata tools (`search`, `get_inspiration`, `get_theme`, `search_logo`, the list tools) are free.
- Hosted AI generation is not enabled on this account, and `generate`/`iterate_generation` are unavailable. Adapt what you find with your own coding instead.

Before coding substantial sections, use 21st to investigate multiple suitable design and component directions. Do not just accept the first generic result. Look for components and patterns suitable for:

- automotive experiences
- editorial layouts
- image-heavy commerce
- premium catalogs
- dynamic navigation
- filtering/search experiences
- creative galleries
- immersive hero treatments
- transitions and interactions

Use 21st results as design material, then adapt them coherently. Do not create a Frankenstein UI of unrelated components. Keep one consistent art direction.

Keep a log in `21ST-LOG.md` of every 21st MCP call you make: tool name, purpose, the query or id (no secrets), and what design decision it influenced (or "none" if it influenced nothing). The goal is indisputable evidence that this version actually used 21st.

## Definition of done

- `npm run build` and `npm run lint` both pass.
- Verify the rendered result yourself in a real browser at desktop and mobile widths and fix what you find.
- Write `NOTES.md` in the project root recording: the art direction and major design decisions, libraries added, approximate number of custom components, animations and interactions implemented, and whether any external UI/design tool was used, plus a pointer to 21ST-LOG.md.
- Finish with a short summary of what you built.
