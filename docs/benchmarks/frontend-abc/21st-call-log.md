# 21st MCP call log

Every `mcp__21st__*` call made while designing and building this site, in order.
Account: free tier, 2 `get_component` retrievals per day, hosted generation off.
Preview images and preview videos returned by the search tools were downloaded and
inspected (videos as frame strips via ffmpeg) before any decision was made; "viewed"
below means the preview was actually looked at, not just the metadata.

## Phase 1: research before any code

| # | Tool | Purpose | Query / id | What it influenced |
|---|------|---------|------------|--------------------|
| 1 | `get_usage` | Confirm tier, retrieval quota, AI generation status | none | Confirmed 2 retrievals/day and no generation, so the plan became "search widely, retrieve two, adapt by hand". |
| 2 | `get_inspiration` | Broad direction for the whole homepage | "premium automotive marketplace homepage for enthusiast used cars, editorial magazine layout, image-heavy" | Surfaced Hero Carousel (24752) and Elegant Carousel (10025), the two hero candidates. Viewed both. Elegant Carousel's per-slide labelled progress rail fed the hero's position rail; its split layout was rejected because the car photos are landscape. |
| 3 | `search` (component) | Automotive-specific heroes | "car dealership automotive hero" | Nothing automotive-specific; generic SaaS heroes. Confirmed there is no ready-made car hero, so the hero would be adapted from an editorial pattern. |
| 4 | `search` (template) | Look for a car marketplace template | "automotive car marketplace" | 0 results. None. |
| 5 | `search` (component) | Filtering UI patterns | "product filter sidebar with facets and range slider" | Viewed Ecommerce Category Page (29395, preview + video) and Range Slider (7581). 29395 set the filter rail structure: sticky rail, removable active-filter tokens, sort control, empty state, mobile filter sheet. 7581's histogram-under-slider became the price rail where every car is a tick mark. |
| 6 | `search` (component) | Card + favourite patterns | "listing card with favorite heart button image hover" | Heart Favorite (10627) and Carousel Cards (19168) confirmed the save-button-on-image convention; kept the convention, rejected the rounded card shell. |
| 7 | `search` (component) | Detail preview container | "side drawer sheet product detail quick view" | Viewed Information Drawer (27160). Its full-height drawer with staged content fade set the quick-view drawer's motion (panel slides, then content staggers in). Wensity Drawer (31360) set the responsive split: side drawer on desktop, bottom sheet on mobile. |
| 8 | `search` (component) | Navigation patterns | "editorial navbar menu full screen overlay animated" | Viewed Immersive Full Screen Navigation (27229, preview + video). Its panel wipe followed by large staggered links became the mobile menu. |
| 9 | `get_inspiration` | Immersive hero options | "immersive full-bleed hero with large photography, oversized typography and slideshow for luxury vehicles" | Viewed Hero Scrub (12213, automotive): rejected, it needs a video frame sequence we don't have. Reinforced Hero Carousel (24752) as the hero base. |
| 10 | `search` (component) | Scroll-driven sections | "horizontal scroll gallery pinned sticky section" | Viewed Scroll Gallery (30118), Sticky Content Wrapper (26064), Horizontal Scroll Gallery (20139). 26064 (sticky image that swaps while copy scrolls) became the "Car of the week" section. Horizontal pinned galleries were rejected as scroll-jacking on a shopping page. |
| 11 | `search` (component) | Editorial / asymmetric grids | "bento grid editorial magazine layout asymmetric images" | All results were SaaS feature bentos with rounded cards. Rejected. The gallery gets its rhythm from mixed column spans instead. |
| 12 | `search` (component) | Search patterns | "search command bar with suggestions autocomplete" | Command Search (28888) and Autocomplete (28230) set the search field behaviour: live suggestions with keyboard navigation (arrow keys + Enter) that open a car directly. The auto-typing placeholder was rejected as decoration. |
| 13 | `search` (component) | Spec sheet presentation | "spec sheet stats table luxury product specifications" | Only dashboards and pricing tables. None; the spec sheet is modelled on a window sticker instead. |
| 14 | `search` (component) | Footer | "editorial footer large wordmark" | Viewed Footer with Minimal Outline (29772). Its outlined wordmark that animates into view was built into the first version of the footer, then **removed** after the rendered-visual review: it was decoration-only motion, which the brief rules out. Final influence: none beyond the footer's column structure. |
| 15 | `get_inspiration` | Filter transitions | "inventory browsing with animated filter transitions, layout reflow when filters change, sort control, result count, empty state" | Viewed Filter Grid (23525). Its smooth reflow on filter change and live counts set the inventory motion: layout animation on reflow, counts per filter option. Its segmented chips were rejected (too pill-heavy). |
| 16 | `get_inspiration` | Card directions | "image-heavy commerce product card with hover image swap, specs row and save button for a premium catalog" | Product Card (5650) / Product Reveal Card (2583) confirmed hover image swap as the card's image transition; their rounded, shadowed shells were rejected. |
| 17 | `search` (theme) | Palette candidates | "warm neutral editorial paper" | 0 results. None. |
| 18 | `search` (theme) | Palette candidates | "dark luxury automotive" | 0 results. None. |
| 19 | `search` (theme) | Palette candidates | "warm" (sort popular) | 0 results. None. |
| 20 | `search` (theme) | Palette candidates | "neutral" (color orange) | 0 results. None. |
| 21 | `search` (component) | List-with-preview patterns | "hover image list preview interactive rows" | Viewed Interactive List Preview (26256, preview + video) and Hover Image List (28258). 26256 was chosen for code retrieval #2 (see #32). |
| 22 | `search` (theme) | Palette candidates | "minimal" | 15 themes; picked Amber Minimal and Modern Minimal to inspect. |
| 23 | `search` (template) | Editorial templates | "editorial magazine" | 0 results. None. |
| 24 | `search` (component) | Number animation | "animated number counter odometer rolling digits" | Rolling Digits (19158) and Number Flow (28181) led to the odometer-style digit roll used for result counts and the saved counter. Written by hand, so no new dependency. |
| 25 | `get_theme` | Inspect token structure | 94e6d897-3245-4a19-b22b-00eac7e02295 (Amber Minimal) | Adopted its structure: neutral ground, one warm accent reserved for interactive state, `--font-serif: Source Serif 4`. Source Serif 4 is the editorial serif here. The amber value itself was replaced by a tachometer-needle orange and the whites by primer greys. |
| 26 | `get_theme` | Inspect token structure | 88cbde1f-7527-430c-b4d5-49bb3b9e621d (Modern Minimal) | Rejected: default blue primary, the palette the brief asks to avoid. Only confirmed the semantic token naming. |
| 27 | `search` (component) | Headline reveal | "text reveal headline mask lines stagger on load" | Text Reveal (Mask) (19257) confirmed the masked line wipe, which is also in the retrieved Hero Carousel. It is used once, on the hero headline. |
| 28 | `search` (component) | Image depth | "image clip-path reveal on scroll parallax" | Parallax Image (20023) set the parallax approach: scroll-linked translate on the hero and the car-of-the-week photo only, not everywhere. |
| 29 | `search_logo` | Maker logos for a make filter | "porsche" | 0 results. Car maker marks aren't in the library, so the make filter is typographic. |
| 30 | `search_logo` | Maker logos | "bmw" | 0 results. Same decision as #29. |
| 31 | `search` (component) | Save feedback | "toast notification with undo action" | Toast (3977) / Sonner Toast (19941) set the save and remove feedback: a toast with an Undo action. |

## Phase 1b: the two code retrievals (free-tier quota: 2 per day)

| # | Tool | Purpose | Id | What it influenced |
|---|------|---------|----|--------------------|
| 32 | `get_component` | Retrieval 1: the hero | 24752 (Hero Carousel, crafterui) | The hero's foundation. Adopted: measured geometry from one ResizeObserver; a motion-value-driven filmstrip track with spring and drag-with-velocity landing; a shared top edge where the focused card unfurls to full height and its neighbours stay clipped; the background re-grade (`mix-blend-mode: color` + `multiply` with an accent colour); the masked line-wipe headline; autoplay that pauses on hover or focus; a position rail. Adapted: cards are landscape because cars are; the accent is each car's factory paint colour; wheel-stepping removed (a scroll trap on a shop homepage); the mono uppercase meta replaced by price, mileage and location; a grain overlay kept to unify mismatched photos. |
| 33 | `get_component` | Retrieval 2: list with image preview | 26256 (Interactive List Preview, hyperiux) | The Collections index and the inventory's Index view. Adopted: a highlight bar that tweens to the hovered row with inverted text; stacked preview images revealed with a `clip-path: inset(50%) → inset(0)` iris and a rising z-index so each new image layers over the last; a lerped pointer-follow on the preview; a coarse-pointer (touch) fallback that shows images inline; reduced-motion fallbacks. Adapted: ported from GSAP to `motion` (no GSAP dependency), difference blend removed, rows carry real listing data. After review, the Collections preview became a static plate in the empty column beside the list, and the Index-view preview floats above the hovered row, so neither covers the row's own data. |

## Build-phase calls

Made after the first full render, once it was clear which inspiration results had
actually been used. Each call feeds 21st's ranking with a real accept/reject signal.
Two calls failed with a connection reset while the MCP server reconnected and were
retried; the failed attempts are listed too.

| # | Tool | Purpose | Query / id | What it influenced |
|---|------|---------|------------|--------------------|
| 34 | `record_inspiration_feedback` | Feedback on call #2 | feedbackId 30d3d3ce…, result 24752, accepted | Failed (ECONNRESET, server reconnecting); retried as #39. |
| 35 | `record_inspiration_feedback` | Feedback on call #2 | feedbackId 30d3d3ce…, result 19074, rejected | Failed (ECONNRESET); retried as #40. |
| 36 | `record_inspiration_feedback` | Feedback on call #9 | feedbackId 40216236…, result 12213 (Hero Scrub), rejected | Recorded. Rejected because it needs a video frame sequence the project doesn't have. |
| 37 | `record_inspiration_feedback` | Feedback on call #15 | feedbackId 150b1b6a…, result 23525 (Filter Grid), accepted | Recorded. Its reflow-on-filter behaviour is in the inventory. |
| 38 | `record_inspiration_feedback` | Feedback on call #16 | feedbackId 142be07f…, result 5650 (Product Card), rejected | Recorded. The rounded, shadowed card shell was rejected; only the hover image swap idea was kept. |
| 39 | `record_inspiration_feedback` | Retry of #34 | feedbackId 30d3d3ce…, result 24752 (Hero Carousel), accepted | Recorded. It is the hero's foundation. |
| 40 | `record_inspiration_feedback` | Retry of #35 | feedbackId 30d3d3ce…, result 19074 (Editorial Collage Hero), rejected | Recorded. Two overlapping photos in a soft wash didn't suit landscape car photography. |
