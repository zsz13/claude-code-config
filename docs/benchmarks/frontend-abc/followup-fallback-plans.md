# Follow-up fallback runs: the replies

Round 2 of the [follow-up protocol](followup-protocol.md), run on the final skill
text in sessions with no MCP server connected (`--strict-mcp-config` with an
empty server list). Each reply is the run's complete final answer; the scoring
rests on these.

- **F1, F2:** the [composition-plan prompt](prompts/composition-plan.md) (used-car marketplace), in an empty directory.
- **F3, F4:** [plan-vet](prompts/followup/plan-vet.md) (veterinary clinic), in an empty directory.
- **EF1, EF2:** [est-compare-open](prompts/followup/est-compare-open.md), in the control build, an established design system.

The skill's worked example is a wine shop; no reply uses it.

---

## F1

No reference-research tools (Refero, Mobbin, 21st.dev) are connected here, so the art direction below comes from the car world itself rather than from other marketplaces.

**Art direction** (working name: *Paddock*)
- **Borrowed from the car world:**
  - The window sticker: ruled spec blocks and aligned numbers. It shapes the spec line on each car card and the spec sheet in the detail view.
  - The stamped service book: dated history entries.
  - The auction catalogue: lot numbers, large photos and short editorial captions.
  - The factory option-code sheet: codes set in a fixed-width font.
  - The rev counter: its red zone sets the rule that one warm accent color is used sparingly.
- **Look:** a warm off-white background with near-black text, one orange accent used only for main actions and saved cars, and dark bands for the editorial sections. Type is a narrow sans-serif for headlines, a plain sans-serif for body text, and a fixed-width font for specs, VINs and lot numbers.
- **Signature element:** the live results count rolls like a mechanical odometer whenever filters change. Nothing else on the page animates that way.
- **Ruled out:** a full-width stock photo with a centered see-through search bar, the same card grid in every section, a row of made-up stats, a testimonial carousel, gradients, glass effects or purple, and every element fading in on scroll.

### Homepage sections, in order

1. **Header**
   *Job:* help people find their way around and keep search and saved cars always one tap away.
   *Layout:* a slim bar that stays at the top: logo on the left, page links in the middle (Inventory, Featured, How buying works, Sold) and a Garage button with the saved-car count on the right; on mobile the links move into a full-height menu.

2. **Hero + search**
   *Job:* turn what the buyer wants into a filtered list of cars in one action.
   *Layout:* an uneven two-column split: headline and a window-sticker-style search form on the left (make/model, max price, max miles, gearbox) with a live "Show 214 cars" button, and one car photo with a lot-number caption on the right; on mobile the form comes first and the photo shrinks to a short strip.

3. **Browse by breed**
   *Job:* give people who shop by character rather than specs a way in (Air-cooled, Manual only, JDM heroes, V12 GT, Track-ready, Modern classics).
   *Layout:* one horizontally scrolling row of text-led tiles, each with a name, car count and simple line drawing; tapping one applies a preset filter and scrolls down to the inventory.

4. **Inventory**
   *Job:* the main work of the page: find, compare and save cars.
   *Layout:* a filter panel on the left that stays in view, and on the right a toolbar (odometer count, sort menu, removable filter tags) above a 3-column grid of cards (photo, save heart, price, spec line of year · miles · gearbox · drive) that animate into place when filters change; on mobile it's one column, with filters in a bottom panel opened by a "Filters · 3" button that stays on screen.

5. **Featured lot**
   *Job:* tell one exceptional car's full story and history, to earn the trust of buyers spending a lot.
   *Layout:* a full-width dark band: a large photo gallery across two-thirds, and beside it editorial notes plus a service-book-style list of dated history entries, with an "Open full listing" button.

6. **How buying works**
   *Job:* take the fear out of buying a $90k car without seeing it: inspection, refundable deposit, enclosed transport, return window.
   *Layout:* four numbered, text-only steps along one horizontal line (a vertical timeline on mobile), with no icon cards.

7. **Recently sold**
   *Job:* show what similar cars actually sold for; this replaces testimonials as the proof buyers can trust.
   *Layout:* a dense ruled table (car, miles, sold price, difference from asking price, days listed) with fixed-width numbers; on mobile each row folds into two lines.

8. **Footer**
   *Job:* give a next step when nothing fit, plus the full site map.
   *Layout:* a dark block: a top row with a "Hunting for something specific?" alert sign-up form, then four link columns (Buy, Sell, Company, Support) and a legal bar at the bottom; the columns become a 2-column grid on mobile.

**Pop-up panels (opened from the page, not part of the scroll order)**
- **Vehicle detail**
  *Job:* look closely at one car without losing your place in the inventory.
  *Layout:* a panel sliding in from the right on desktop and a full-screen view on mobile, with a gallery, window-sticker spec sheet, service history, price and a "Request a viewing" button; each car has its own shareable link, and Esc or the back button closes it.
- **Garage (saved cars)**
  *Job:* review your saved cars.
  *Layout:* a narrow panel from the right listing each saved car (thumbnail, name, price, remove button); saved cars stay in the browser between visits.

---

## F2

No design-research tools are connected here (Refero, Mobbin, 21st.dev) and the directory is empty. So the direction below comes from things car buyers already know, not from other sites.

**Direction**
- **Borrowed from the car world:** the window sticker (spec tables with thin rules and aligned figures), the auction catalogue (lot numbers and captioned photos), the stamped service booklet (a history timeline) and the magazine road-test data panel (lots of figures in a small space).
- **Look:** warm off-white background, near-black text and one signal-orange accent for primary actions and price drops. The photos carry the colour. Model names are in a condensed sans-serif, body text in a neutral sans, and specs in monospace figures.
- **Signature element:** a vehicle detail panel laid out like a window sticker. It's also the one big animation: the card photo expands into the panel's gallery. Beyond that there's only small feedback on the favourite heart and a short reflow when filters change. All motion is off for people who've set their device to reduce motion.
- **Things I'm deliberately avoiding:** a centred hero with a pill-shaped search box over a stock photo, a row of three "Why choose us" icon cards, "10,000+ happy customers" counters, testimonial carousels, glass or gradient effects, and the same card grid in every section.

**Homepage sections, in order**

1. **Header**
   - *Job:* keeps navigation and a live count of saved cars always in reach.
   - *Layout:* slim sticky bar with the wordmark left, Inventory / Lot of the week / How we inspect in the centre and "Shortlist (3)" on the right; on mobile a menu sheet holds every link.

2. **Hero + search**
   - *Job:* takes a buyer from "I want this" to filtered results in one step.
   - *Layout:* split screen, with a headline and a four-field search on the left (Make, Model, Max price, Gearbox) whose button shows the live count ("Show 38 cars"). On the right is one large featured car with its lot caption, e.g. "Lot 0417 · 2019 Porsche 911 Carrera T · 7-speed manual · 18,400 mi · $118,500". On mobile the search sits above the photo.

3. **Browse by character**
   - *Job:* a way in for people who know the kind of car they want but not the model.
   - *Layout:* a horizontal row of text-led tiles, each with a count: Manual only, Air-cooled, JDM icons, V8 & V12 GT, Track-ready, Electric performance. Tapping one applies that filter and scrolls to the inventory. The row swipes on mobile.

4. **Inventory**
   - *Job:* find cars and add them to the shortlist.
   - *Layout:* a sticky filter column on the left (price, year, mileage, make, body, gearbox, drivetrain, one-owner, full service history). On the right: sort control, result count, removable filter chips, then a 3-column card grid. Each card has a photo with a heart button, the model, one spec line (miles · gearbox · owners · location) and the price. On mobile the filters move into a bottom sheet with a "Show 24 cars" button. If nothing matches, it suggests which filter to remove.

5. **Vehicle detail panel** (opens over the page from any card; not a scroll section)
   - *Job:* lets buyers judge a car without losing their place in the results.
   - *Layout:* a panel sliding in from the right, full-screen on mobile. It holds the photo gallery, the window-sticker spec table, a service-history timeline, an inspection summary, and the price with a "Request a viewing" button. Each car has its own link by lot number; Esc or Back closes it.

6. **Your shortlist**
   - *Job:* compare saved cars side by side.
   - *Layout:* a comparison table with one column per saved car, headed by a thumbnail, and rows for price, mileage, year, gearbox and owners. The columns swipe on mobile. Saved cars stay in the browser between visits. When it's empty, it tells you to tap a heart on any car.

7. **Lot of the week**
   - *Job:* shows the quality of the selection by telling one car's story properly.
   - *Layout:* a full-width photo with a narrow column of editorial text and a quote from the car's service records, e.g. a one-owner 2004 BMW M3 Competition with 41,000 miles. It's the only sparse, long-read section on the page.

8. **How every car is vetted**
   - *Job:* answers the main worry with a used premium car: is it sound?
   - *Layout:* four numbered steps along a horizontal line (Sourced → 212-point inspection → History verified → Delivered with 7-day return) next to an excerpt from a sample inspection sheet. It stacks vertically on mobile.

9. **Footer**
   - *Job:* closes the page with new-car alerts, navigation and business details.
   - *Layout:* a dark block with a "Get new-arrival alerts" email field that shows the current search, four columns of links, showroom address and hours, and a legal row. Columns stack on mobile.

Does this order and direction look right? If so, the next step is choosing the tech stack, the design tokens and the mock data of about 24 cars.

---

## F3

I haven't created any files. No design research tools were connected, so the visual direction below comes from the paper tools vet clinics already use rather than from other products.

### Direction

- **Borrowed from the clinic:**
  - The paper appointment book gives the time-first schedule grid, with one column per vet.
  - The kennel card clipped to each run gives a small patient card.
  - The treatment-room whiteboard gives the patient-flow board.
  - Printed receipts and vaccine certificates give the plain money and due-date tables.
- **Look:** a light, dense working tool. Off-white background, dark text, and one accent colour used only for primary buttons. Thin lines instead of boxed cards. Times, weights and prices are set in fixed-width digits so they line up in columns.
- **Signature element:** the patient card, which shows the name, species, owner's surname and warning stickers ("Bites", "Penicillin allergy", "Diabetic"). The same card appears on every screen, so safety information is always visible.
- **Things I'd avoid:** a row of revenue charts on the dashboard, a month calendar as the main booking view, a grid of pet photos, an icon-only sidebar, and paw-print decoration, gradients or purple.
- **Assumptions:** the front-desk computer is the main device, vets use tablets in the exam rooms, and phones matter least. The clinic has 2–4 vets.

### Screens

| Screen | Job | Layout |
|---|---|---|
| **Today** (front-desk dashboard) | Run the day: check people in, see who's waiting and for how long, and get finished patients paid and out. | Four columns (Due next · Waiting, with a live wait timer · In exam, with room and vet · Ready to check out) under a check-in search bar, plus a narrow right column of callbacks, refill requests and results to pass on. |
| **Schedule** | See every vet's day; book, move or cancel appointments without double-booking. | 15-minute rows down the left, one column per vet, appointments shown as blocks with the patient card and reason; date strip and day/week switch on top. |
| **Book appointment** (panel, not a separate page) | Book a phone caller in under a minute. | Panel that slides in from the right over the Schedule: find client and pet → reason (sets the length) → vet → suggested open slots → confirm, with a reminder on/off switch. |
| **Clients** (search) | Find a household by owner name, pet name, phone number or microchip. | One large search box over a results table you can move through with the keyboard: owner, pets, phone, balance, last visit. |
| **Client** (household) | Everything about the owner: contact details, their pets, what they owe, and messages sent. | Header with contact details and balance; pet cards on the left; a timeline of visits, invoices and messages on the right. |
| **Patient record** | Give whoever is holding the animal the key clinical facts in five seconds, then the full history. | Header that stays pinned (patient card, age, sex/neutered, weight trend, owner) above a wide visit-history column and a summary column: problems, current meds, vaccines due, allergies, next appointment. |
| **Visit** (exam note) | Record the consult and log each charge as it happens, so nothing is missed at checkout. | Patient header; on the left, a vitals row then Subjective / Objective / Assessment / Plan (SOAP) notes; on the right, a running "charges this visit" list picked from the price list. |
| **Checkout** | Turn the visit's charges into an invoice, take payment, and book the next visit before the client leaves. | Invoice in the centre (line items, quantity, price, tax, discount, total), payment panel on the right (amount due, payment method, split payment, change), and buttons along the bottom: take payment · email/print receipt · book follow-up. |
| **Billing** | Keep the money straight: unpaid invoices, payments received, and end-of-day cash-up. | Tabs (Unpaid · Payments · End of day) over a filterable table with a totals row; End of day compares takings by payment method with the counted cash drawer. |
| **Reminders** | Bring animals back for vaccines, dental checks and check-ups coming due. | List filtered by month and grouped by reminder type, showing whether each client has been contacted, with bulk "Send SMS/email" and "Mark as called". |
| **Settings** | Hold the data other screens depend on: services and prices, staff and working hours, rooms, tax, clinic details. | Section list on the left, form or editable table on the right. |

**Shared across screens:**
- **Navigation:** a top bar with Today · Schedule · Clients · Billing · Reminders, a global search (opened with "/") and a "New appointment" button. I chose a top bar over a sidebar so the Schedule has room for the vet columns. On a phone, it collapses into a menu that still lists every screen.
- **Appointment status:** Booked → Arrived → In exam → Ready to check out → Paid. Today, Schedule and Checkout all use these same labels, and status is always shown as text as well as colour.

### Questions that would change this plan

1. **Do vets write clinical notes in this app, or is it for the front desk only?** If front desk only, Visit goes away and the Patient record gets simpler.
2. **Card payments:** should the app connect to a card terminal, or only record payments taken elsewhere?
3. **Schedule columns:** one per vet or one per exam room?
4. **Reminders:** are SMS/email reminders needed in the first version, or can Reminders wait?
5. **Branding:** is there an existing logo or brand colours?

---

## F4

I didn't create any files. The folder is empty, so this is a new product with no existing design system. No design-reference tools were connected, so the visual direction below comes from the paperwork a vet clinic already uses rather than from other apps.

**Assumptions** (correct any that are wrong):
- The main users are front-desk staff working at a desktop screen. Vets use a tablet in the exam room for notes and records.
- Phone use is occasional, mostly checking the schedule.
- Screens are dense and practical, and the app runs in light mode.

### Visual direction

**Based on the clinic's own paperwork:**
- **Appointment book:** scheduling is a time grid with a column per vet, not a month calendar.
- **Kennel card:** the card clipped to a kennel becomes a patient ID strip (the signature element, described below).
- **Medical chart (SOAP notes):** visit notes have four fixed sections (Subjective, Objective, Assessment, Plan) instead of one free-text box.
- **Printed invoice or estimate:** billing looks like the itemized receipt the owner takes home.
- **Treatment-room whiteboard:** the front-desk dashboard is a board showing where each patient is.
- **Vaccine reminder postcard:** due dates appear as text, like "Rabies due 14 Oct", not as colored dots.

**Signature element:** the kennel-card strip. It shows:
- the pet's name in large type
- species, breed, sex and age
- weight and how it has changed
- the owner and their phone number
- labeled alerts, like "Bites", "Allergy: penicillin" or "Diabetic"

It looks the same everywhere a patient appears, so staff never mix up two pets named Bella.

**Defaults I'm avoiding:**
- a row of number tiles and a revenue chart at the top of the dashboard
- a month calendar as the main scheduling view
- a grid of patient cards with round pet photos
- status shown only by color
- paw-print decoration or cutesy pastel pet branding

### Screens

**App frame:** a top bar with a search box that's always visible, and links to Today, Schedule, Clients and Billing. On a phone or tablet, the same four links move to a bar at the bottom of the screen.

| # | Screen | Job | Layout |
|---|---|---|---|
| 1 | **Today** (front-desk dashboard) | Run the front desk: see who's expected, waiting, in a room or ready to pay, and move each one to the next stage in one click | Four columns (Expected · Waiting · In room · Checkout) holding kennel-card rows with times, plus a narrow right panel for today's callbacks, refill requests and reminders due |
| 2 | **Schedule** | Book, move and cancel appointments across vets and rooms | Day view with times down the left and one column per vet, a switch to week view, and a click on an empty slot opens the booking panel |
| 3 | **Book appointment** (panel over Schedule or Today) | Book a visit in under a minute while on the phone | Panel from the right, top to bottom: find owner or pet → reason (sets the usual length) → vet → next open slots → a button like "Book 10:30 with Dr. Okafor" |
| 4 | **Clients & patients** | Find a household or animal by owner name, pet name, phone or microchip | One wide search box above a dense table grouped by owner, with each owner's pets listed underneath with species and next due date |
| 5 | **Client account** | One household: contact details, all their pets, what they owe | Owner details and balance at the top, a row of kennel cards (one per pet), and their invoices and payments below |
| 6 | **Patient record** | Everything about one animal at a glance, with its history close at hand | Kennel-card strip across the top; past visits (newest first) take the left two-thirds; the right third shows vaccines due, current medications, allergies and weight trend |
| 7 | **Visit note** | The vet records the exam and treatment, and charges are added as they go | The four SOAP sections in the main column, with a running list of charges on the right that becomes the invoice |
| 8 | **Checkout** | Turn the visit into a bill, take payment and book the follow-up | Receipt-style invoice in the center, payment panel on the right (method, split payment, amount received), and follow-up or reminder booking below |
| 9 | **Billing** | Track unpaid and part-paid invoices and close out the day | One line of end-of-day totals by payment method, above a filterable invoice table sorted by age, with status written as words |

**Later, not main screens:** price list and services, staff and rooms, opening hours, a batch screen for sending vaccine reminders, and treatment estimates (these can reuse the Checkout layout with an "Estimate" status).

**Three questions that would change this plan:**
1. Do vets write their notes in this app? If not, drop screen 7 and have the front desk enter charges at Checkout.
2. Do you need treatment estimates now, or can they wait?
3. Should Checkout take card payments through a connected card reader, or only record payments made on a separate terminal?

---

## EF1

### Plan: side-by-side comparison of up to three cars (Chicane)

This is only a plan. No files were changed. I read the tokens, primitives, card, both drawers, the URL-state helper, the saved store and the credits route. No reference-research tools were connected (Refero, Mobbin, 21st.dev), so the direction below borrows only structure from things car buyers already know. All visual styling comes from the site's existing design system.

### What already exists and shapes this plan

- **Look and feel:** square corners, thin divider lines, three widths of the Archivo font (`display`, `semiwide`, and `narrow` with fixed-width numbers), Newsreader serif for descriptions, and the traffic-yellow `signal` accent used sparingly. Dark `tarmac` blocks appear only for the main call to action.
- **Paint chips:** each car has a short code and a paint colour in `present()` (`992`, `E46`, `R34`). That is the natural compact label for a car in the comparison.
- **URL state:** `?car=` opens the detail drawer and the back button closes it (`car-param.ts`). It only changes its own parameter, so it will also work on another route.
- **Copy conflict:** the saved drawer's button already says "Compare them in the inventory" (`saved-drawer.tsx:117`), but it only filters the inventory. That wording has to change once "compare" means something real.
- **No test runner** is installed. Only lint and build are available.

### Direction (structure only)

- **Magazine comparison-test spec box:** labels in a left column, the cars across the top, rows grouped into sections. This is the backbone of the table.
- **Auction lot sheet:** the history facts (owners, seller, highlights) and the serif write-up get their own section rather than being mixed into the specs.
- **Paint chip deck:** the site's existing chips identify each car wherever space is tight (tray, sticky header, mobile).
- **Things I'd leave out:**
  - Rounded shadowed card per column.
  - Green/red "winner" colouring or a total score. A 225 hp '67 Mustang isn't a worse car than a 591 hp RS6.
  - Radar charts.
  - Horizontally scrolling tables on mobile.
  - Drag-to-reorder.
  - Compare checkboxes that only appear on hover.
  - Opening the comparison as a modal on top of the detail drawer.

### Structure

**Route (recommended): `/compare?cars=id1,id2,id3`.**
- It needs full page width: a label column plus three car columns doesn't fit the 47rem detail drawer.
- A comparison deserves its own link, title and back-button behaviour, just as a single car has `?car=`.
- The page is built on the server from the static listings data.
- Next 16 passes `searchParams` to pages as a Promise (checked in `node_modules/next/dist/docs/.../page.md:14`).

**Page parsing:** split `cars` on commas, drop unknown ids, remove duplicates, keep the first three. It also sets a page title such as `Compare: 911 Carrera S, M3, Skyline GT-R | Chicane`.

**Where the selection lives:**
- **On the home page:** a new `compare-store.ts`, an ordered list of at most three ids. It works like `saved-store.ts` (`useSyncExternalStore`, localStorage, syncs across tabs). I'd pull the shared logic of the two stores into a small helper and leave `useSaved`'s API unchanged.
- **On `/compare`:** the URL is the source of truth. Edits update it with `window.history.replaceState`, which the Next 16 docs say integrates with the router (`04-linking-and-navigating.md:345`). Edits also update the stored list. Simply opening a shared link does not overwrite the viewer's own tray.

**`MarketProvider`** gains `compare`, `toggleCompare(id)` (returns `added`, `removed` or `full`) and `clearCompare`. The compare page wraps itself in `MarketProvider` and mounts the existing `VehicleDrawer`, so hearts and the detail drawer work there too.

**Files:**

| New | Changed |
|---|---|
| `app/compare/page.tsx` (server: parsing, metadata, slim header copied from `credits/page.tsx`) | `market-provider.tsx` |
| `components/compare-view.tsx` (client: table, filters, picker) | `vehicle-card.tsx`, `vehicle-drawer.tsx` (toggle) |
| `components/compare-tray.tsx` | `saved-drawer.tsx` (copy and shortcut) |
| `lib/compare.ts` (pure: parse, row config, "rows that differ", best value in a row) | `app/page.tsx` (mount the tray) |
| `CompareToggle` in `primitives.tsx`, next to `FavoriteButton` | `saved-store.ts` (shared helper) |

### Choosing cars

- **Grid card:** a small square "☐ Compare" / "✓ Comparing" label on the photo, left of the heart. It uses the same style as the Featured badge. It is always visible, including on touch.
- **List row:** the same toggle next to the heart.
- **Detail drawer:** a "Compare" toggle in the header next to the heart. The drawer is where people make decisions, so this is the most important entry point.
- **Saved drawer:** rename the current button to "Show them in the inventory". When 2–3 cars are saved, add "Compare these N", which opens `/compare` with those cars.
- **When three are already chosen:** toggles on other cars stay enabled. Pressing one changes nothing and says "Comparison is full. Remove a car to add the 1997 Supra." in the tray and through a screen-reader announcement. Disabled buttons would give no explanation.

**Compare tray (home page only):**
- A fixed bar at the bottom on the dark `tarmac` surface. It appears when one or more cars are chosen and sits below the drawers (`z-40`).
- It slides up using the drawers' existing easing, and each chip draws in with the existing `animate-chip` animation.
- The footer gets extra bottom padding while the tray is visible, so nothing is hidden behind it.

```
Desktop:  [■992 911 Carrera S ×] [■E46 M3 ×] [ empty: third car ]    Clear   [ Compare 2 cars ]
Mobile:   ■992 ■E46 □             Clear   [ Compare ]      (removing is done from the cards)
```

With one car chosen, the button is replaced by the text "Pick one more to compare".

### Compare page layout

**Desktop (1280px):**
```
Chicane                                                      Back to the inventory
────────────────────────────────────────────────────────────────────────────────
Side by side  (display)                  serif standfirst naming the three cars
                                         [switch] Only rows that differ   Copy link
═══════════════���════════════════════════════════════════════════════════════════
              │ ■992 911 Carrera S ♡ × │ ■E46 M3 ♡ ×       │ ■R34 Skyline GT-R ♡ ×   ← sticky header
              │ [photo 3:2]            │ [photo]           │ [photo]
THE DEAL      │                        │                   │
Price         │ $128,900               │ $42,500 ▪ Lowest  │ $289,000
Mileage · Listed · Location · Seller
PERFORMANCE   Power ▪ · 0–60 ▪ Quickest · Engine · Gearbox · Drivetrain
THE CAR       Year · Body & generation · Exterior (swatch) · Interior · Owners ▪ · Collection
THE STORY     Highlights (✓ list) · Description (serif)
              │ [View full listing]    │ ...               │ ...
```

- **Table:** one real `<table>` with fixed column widths. The label column is 11–13rem and the car columns are equal.
- **Rows** use the thin row dividers from the drawer's spec list. Each section starts with the heavy `border-t-2 border-ink` rule the drawer uses under the price.
- **Numbers** use the `narrow` type.
- **Sticky header:** only the compact row (chip, model, price, heart, remove) sticks to the top. The photos scroll away.
- **Two cars:** the third column shows an "Add a car" slot, so the layout stays stable and invites a third choice.

**Tablet (768px):** the same table with a 9rem label column and smaller photos.

**Mobile (375px, below `md`):** each label sits on its own line with the values in columns underneath, so the numbers stay side by side without scrolling sideways:
```
■992 $128.9k │ ■E46 $42.5k │ ■R34 $289k      ← sticky chip strip (formatPriceShort already exists)
[img]          [img]          [img]
POWER
443 hp         333 hp         276 hp
```
- Long rows (Interior, Highlights, Description) stack one car at a time, each introduced by its chip.
- Changing table elements to CSS grid can strip table meaning in Safari, so the table gets explicit ARIA roles (table, row, column header, row header, cell).

### Interactions on the compare page

- **"Best in row" markers:** only for Price (lowest), Mileage (lowest), Power (highest), 0–60 (quickest) and Owners (fewest). Year gets none. No marker when all values are equal. The marker is the yellow bullet already used for tags, plus a text word, so it never relies on colour alone.
- **Only rows that differ:** a switch that hides rows where every car has the same value, and hides a section's heading when all its rows are hidden. It announces "4 rows hidden". It is off by default and disabled with only one car.
- **Remove (×):** the column disappears straight away, without animating table cells. The URL updates and focus moves to the next column's header, or to the add slot.
- **Add a car:** opens a Radix dialog, following the drawer pattern. It has a search box and a plain list of all 12 cars (chip, title, price, mileage). Cars already being compared show "Comparing" and can't be picked. After adding, focus moves to the new column. With 12 cars there's no need to reuse the full filter panel.
- **Open a car:** the model name or "View full listing" opens the existing `VehicleDrawer` with `openCar(id, compareIds)`. Previous/next then step only through the compared cars, and Back closes the drawer and stays on `/compare`.
- **Copy link:** the same pattern as the drawer's `CopyLink`, copying `/compare?cars=…`.

**Edge cases:**
- **0 cars:** "Pick two or three cars to compare." plus a "Browse the inventory" link and the add slots.
- **1 car:** the column is shown with a prompt to add another.
- **Removed or sold id in a link:** a note saying "One car in this link is no longer listed."
- **More than 3 ids:** the first three are used.
- **Duplicate ids:** removed.

### Accessibility

- **Table labelling:** a hidden caption lists the cars. Car names are column headers and spec names are row headers, so a screen reader reads "Power, 2004 BMW M3: 333 hp".
- **Toggles:** they use `aria-pressed` and include the car in their name ("Add 2004 BMW M3 to comparison"). A single polite announcement area on the page reports adds, removals and the "full" message.
- **Tap targets:** at least 44px, the same as the existing `size-11` icon buttons.
- **Focus rings** reuse the existing `:focus-visible` styles, including the `on-dark` variant for the tray.
- **Reduced motion** is already handled site-wide and by `MotionConfig`.
- **Minor fix:** on `/compare` the drawer's fallback focus target (`#saved-trigger`) doesn't exist, so it needs a local fallback.

### How it would be verified once built

- **Checks:** `npm run lint` and `npm run build`, which also type-checks.
- **Browser:** `npm run dev` with Playwright at 375, 768, 1280 and 1440px, for home with the tray and for `/compare` with 0 to 3 cars and a bad id.
- **Keyboard:** tab through the tray, the table, the picker and the drawer opened from `/compare`.
- **Review:** after that, `visual-design-judge` on the screenshots and `adversarial-jury` on the code.

### Decisions for you

1. **Unit tests:** the logic in `lib/compare.ts` is easy to test, but there's no test runner. Should Vitest be added, or do lint, build and browser checks do for now?
2. **"Best in row" markers:** I've kept them neutral and limited to five rows. If you'd rather the comparison make no judgement at all, drop them.
3. **How long the selection lasts:** I've planned localStorage, matching saved cars, so a comparison survives closing the tab. sessionStorage would clear it with the tab instead.

---

## EF2

I haven't changed any files. This plan comes from reading the home page, the data (12 listings), the design tokens, the saved-cars store, the `?car=` URL handling, and the car card, detail drawer, saved-cars drawer and nav. I had no screen-reference or component-search tools connected, so the structure borrows from car-world documents instead: a magazine group-test data panel, a window sticker and an auction lot header. All styling reuses what the site already has.

### Key decisions

1. **The comparison gets its own page, `/compare?cars=id1,id2,id3`, not a drawer.** Three columns need the full width, the link can be shared with a real title ("992 vs E46 vs R34 | Chicane"), and Back works as expected. The existing detail drawer still opens on top of it.
2. **The compare list is separate from Saved.** Saved means "interested in"; the compare list means "choosing between these now", and people will often save more than three cars. It would live in a new `compare-store.ts` that copies the saved-cars store: kept in the browser, still works if storage is blocked, holds up to 3 cars in the order added.
3. **On `/compare`, the address bar decides which cars show.** The stored list only changes when the user adds or removes a car, so opening someone else's link doesn't overwrite your own list.
4. **The cap of 3 means every column fits at every screen width.** Even on a 375px phone there's no sideways scrolling, which is why the limit is worth having.
5. **Only data the listings already contain.** No invented weight, torque, price-per-hp or overall "winner" score.

### Where you add cars

- **Detail drawer:** a "Compare" toggle next to the heart in its header.
- **Saved drawer:** a compare toggle on each row. When two or more are picked, the footer shows "Compare 2 cars". The current button, "Compare them in the inventory", only filters the inventory to saved cars, so it becomes "Show them in the inventory".
- **List-view rows:** a toggle next to the heart. Grid cards stay as they are; the heart remains their only action.
- **Adding a fourth car:** the button isn't disabled, because a disabled button can't say why. Clicking it tells the user, including screen-reader users, "Compare holds three cars. Remove one to add the 992."

**Compare tray (home page).** A bar fixed to the bottom of the screen, in the site's dark colour, shown once at least one car is picked:
```
Compare  [■ 992 ×] [■ E46 ×] [ + ]              Clear   Compare 2 cars →
```
- Each slot shows the car's paint colour and its short code (992, E46, R34…). The codes already exist in the data and no two cars share one.
- With only one car picked, the main button becomes the text "Add one more to compare".
- It sits below dialogs but above the page. While it's visible the page gets extra bottom space so it doesn't cover the footer.
- It slides up once when it first appears and has no other animation.

### Compare page layout

- **Header:** like the Photo credits page (logo, "Back to inventory", "Copy link"). The main site nav can't be reused because its links only jump to sections on the home page.
- **Title:** "992 vs E46 vs R34", with a line underneath naming each car in full.
- **Body:** one real HTML table (one column per car, one row per spec), so screen readers announce "Power, 2004 BMW M3, 333 hp". The page is capped at about 80rem wide so the eye doesn't travel too far across three values.

```
                  ┌────────────┬────────────┬────────────┐
                  │   photo    │   photo    │  + Add a   │ scrolls away
                  │    4:3     │    4:3     │    car     │
                  ├────────────┼────────────┼────────────┤
                  │ 2021 Porsche│ 2004 BMW  │            │ STICKY row
                  │ 911 Carrera S│ M3       │            │
                  │ $128,900   │ $41,500    │            │
                  │ View · ♥ · ×│ View · ♥ · ×│           │
PRICE & HISTORY   ├────────────┴────────────┴────────────┤
Price             │ $128,900    ■ $41,500                │
Mileage           │ ■ 18,400 mi   96,000 mi              │
Drivetrain        │ RWD on both  (identical → one merged, muted cell)
```

**Row groups:**
- **Price & history:** Price, Mileage, Owners, Listed, Seller, Location.
- **Performance:** Engine, Power, 0–60 mph, Gearbox, Drivetrain.
- **The car:** Generation and body, Exterior (with a paint swatch), Interior, Collection.
- **Highlights:** each car's highlight list and tags, lined up at the top.
- **Left out:** the long descriptions. Three paragraphs side by side are unreadable; "View" opens the full listing.

**Showing differences:**
- **Leading values:** where "better" is plain fact, the leading value gets the site's small yellow square: lowest price, lowest mileage, most power, quickest 0–60, fewest owners.
  - A one-line key under the title explains the square, and screen readers hear a word like "Lowest" rather than relying on the colour.
  - Tied values all get the square. No square if every value is the same.
- **Identical rows** collapse into one muted cell, so sameness shows at a glance.

**Column actions:**
- **View** opens the existing detail drawer. Its previous/next arrows step through the compared cars ("1 of 3").
- **The heart** saves the car, as it does elsewhere.
- **×** removes the column. Focus then moves to the next column, and screen readers hear "Removed 2004 BMW M3. Comparing 2 cars."

**"Add a car" slot:** opens a picker shaped like the saved drawer. Saved cars come first, then the rest, leaving out cars already compared. There are only 12 cars, so no search is needed.

**Phones (under 640px):**
- The label column goes away. Each label becomes a small full-width caption above its 2–3 values, about 105px per column.
- The sticky row shrinks to the swatch, the short code and a short price ("$128.9k"), so you can still tell the columns apart while scrolling.
- Photos stay, as small 4:3 thumbnails.
- This needs CSS that can strip table meaning from the markup in some browsers. The screen-reader tree has to be checked, with ARIA table roles added back if needed.

**Other states:**
- **No cars, or a bad link:** "Pick two or three cars to compare." It shows the saved cars to pick from, or "Browse the inventory" if nothing is saved.
- **One car:** a single column, with "Add another car to compare it against" in the empty slot.
- **Messy links:** unknown IDs, duplicates and anything past three are dropped quietly, and the address bar is corrected without adding a Back step.

### What would change

| New | Purpose |
|---|---|
| `src/lib/compare-store.ts` | The stored compare list, capped at 3 |
| `src/lib/compare.ts` | Read IDs from the link, build compare links, row definitions (label, group, value, which direction leads) |
| `src/app/compare/page.tsx` | The page itself. In this Next.js version the query string arrives as a Promise and must be awaited. It also sets the page title and wraps the table in the existing site context so the detail drawer works |
| `src/components/compare-view.tsx` | The table, empty slots and address-bar updates |
| `src/components/compare-picker.tsx`, `compare-tray.tsx` | The "Add a car" picker and the home-page tray |

- **Existing files that change:** `page.tsx` (adds the tray), `vehicle-drawer.tsx`, `saved-drawer.tsx`, and `vehicle-card.tsx` (list rows only).
- **No new dependencies.**
- **One thing to get right:** when the comparison updates the address bar, it has to keep the `car` parameter and the existing history state, or the detail drawer's Back behaviour on `/compare` breaks.

**Checks once it's built:**
- `npm run build` and `npm run lint`.
- Screenshots at 375, 768, 1280 and 1600px: no sideways scrolling with three cars on a phone, the sticky row working, and long values like "3.0L twin-turbo flat-six" wrapping cleanly.
- A keyboard tab-through, screen-reader table reading, reduced motion, blocked storage, a junk shared link, and Back closing the drawer on `/compare`.

**Decisions for you:**
- **Compare button on grid cards?** I left it off to keep the cards clean. If you want it, it would be a second small button beside the heart on the photo.
- **Keep the yellow "leads the row" square?** It states facts, not a verdict, but you might prefer no highlighting at all.
