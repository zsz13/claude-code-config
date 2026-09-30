# Blind visual judgment

One `visual-design-judge` run (model `opus`), 2026-09-30, on anonymized
screenshots of the three builds. The judge saw only files named `siteA`,
`siteB` and `siteC`; the mapping was fixed before the run and not shown to it:

| Label | Build | Condition |
|---|---|---|
| A | legacy-auto | ordinary request, configuration as it was |
| B | 21st | detailed brief + required 21st use |
| C | control | detailed brief, no 21st |

Averages over the 13 scored criteria, computed from the scores below:
A 76/13 = 5.8, B 92/13 = 7.1, C 102/13 = 7.8.

This is one judge, one run, one build per condition. Its scores are opinions
with named evidence, not measurements.

## Prompt given to the judge

One compound, "AI" hyphenated with "generated", appears twice in the original
and is written "AI-built" here, because this repository's verifier reserves
that compound for authorship claims. The prompt is otherwise verbatim, with its
folder path shortened.

> You are judging three independently built versions of the same product, blind. Work ONLY from the screenshots in this folder; do not open any other directory and do not use the browser tools:
>
> blind/
>
> Files are named site{A,B,C}-{desktop|mobile}-{state}.png. "desktop-scroll-NN" and "mobile-scroll-NN" are consecutive viewport frames taken while scrolling down the page (1440x900 and 390x844); the other states are: details (vehicle detail view opened), filter-applied (one filter applied), card-hover (pointer over a card), filter-sheet (mobile filter UI), menu (mobile navigation opened; a site may have none). All three use the same 12 cars and the same Wikimedia Commons photos, so photo quality is not a differentiator. A small round "N" badge bottom-left is the Next.js dev indicator: ignore it.
>
> The brief all three were given: a premium, editorial automotive marketplace for enthusiast used cars (hero, search, inventory with filters, rich vehicle cards with price/mileage/year/location, featured vehicle treatment, details drawer/modal, favorites, responsive, polished footer, multiple distinct sections). It should look like a serious design team shipped it, not a generic AI-built site.
>
> Look at every image. Then report, for EACH site:
> 1. Scores 1-10 with one line of evidence each (name the file): art direction; originality; layout composition and section diversity; visual hierarchy; typography; spacing rhythm; image presentation; card design; navigation (incl. mobile); filtering UI; detail view; perceived premium feel; responsive quality.
> 2. AI-built fingerprints you can see (be specific: uniform card grids, pills, one radius everywhere, template chrome, predictable hero, etc.), and whether an ordinary person would recognise it as AI-built, and why.
> 3. The single strongest and single weakest design decision.
>
> Then: an overall ranking with the margin between each pair (large / moderate / small / negligible), and a short note on what the three have IN COMMON (patterns all three share). Do not guess which tools or prompts produced which site; judge only what is rendered. Keep the report under 900 words.

## Report, verbatim

I judged all three sites only from the screenshots in the blind/ folder. Scores are out of 10.

### Site A ("Glovebox", green and yellow)
**Scores**
- **Art direction 6:** a coherent green, yellow and paper palette, but it reads as a standard marketplace (A-desktop-scroll-01).
- **Originality 5:** the one real move is the sentence-builder search, "Show me all cars built in any year…" (A-desktop-scroll-00).
- **Layout and section diversity 3:** there are only three sections: hero, inventory, footer (A-desktop-scroll-00 to 04). There is no featured, collections or sell section.
- **Visual hierarchy 7:** the headline, the search panel and the grid read in a clear order.
- **Typography 6:** a wide display face for headline and card titles over a neutral sans; it works but lacks character.
- **Spacing rhythm 7:** even and tidy, but monotonous.
- **Image presentation 5:** every image is the same crop, and the hero is a photo with a thumbnail strip.
- **Card design 6:** clear content (chassis-code chip, owners, "Listed N days ago"), but boxed white cards all built the same way.
- **Navigation 4:** desktop has two links. Mobile has no menu at all, only a "Saved" button (A-mobile-scroll-00).
- **Filtering UI 8:** counts per option, zero-count options greyed out, collection chips, a removable active chip (A-desktop-filter-applied).
- **Detail view 8:** a modal with a spec grid, seller block and payment estimator (A-desktop-details).
- **Perceived premium feel 5.**
- **Responsive quality 6:** the mobile layout is clean but just one collapsed column (A-mobile-scroll-02/03).

**AI fingerprints:** a row of pill chips; identical bordered cards on one radius; a white circular heart button on every photo; a "Just listed" badge top-left. Most people would see a competent template rather than obviously AI, and that is the problem: nothing says "editorial."

**Strongest decision:** the sentence-builder search.
**Weakest decision:** the thin page. It is missing the featured treatment and the extra sections the brief asked for, and has no mobile navigation.

### Site B ("Chicane", red-tinted hero)
**Scores**
- **Art direction 7:** a serious editorial voice: wide grotesque, italic serif paint names, gray paper background.
- **Originality 7:** paint-colour swatches on cards, a "Car of the week" split section (B-desktop-scroll-06).
- **Layout and section diversity 8:** hero, collections index, mixed-size gallery, car of the week, a numbered buying timeline, sell section, footer.
- **Visual hierarchy 6:** the red-tinted hero with a thumbnail strip over it is muddy and crowded (B-desktop-scroll-00). "Featured" appears on 5 of 12 cars.
- **Typography 8:** the grotesque, serif body and italic colour names give it a real magazine voice.
- **Spacing rhythm 6:** the right third of "How buying works" is empty (B-desktop-scroll-08); the sticky header covers the search box (B-desktop-scroll-01); "Nashville, TN" wraps (B-desktop-scroll-05).
- **Image presentation 7:** large feature tiles break up the grid; the tinted hero lets it down.
- **Card design 8:** no boxes, and colour name, price and specs sit on hairline rules.
- **Navigation 8:** a designed full-screen mobile menu with car thumbnails (B-mobile-menu).
- **Filtering UI 7:** a price slider with a stock histogram, counts, "Clear all". The sticky sidebar is clipped at "History".
- **Detail view 7:** a drawer with "2 of 12" paging, Save and "Ask the seller" (B-desktop-details).
- **Perceived premium feel 7.**
- **Responsive quality 6:** on mobile the inventory starts only in the fourth frame (B-mobile-scroll-03).

**AI fingerprints:** a colour-tinted photo hero; the italic serif plus grotesque "editorial" mix; badge overuse; a numbered timeline section; a footer carrying the full photo-credit list. An ordinary visitor would probably take it for a boutique site, a design-literate one less so.

**Strongest decision:** the mixed-size editorial gallery.
**Weakest decision:** the tinted hero with the overlapping thumbnail strip.

### Site C ("Chicane", paint-strip hero)
**Scores**
- **Art direction 8:** a consistent paint and paper system, with amber used sparingly as the accent.
- **Originality 8:** "The whole inventory, by factory paint", a strip of paint-chip bars that opens up to show a car (C-desktop-scroll-00/01), and a paint-swatch filter.
- **Layout and section diversity 8:** hero plus paint strip, a dark "Featured this week" carousel, inventory, a dark collections index with colour chips and "from" prices, sell section, footer.
- **Visual hierarchy 8:** a strong headline, then search, then the paint strip.
- **Typography 8:** wide display, serif italic, and condensed figures for prices and mileage (C-desktop-scroll-04).
- **Spacing rhythm 7:** about 40px of dead space between model name and price rule in every card (C-desktop-scroll-05); a blank band at the top of frames (C-desktop-scroll-03 and 06).
- **Image presentation 8:** hovering a card swaps to a second photo (C-desktop-card-hover).
- **Card design 7:** no boxes, good data, but that dead gap, and "Featured" on 5 of 12 cars.
- **Navigation 8:** a full-screen mobile menu with a "View saved cars" count (C-mobile-menu).
- **Filtering UI 8:** segmented controls, paint swatches, collapsible groups, a "Saved cars only" toggle.
- **Detail view 8:** a drawer with a heart button, "Copy link", thumbnails and "1 of 12" paging (C-desktop-details).
- **Perceived premium feel 8.**
- **Responsive quality 8:** the paint strip becomes a 6×2 swatch grid on mobile (C-mobile-scroll-01), so it was redesigned, not just collapsed.

**AI fingerprints:** a fixed section formula (huge display heading, small serif paragraph offset to the right, alternating dark and light bands, numbered steps, half-width photo) and badge overuse. Most people would not see it as AI-built. The fixed section formula is the tell.

**Strongest decision:** the paint-chip hero.
**Weakest decision:** "Featured" badges on 5 of 12 grid cards, repeating the featured carousel, together with the dead space in the cards.

### Ranking
1. **C**
2. **B:** a moderate gap behind C (a messier hero, weaker spacing, inventory buried on mobile).
3. **A:** a large gap behind B. A has the best-built filters and detail modal, but it falls short on sections, editorial character and mobile navigation.

### What all three share
- The same page layout: warm off-white background with near-black text, a wide display typeface for headlines, and a left filter sidebar next to a 3-column grid.
- The same card details: a round white heart button top-right on every photo, and a dark badge top-left ("Featured" or "Just listed").
- The same interaction patterns: a mobile bottom sheet with "Clear all" plus "Show 12 cars"; a detail modal or drawer with a "1/2" photo counter; a dark footer with photo credits; a "Bayside Blue" search hint.
- The same copy voice: receipts, binders, records.
- B and C match beyond that: the same name and many of the same section templates.

### States and viewports not verified
- Keyboard focus, loading, empty results, and error states.
- Hover on anything other than cards.
- Tablet widths.
- The lower part of every detail view.
- Site A's mobile menu (there is none).
- The saved or favourites list view.
- Carousel motion.
- Whether the blank bands at the top of B and C frames come from a hiding header or a real gap.
