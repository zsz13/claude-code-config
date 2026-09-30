# Composition plan test: the ten plans

Each plan is the complete final answer of one fresh headless session to
[prompts/composition-plan.md](prompts/composition-plan.md), under the protocol in
[composition-protocol.md](composition-protocol.md). The header line of each run
records the skills it invoked and its 21st calls, both counted from its
stream-json transcript. No run invoked a skill, so, by the protocol, none is
informative about the paragraph under test.

---

## before-1

Skills invoked: none. 21st: connected, 0 calls.

### Homepage plan: "Paddock", an enthusiast and premium used-car marketplace

1. **Header / nav**
   - **Job:** Shows where you are on the site, keeps search one tap away and shows how many cars you've saved.
   - **Layout:** A sticky, slim bar that starts transparent over the hero and turns solid on scroll: wordmark on the left, links in the center (Buy, Sell, How it works), and a favorites heart with a count badge on the right; on mobile the links move into a slide-in drawer.

2. **Hero + search**
   - **Job:** Sets the premium tone at once and gets people into inventory within one interaction.
   - **Layout:** A full-bleed photo of a car in a moody setting with a dark gradient, a large headline on the left, and a search panel (make, model, max price, body style → "Show 248 cars") with quick-filter chips underneath ("Manual only", "Under 20k mi", "Air-cooled"); on mobile the panel stacks below the headline.

3. **Trust strip**
   - **Job:** Earns credibility before anyone scrolls further.
   - **Layout:** A thin row of 4 stats with icons (150-point inspection, 7-day returns, nationwide delivery, 1,200+ cars sold) whose numbers count up when they come into view; on mobile it scrolls sideways.

4. **Browse by collection**
   - **Job:** Gives a way in for people who are browsing without a specific car in mind.
   - **Layout:** A row of 6 tall image tiles (Sports Coupés, Grand Tourers, Modern Classics, Track Weapons, Performance SUVs, Electric Performance) that zoom slightly on hover and act as filter presets when clicked; on mobile it becomes a swipeable carousel.

5. **Car of the week spotlight**
   - **Job:** Adds an editorial, enthusiast feel that sets this apart from a generic listings site.
   - **Layout:** A split card: a large image on the left and, on the right, a short story, a spec grid (power, 0–60, gearbox, owners), the price and a "View details" button; on mobile the image sits on top.

6. **Inventory (core section)**
   - **Job:** Lets people search, filter, compare and save cars.
   - **Layout:** A sticky filter sidebar on the left (price and mileage range sliders, year, make, body, transmission, drivetrain, fuel, color). Above the grid: a result count, removable chips for active filters, a sort menu and a grid/list toggle. The grid shows 3 cards per row on desktop, 2 on tablet and 1 on mobile, where the filters open as a bottom sheet with a "Show N cars" button.
   - **Vehicle cards:** A photo carousel that changes on hover or swipe, a heart button to save, badges (One owner, No accidents, Manual), the title, a specs line (miles · gearbox · hp), and the price with an estimated monthly payment.

7. **How it works**
   - **Job:** Explains a high-value online purchase so people feel less uneasy about it.
   - **Layout:** A 4-step timeline (Browse → Review inspection report → Reserve with a refundable deposit → Delivered) with a connecting line that draws in as you scroll; on mobile the timeline runs vertically.

8. **Owner stories**
   - **Job:** Provides social proof from real enthusiasts.
   - **Layout:** 3 testimonial cards in a row, each with a buyer photo, a quote, the car purchased and a star rating; on mobile they become a snap-scroll carousel.

9. **Sell / alerts CTA band**
   - **Job:** Collects leads from people who aren't ready to buy today.
   - **Layout:** A full-width dark band split in two: "Sell your car: get an offer in 24h" on the left, and "Get alerts for new 911s, M cars…" with an email field on the right; the halves stack on mobile.

10. **Footer**
    - **Job:** Holds full navigation, trust signals and legal links.
    - **Layout:** A dark footer with 4 link columns (Buy, Sell, Company, Support), a newsletter and social links, an oversized wordmark along the bottom edge, and a row of legal links; on mobile the columns collapse into accordions.

**Overlays (on top of the page, not part of the scroll):**
- **Vehicle details:** A right-side drawer on desktop and a full-screen sheet on mobile, containing a photo gallery, a spec table, highlights, the inspection summary, a payment estimator, and Save and Reserve buttons.
- **Favorites:** A drawer that opens from the header heart and lists saved cars.
- **Mobile filters:** The bottom sheet described in the inventory section.

The Mobbin and Refero design-reference servers aren't authorized in this session. You can connect them through their claude.ai connector settings or `/mcp` if you want reference screens used later.

---

## before-2

Skills invoked: none. 21st: connected, 0 calls.

The working name is **Paddock**. It has a dark, editorial look with one accent color.

1. **Header**
   - **Job:** Navigation, plus quick access to saved cars.
   - **Layout:** A sticky bar that is transparent over the hero and turns solid on scroll: logo on the left, links in the center, and a heart with the saved-car count on the right. On mobile, a menu button opens a full-screen menu.

2. **Hero + search**
   - **Job:** Set the premium tone and get users into inventory in one step.
   - **Layout:** A full-width car photo with a dark gradient and the headline on the left. A search bar (make/model, body style, max price, Search) sits along the bottom edge; on mobile it shrinks to one field that opens a search panel.

3. **Browse-by chips**
   - **Job:** One-tap shortcuts into enthusiast niches (Manual only, Air-cooled, JDM, V8, Wagons, Under 30k mi).
   - **Layout:** A horizontally scrolling row of icon chips; tapping one applies that filter and scrolls down to the inventory.

4. **Curated collections**
   - **Job:** Hand-picked themed groups of cars, so the site feels built by enthusiasts rather than like a classifieds list.
   - **Layout:** An uneven grid of one large tile and four small ones, each with a photo, title and listing count; it becomes one column on mobile.

5. **Inventory**
   - **Job:** The main place to browse, filter and compare cars.
   - **Layout:** A sticky filter sidebar on the left (make, price, mileage, year, transmission, drivetrain, body style, color) and a 3-column grid of car cards on the right. The grid has a result count, a sort menu and removable active-filter tags. On mobile, filters move into a panel that slides up from the bottom and the grid becomes one column.
   - **Vehicle card:** A photo that cycles through the gallery on hover (swipe on mobile), a heart toggle, badges (Inspected, No accidents, Price drop), year/make/model, price, and a spec row (miles · gearbox · location).

6. **How it works / trust**
   - **Job:** Make buying a used car online feel safe.
   - **Layout:** A 4-step horizontal timeline (Inspect → Verify history → Deliver → 7-day return) with icons and short copy; it stacks vertically on mobile.

7. **Recently sold**
   - **Job:** Show that real cars sell here, and at what prices.
   - **Layout:** A slowly auto-scrolling strip of small sold-car cards showing the final price and days to sell; it pauses on hover.

8. **Price alerts sign-up**
   - **Job:** Bring visitors back by offering email alerts for their saved searches.
   - **Layout:** A full-width band in a contrasting color, with the headline on the left and an email field and button on the right; it stacks on mobile.

9. **Footer**
   - **Job:** Links, trust signals and a finished look at the bottom of the page.
   - **Layout:** Logo, tagline and social icons above 4 link columns, then a bottom row with legal links and a region/currency selector. The link columns become expandable sections on mobile.

**Overlays (open on top of the page)**
- **Vehicle details:** Opens from any card, as a side panel on desktop and full screen on mobile. It shows the photo gallery with thumbnails, price and a monthly-payment estimate, a spec grid, highlights, a history-report summary, seller info, and a "Request viewing" button.
- **Favorites drawer:** Slides in from the heart in the header and lists saved cars, which are stored in the browser (so they survive a reload).

The Mobbin and Refero design-reference tools need authorization before I can use them for inspiration during the build. You can connect them in your claude.ai connector settings or with `/mcp`.

---

## before-3

Skills invoked: none. 21st: connected, 0 calls.

### Homepage sections, in order

1. **Sticky header**
   - *Job:* Keep brand, navigation, search and saved cars within reach on every scroll position.
   - *Layout:* A slim bar with the wordmark on the left, Buy / Sell / How it works in the centre, and a favourites heart with a count badge plus a "Sell your car" button on the right. It starts transparent over the hero, turns solid once you scroll, and becomes a hamburger drawer on mobile.

2. **Hero + search**
   - *Job:* Set the premium, enthusiast tone right away and get users into the inventory in one step.
   - *Layout:* A full-bleed photo of a car with a dark gradient and a left-aligned headline. Over it sits a search panel (make, model, max price, body style, Search) with quick-filter chips underneath ("Manual only", "Under 10k miles", "Air-cooled"). On mobile it all stacks into one column.

3. **Trust strip**
   - *Job:* Build credibility before users start browsing.
   - *Layout:* One row of four stats that count up when scrolled into view: cars inspected, 150-point inspection, nationwide delivery, 7-day returns. On mobile it becomes a 2×2 grid.

4. **Browse by collection**
   - *Job:* Let enthusiasts browse by what they're after rather than only by make or model.
   - *Layout:* A horizontal scrolling row of tall image tiles (Track-Ready, Modern Classics, Grand Tourers, Manual Gearbox, Electric Performance), each with a label and a live count. It's a swipe carousel on mobile.

5. **Featured picks**
   - *Job:* Show a few standout listings with an editorial feel.
   - *Layout:* An uneven tile grid with one large feature card and three or four smaller cards. Each card has a short "why we love it" note, and the grid collapses to a single stack on mobile.

6. **Inventory with filters** (the main section)
   - *Job:* Let users narrow the stock down and compare cars side by side.
   - *Layout:*
     - **Filters:** a sticky sidebar on the left with make, price and year ranges, mileage, transmission, drivetrain, body style, colour and fuel.
     - **Toolbar:** result count, removable chips for active filters, a sort menu and a grid/list toggle.
     - **Results grid:** three columns on desktop, two on tablet, one on mobile.
     - **Vehicle cards:** a swipeable photo gallery, a heart button to save the car, badges (One Owner, No Accidents, Manual), a row of key specs, and the price with an estimated monthly payment.
     - **Mobile:** the filters move into a bottom sheet with a sticky "Show N cars" button.

7. **How it works**
   - *Job:* Explain how buying works: browse → inspect report → reserve → delivered.
   - *Layout:* Four numbered steps in a row joined by a line that draws itself as you scroll. On mobile it becomes a vertical timeline.

8. **Owner stories**
   - *Job:* Show social proof from real buyers.
   - *Layout:* Three quote cards, each with the buyer's photo, the car they bought and a star rating. It's a swipe carousel on mobile.

9. **Sell your car banner**
   - *Job:* Attract sellers, since a marketplace needs stock as well as buyers.
   - *Layout:* A split banner with a headline and a licence plate/VIN field plus "Get an offer" on the left, and a cut-out car image on the right. It stacks on mobile.

10. **Footer**
    - *Job:* Close the page with navigation, trust signals and a new-arrivals email signup.
    - *Layout:* A dark footer with four link columns, an email signup box, social icons, and a bottom row with legal links and region settings. On mobile the link columns collapse into accordions.

### Overlays (not part of the page's scroll order)
- **Vehicle details:** a large modal on desktop, full-screen on mobile. It has a photo gallery with thumbnails, a specs table, highlights, a vehicle history summary, the inspection report and price with Reserve and Save buttons. It opens from any vehicle card and closes with Esc or a swipe down.
- **Favourites panel:** slides in from the right via the header heart. It lists saved cars with a "compare" option, and saved cars stay saved in the browser between visits.

Two design-research tools I have access to (Mobbin and Refero) aren't authorised, so I couldn't use them. You can connect them through your claude.ai connector settings or `/mcp` if you want me to use them for visual references during the build.

---

## before-4

Skills invoked: none. 21st: connected, 0 calls.

### Homepage plan: enthusiast and premium used-car marketplace

1. **Header / nav**
   - **Job:** Get people around the site and give them one-tap access to their saved cars.
   - **Layout:** Slim sticky bar with the logo on the left, Buy / Sell / How it works in the middle, and a heart with a saved-car count plus a "Browse cars" button on the right. The background blurs once you scroll, and on mobile the links fold into a slide-out menu.

2. **Hero + search**
   - **Job:** Set a premium tone and get shoppers into the listings within one interaction.
   - **Layout:** Full-width photo of a car with a dark fade and a bottom-left headline. A search bar with make, model, max price and body style sits over the bottom edge of the photo. On mobile it shrinks to one search field and a "Filters" button.

3. **Trust strip**
   - **Job:** Answer the main worry about buying used, "can I trust this car?", before people start browsing.
   - **Layout:** Thin row of four icons with short labels: 150-point inspection, verified history, 7-day return, nationwide delivery. It becomes a sideways scroll on mobile.

4. **Collections rail**
   - **Job:** Let people browse by enthusiast theme instead of dry filters: Air-cooled, Manuals only, JDM icons, V12 grand tourers, Track-ready, Under $60k.
   - **Layout:** Sideways-scrolling row of tall photo tiles, each with a name and a car count. Tapping a tile applies that filter to the inventory below and scrolls down to it.

5. **Inventory**
   - **Job:** The core of the site: filter, sort, save cars and open a car's details.
   - **Layout:** Filter sidebar on the left (price, year, mileage, gearbox, drivetrain, body style) and a 3-column grid of car cards on the right, with a result count, sort menu and removable filter tags on top.
     - On mobile the sidebar becomes a slide-up panel opened from a floating "Filters (n)" button, and the grid drops to 1 column.
     - Each card has a photo that swaps on hover, a heart button, tags like "Manual" or "1 owner", key specs, the price and an estimated monthly payment.

6. **Editor's pick**
   - **Job:** Tell one car's story at length. This mixes up the pace of the page and signals that the listings are curated.
   - **Layout:** Split row with a large photo gallery on about 60% of the width and a short write-up, spec list and "View details" button on the rest. It stacks on mobile.

7. **How it works**
   - **Job:** Make buying remotely feel safe by showing the process: inspect, then finance, then delivery.
   - **Layout:** Three numbered steps side by side, joined by a thin line that draws itself as you scroll. They stack vertically on mobile.

8. **Sell your car**
   - **Job:** Attract sellers to bring in new listings.
   - **Layout:** Full-width dark band with a one-line pitch, a licence plate / VIN input and a "Get an offer" button.

9. **Footer**
   - **Job:** Links, newsletter sign-up and a confident sign-off.
   - **Layout:** Four link columns and a newsletter field, a very large faded logo across the bottom, and a legal and social row. The link columns collapse into expandable sections on mobile.

These two aren't page sections but open on top of the page:
- **Car details:** a side panel on desktop and a full-screen panel on mobile, with a gallery, spec table, highlights, history and a "Make an enquiry" button. It gets its own link so it can be shared and opened directly.
- **Saved cars:** a panel that opens from the header heart. Saves are kept in the browser, so they survive a page reload.

No files have been created. Separately, the Mobbin and Refero design-reference tools need to be authorised via `/mcp` in an interactive session before I can use them for visual references.

---

## before-5

Skills invoked: none. 21st: connected, 0 calls.

### Homepage plan: enthusiast and premium used-car marketplace

1. **Sticky header**
   - *Job:* Keeps navigation, search and saved cars one tap away.
   - *Layout:* A slim bar with the logo on the left, links (Buy, Collections, How it works, Sell) in the centre, and a favorites heart with a live count on the right. It blurs and turns translucent on scroll, and becomes a hamburger drawer on mobile.

2. **Hero and search**
   - *Job:* Sets a premium, enthusiast tone and gets users into inventory within one interaction.
   - *Layout:* A full-bleed cinematic car photo with a dark gradient. The headline sits bottom-left over a floating glass search panel (make, model, max price, body style and a Search button). Quick-filter chips sit below it ("Manual only", "Under 20k mi", "Air-cooled"). On mobile the panel stacks into a full-width card.

3. **Trust strip**
   - *Job:* Answers "can I trust buying a $90k car online?" before the user scrolls further.
   - *Layout:* One thin row of four stat/claim items with hairline dividers: 150-point inspection, 7-day returns, nationwide enclosed delivery, and 1,200+ cars sold. It becomes a horizontal swipe row on mobile.

4. **Browse by collection**
   - *Job:* Lets people shop by intent, the way enthusiasts actually think about cars.
   - *Layout:* A horizontally scrolling row of tall image tiles (Track-Ready, Grand Tourers, Modern Classics, Electric Performance, Overland 4x4), each with a count. Clicking a tile applies that filter and scrolls to the inventory.

5. **Featured / Editor's picks**
   - *Job:* Showcases standout listings and editorial credibility.
   - *Layout:* An asymmetric grid with one large feature card beside two stacked smaller cards. Each card has a short editorial note ("Paint-to-sample, 1 of 12"). On mobile it becomes a single-column stack.

6. **Inventory with filters (core)**
   - *Job:* The main shopping surface: filter, compare, favorite and open vehicles.
   - *Layout:*
     - **Filter sidebar:** sticky on the left, covering make, price and year sliders, mileage, transmission, drivetrain, body and color.
     - **Toolbar:** result count, removable active-filter chips and sort.
     - **Results grid:** 3, 2 or 1 columns depending on screen width.
     - **Cards:** hover image swipe, heart toggle, price, key specs (year, miles, transmission, location) and badges (Inspected, Price drop, One owner).
     - **Mobile:** filters move into a bottom sheet opened by a floating "Filters" button.

7. **How it works**
   - *Job:* Lowers anxiety about a high-value remote purchase by making the process concrete.
   - *Layout:* A four-step horizontal timeline (Find → Review inspection report → Reserve with refundable deposit → Delivered to your door) with icons and a line that animates in on scroll. It turns into a vertical timeline on mobile.

8. **Owner stories**
   - *Job:* Social proof from real-feeling buyers.
   - *Layout:* Three quote cards, each with a car thumbnail, the owner's name and the car they bought, plus a star rating. On mobile they become a swipeable carousel with snap points.

9. **Spec alerts CTA**
   - *Job:* Captures users whose exact car isn't listed yet.
   - *Layout:* A full-width dark band. "Tell us your spec, we'll tell you when it lands" sits on the left, with an inline make/model and email form plus a submit button on the right. The form stacks on mobile.

10. **Footer**
    - *Job:* Secondary navigation, trust and legal information.
    - *Layout:*
      - **Top:** a dark area with the brand and a one-line mission, then four link columns (Buy, Sell, Company, Support).
      - **Bottom row:** socials, legal links and a "prices are illustrative" mock-data note.
      - **Mobile:** the link columns collapse into accordions.

**Overlays (outside the page flow):**
- **Vehicle details:** a right-side drawer, or a full-screen sheet on mobile, with a gallery, spec table, history and inspection highlights, an estimated monthly payment, and a "Request viewing" button.
- **Favorites:** a drawer opened from the header heart.

The Mobbin and Refero design-reference servers aren't authorized in this session. If you want them for visual references during the build, authorize them via `/mcp` or your claude.ai connector settings.

---

## after-1

Skills invoked: none. 21st: connected, 0 calls.

Here are the homepage sections, top to bottom:

1. **Header / nav**
   - **Job:** Keeps inventory, favorites and "Sell your car" one tap away on every scroll position.
   - **Layout:** A slim transparent bar over the hero that turns solid and blurred once you scroll: logo on the left, links in the middle, and a favorites heart with a count badge plus a "Sell" button on the right. On mobile the links move into a slide-in drawer.

2. **Hero + search**
   - **Job:** Sets the premium enthusiast tone and gets visitors searching within seconds.
   - **Layout:** A full-bleed photo of a car with a left-aligned headline. Below it sits a segmented search bar (make, model, max price, body style) with quick-pick chips such as "Manual", "Air-cooled" and "Under $80k". On mobile the search bar stacks into a card.

3. **Trust strip**
   - **Job:** Builds credibility before the buyer commits to browsing.
   - **Layout:** One row of four stats: cars inspected, 150-point inspection, 7-day return and buyer rating. It becomes a horizontal scroll on mobile.

4. **Shop by passion**
   - **Job:** Gives enthusiasts shortcuts into categories: Track-ready, Grand tourers, Modern classics, EV performance, Manual only and Overland.
   - **Layout:** A horizontal rail of tall photo tiles, each with a category name and listing count. It snaps to each tile when swiped on touch devices.

5. **Editor's picks**
   - **Job:** Showcases a few standout listings to draw attention and set the quality bar.
   - **Layout:** An uneven "bento" grid with one large feature card on the left and two stacked cards on the right. It becomes a single column on mobile.

6. **Inventory** (the core section)
   - **Job:** Lets buyers browse, filter, sort and favorite the full mock inventory, and open the details for any car.
   - **Layout:** A sticky filter sidebar on the left covers price, year, mileage, make, body style, transmission, drivetrain and fuel. On the right, a toolbar (result count, removable filter chips, sort) sits above a card grid of 3, 2 or 1 columns depending on screen width. On mobile, the filters open from a sticky "Filters (n)" button as a bottom sheet.
   - **Vehicle cards:** Each card has a photo carousel that previews on hover, a heart toggle, price, a row of key specs, and badges such as "One owner", "No accidents" and "Price drop".

7. **How buying works**
   - **Job:** Explains the purchase process so a remote purchase feels low-risk: Find, Review the inspection report, Reserve, Delivered.
   - **Layout:** A four-step timeline with icons that runs across the page on desktop and down it on mobile.

8. **Sell your car**
   - **Job:** Brings in sellers with an instant-estimate hook.
   - **Layout:** A split band with a headline and a small VIN/plate plus mileage form on the left and a car image on the right. It stacks on mobile.

9. **Owner stories**
   - **Job:** Provides social proof from real-feeling buyers.
   - **Layout:** Three quote cards, each with a thumbnail of the car bought and a star rating. They become a swipeable carousel on mobile.

10. **Footer**
    - **Job:** Handles closing navigation, "new arrival" email alerts, and legal and trust information.
    - **Layout:** A dark footer with the brand name and alerts sign-up on the left and four link columns. A bottom bar holds legal links, social icons and a region/currency picker. The link columns collapse into accordions on mobile.

Two panels open over the page instead of taking a place in the scroll order:
- **Vehicle details:** A right-side drawer on desktop and a full-screen sheet on mobile. It holds the photo gallery, specs, history report, a price-vs-market indicator and contact/reserve buttons.
- **Favorites:** A slide-out list of saved cars, opened from the heart in the header.

Two design-reference connectors, mobbin and refero, need authorization before I can use them. You can authorize them in your claude.ai connector settings, or with `/mcp` in an interactive session.

---

## after-2

Skills invoked: none. 21st: connected, 0 calls.

Here's the homepage plan, top to bottom:

1. **Header (sticky)**
   - *Job:* Keeps navigation, saved cars and the "Sell your car" link in reach while scrolling.
   - *Layout:* Slim translucent bar with the wordmark on the left, Buy/Sell/Journal links in the center, and a heart icon with a saved-car count plus a "Sell your car" button on the right. On mobile the links move into a slide-in menu.

2. **Hero + search**
   - *Job:* Sets the premium tone and gets the visitor searching right away.
   - *Layout:* Full-bleed photo of a car with a dark gradient and a headline at the bottom left, over a floating search panel (make/model, price range, body style, location, Search). The panel stacks into one column on mobile.

3. **Shop by style**
   - *Job:* A quick way in for people who know the kind of car they want but not the model.
   - *Layout:* A horizontally scrolling row of image tiles (Sports, GT, Track, Classic, Performance EV, Overland). Tapping one filters the inventory below and scrolls to it.

4. **Featured this week**
   - *Job:* An editorial showcase of the standout cars, which gives the page character.
   - *Layout:* One large tile beside two stacked smaller ones, each showing an image, price, mileage and a short note. On mobile they become a single column of cards.

5. **Inventory**
   - *Job:* The main place to browse, filter, save and open cars.
   - *Layout:* A filter sidebar on desktop (price, year, mileage, make, body, transmission, drivetrain); a toolbar with result count, active-filter chips and sort; and a 3-column card grid with a "Load more" button. On mobile the filters move to a bottom sheet and the grid becomes one column.

6. **How it works / why buy here**
   - *Job:* Reduces the perceived risk of buying a premium used car: 150-point inspection, history report, secure payment, delivery and a 7-day return.
   - *Layout:* Four numbered steps in a horizontal row with icons and one-line explanations. They stack vertically on mobile.

7. **Recently sold**
   - *Job:* Shows the marketplace is active and gives buyers real sale prices to compare against.
   - *Layout:* A slow, auto-scrolling strip of compact sold cards (photo, model, final price, days to sell) that pauses on hover.

8. **Sell your car**
   - *Job:* Brings in sellers, so there are more cars to list.
   - *Layout:* A split band with copy, three quick benefits and a "Get a valuation" button on the left and a detail photo of a car on the right. It stacks on mobile.

9. **Footer**
   - *Job:* Site links, trust signals, a newsletter signup and legal text.
   - *Layout:* A dark band with a newsletter signup ("The weekly drop") across the top, four link columns, and a bottom bar with legal links, social icons and a region/currency picker. The columns become collapsible sections on mobile.

A few pieces open on top of the page rather than sitting in it:
- A **vehicle details drawer** (gallery, specs, history, seller, enquire) that opens from any card.
- A **saved cars drawer** that opens from the heart in the header.
- The **mobile filter sheet**.

Separately, the Mobbin and Refero design-reference connectors need authorizing (in claude.ai connector settings or `/mcp`) before I can use them for visual research when we build this.

---

## after-3

Skills invoked: none. 21st: connected, 0 calls.

Here's the plan. No files have been created.

### Homepage sections, in order

1. **Header / nav**
   - *Job:* Keep the brand, main links, a favorites count and "Sell your car" within reach on every screen.
   - *Layout:* A sticky bar that sits transparent over the hero and turns solid with a blurred background once you scroll. Logo on the left, links in the center, favorites heart with a count and a call-to-action on the right. On mobile the links collapse into a slide-in drawer.

2. **Hero + search**
   - *Job:* Set the premium, enthusiast tone right away and get visitors searching within seconds.
   - *Layout:* A full-width car photo with a dark gradient, a large headline and short subline on the left, and a floating search panel (make, model, max price, body style, search button) at the bottom edge. Under it sits a thin row of trust stats, such as listings live, inspected cars and average rating.

3. **Browse by category**
   - *Job:* Give one-tap entry into the segments enthusiasts care about: Sports, GT, Track-ready, Modern classics, Performance EV and Luxury SUV.
   - *Layout:* A row of image tiles with labels and listing counts. It scrolls sideways with snap on mobile and becomes a 6-column grid on desktop.

4. **Featured this week**
   - *Job:* Show hand-picked standout cars with a magazine-style feel so the site reads as curated, not a classifieds dump.
   - *Layout:* An uneven grid with one large feature card on the left and two stacked cards on the right. Each card has an overlaid price, key specs and a favorite button. On mobile it becomes a single column.

5. **Inventory with filters** (the core of the page)
   - *Job:* Let buyers narrow the listings by price, year, mileage, make, transmission, drivetrain, fuel and color, sort the results, and save favorites.
   - *Layout:*
     - **Desktop:** a sticky filter sidebar on the left and a 3-column grid of vehicle cards on the right. Above the grid are the result count, removable chips for active filters and a sort dropdown.
     - **Mobile:** a "Filters" button opens a bottom sheet, and the grid drops to 1–2 columns.
     - **Vehicle cards:** image, badges such as "Manual", "1 owner" or "Price drop", title, price, specs, location and a heart button.
     - **Empty state:** a clear message plus a reset button.

6. **Why buy here**
   - *Job:* Remove the fear of buying a used car: 150-point inspection, full history report, secure escrow payment and nationwide delivery.
   - *Layout:* Four icon-and-text columns on a subtle contrasting band, stacking to 2×2 on tablet and one column on mobile.

7. **Buyer stories**
   - *Job:* Social proof from enthusiasts who bought here.
   - *Layout:* A sideways carousel of quote cards, each with the buyer's car photo, name, the car they bought and a rating. It has arrow controls on desktop and swipe on mobile.

8. **Sell your car CTA**
   - *Job:* Bring in the supply side and end the page's story on an action.
   - *Layout:* A split banner with a large car image on one side and a headline, three value points and a button on the other. It stacks with the image on top on mobile.

9. **Footer**
   - *Job:* Navigation, newsletter signup, trust links and legal.
   - *Layout:* A newsletter band on top, then four link columns (Buy, Sell, Company, Support) next to the brand block and social icons, with a legal line at the bottom. On mobile the link columns collapse into accordions.

### Overlays (not part of the scrolling page)

- **Vehicle details:** opens from any card as a large modal on desktop and a full-screen sheet on mobile. It contains a swipeable gallery, a spec table, highlights, a price-vs-market indicator and a contact-seller form.
- **Favorites drawer:** slides in from the header heart, lists saved cars with a remove button, and keeps them after a page reload.

The Mobbin and Refero design-reference servers aren't authorized in this session, so I didn't use them. If you want them for the build, authorize them with `/mcp` in an interactive session.

---

## after-4

Skills invoked: none. 21st: connected, 0 calls.

### Homepage sections, in order

1. **Header (sticky)**
   - **Job:** Keeps navigation, the saved-cars count and "Sell your car" in reach while scrolling.
   - **Layout:** A slim translucent bar with the logo on the left, links in the center, and a heart with a live count plus the CTA on the right. On mobile it collapses to a menu sheet.

2. **Hero and search**
   - **Job:** Sets the premium, enthusiast tone and gets people searching straight away.
   - **Layout:** A full-width car photo with a dark gradient and the headline on the left. A search bar with four fields (make, model, max price, body style) sits at the bottom edge of the photo. On mobile the fields stack into one input plus a "Filters" button.

3. **Trust strip**
   - **Job:** Answers "can I trust a used car bought online?" before anyone scrolls further.
   - **Layout:** A thin band of four short claims with icons, such as "150-point inspection", "Verified history" and "7-day returns". On mobile it scrolls sideways.

4. **Editor's picks**
   - **Job:** Shows a few hand-picked cars to make people want to browse.
   - **Layout:** One large card on the left and two smaller cards stacked on the right. On mobile it becomes a swipeable carousel.

5. **Inventory**
   - **Job:** The main browsing area, and where the hero search sends its results.
   - **Layout:**
     - A row of quick-filter chips on top, such as "Manual", "Track-ready" and "Under 30k mi".
     - A filter sidebar on the left with price and year ranges, make, transmission and drivetrain.
     - A results bar with the count and a sort menu.
     - A responsive grid of car cards. Each card has a photo carousel, a heart to save it, a price rating badge and key specs.
     - On mobile the sidebar becomes a bottom sheet with a sticky "Show N cars" button.

6. **How it works**
   - **Job:** Explains the buying process from browsing to delivery and lowers the risk of a big purchase.
   - **Layout:** Four numbered steps connected by a line. They sit in one row on desktop and stack vertically on mobile.

7. **Buyer stories**
   - **Job:** Social proof from enthusiasts, tied to the actual cars they bought.
   - **Layout:** A carousel of quote cards. Each card shows the buyer's name, the car they bought and a photo of it.

8. **Sell your car**
   - **Job:** Brings in sellers.
   - **Layout:** A split banner with the pitch and a small "get an estimate" form (make, model, year, mileage) on the left and an image on the right. On mobile they stack.

9. **Footer**
   - **Job:** Links, newsletter sign-up and trust details to close the page.
   - **Layout:** A dark block with the brand and newsletter field on the left, four link columns, and a bottom bar with legal and social links. On mobile the columns become accordions.

Two panels open over the page rather than being sections:
- **Vehicle details:** Opens from any card. It's a side drawer on desktop and a full-screen sheet on mobile, with the photo gallery, full specs, history and a request-viewing button.
- **Saved cars:** Opens from the header heart. Saved cars are kept in the browser's local storage.

The Mobbin and Refero design-inspiration servers need authorizing before I can use them for reference. You can do that in your claude.ai connector settings or with `/mcp` in an interactive session.

---

## after-5

Skills invoked: none. 21st: connected, 0 calls.

### Homepage plan: premium used-car marketplace

1. **Sticky header**
   - **Job:** Keeps navigation, the favorites count and a quick way back to search in view on every scroll position.
   - **Layout:** Logo on the left, links in the center (Buy, Collections, Sell, How it works) and a heart button with a count on the right. It's transparent over the hero, turns solid and blurred once you scroll, and becomes a slide-in menu on mobile.

2. **Hero and search**
   - **Job:** Sets the premium tone right away and gets people searching in one step.
   - **Layout:** A full-width car photo under a dark gradient, with a large headline on the left. Below it sits a floating search bar (make, model, max price, body style, Search button) and a row of quick-pick chips like "Air-cooled 911", "Manual only" and "Under $75k".

3. **Trust stats strip**
   - **Job:** Answers "can I trust buying a car online?" before the visitor has to ask.
   - **Layout:** Four stats in a row, each with a small icon and a number that counts up: cars inspected, 150-point inspection, 7-day returns, nationwide delivery. It becomes a 2×2 grid on mobile.

4. **Curated collections**
   - **Job:** Lets enthusiasts browse by taste rather than specs. Each tile applies a filter to the inventory and scrolls down to it.
   - **Layout:** A row of tall photo tiles that scrolls sideways and snaps into place: JDM Legends, Air-Cooled, Modern GT, Track-Ready, Analog Manuals. Each tile shows its car count and zooms slightly on hover.

5. **Inventory with filters** (the core of the page)
   - **Job:** Browse, filter, sort and save cars.
   - **Layout:** A filter sidebar on the left that stays in view as you scroll, with price and mileage sliders, year, make, body style, transmission and drivetrain.
     - On the right is a results bar (count, active-filter chips you can remove, sort menu) above a 3-column card grid.
     - Cards animate when filters change.
     - On mobile the grid drops to one column and the filters move into a sheet that slides up from the bottom.
   - **Vehicle card:** A photo you can swipe or hover through, a heart button that pops when tapped, and a badge such as "Just listed" or "Price drop". Below the photo: year, make and model, the trim, price, mileage and location, and tags like "1-owner" or "Manual".

6. **Car of the week**
   - **Job:** Editorial storytelling that sets the site apart from a plain listings page.
   - **Layout:** Split in two, with a large photo gallery on the left and on the right a short story, a key-specs table, price and an "View details" button. It stacks on mobile.

7. **How it works**
   - **Job:** Takes the fear out of buying a car remotely.
   - **Layout:** Three numbered steps (Reserve online → Review the inspection report → Delivered to your door), joined by a line that draws itself as you scroll.

8. **Buyer stories**
   - **Job:** Social proof from real-feeling owners.
   - **Layout:** A carousel of quote cards, each with the owner's name, a photo of their car and a star rating. It pauses on hover and can be swiped on mobile.

9. **Sell your car CTA**
   - **Job:** Brings in the other side of the marketplace: sellers.
   - **Layout:** A dark full-width band, with copy on the left and on the right a "Get an offer in 2 minutes" box where you enter a VIN or plate.

10. **Footer**
    - **Job:** Newsletter signup, navigation and legal.
    - **Layout:** A newsletter row at the top ("New arrivals, every Friday"), then four link columns (Buy, Sell, Company, Support), then social icons, the legal text and a region selector. The link columns fold into collapsible sections on mobile.

### Pop-ups that open over the page (not page sections)

- **Vehicle detail:**
  - On desktop, a large centered window with a photo gallery, specs, highlights, the inspection summary, a monthly payment estimate and "Reserve" and "Favorite" buttons.
  - On mobile, a full-screen sheet you can swipe down to close.
  - It can be closed with Esc and handles keyboard focus properly.
- **Favorites panel:**
  - Slides in from the right when you click the header heart.
  - Lists the saved cars with a remove button and remembers them between visits.

### Note on design references

The Mobbin and Refero design-reference tools can't be used until you authorize them. Do that through their claude.ai connector settings or with `/mcp` in an interactive session. This plan doesn't depend on them.
