# Benchmarks and evidence

Everything in this setup is a claim about behavior. This page says which claims
are backed by measurement, which are backed by observation, which are design
rationale, and which are untested.

**Evidence classes used below**

| Class | Meaning |
|---|---|
| **Measured** | A number produced by an instrument or a recorded run, reproducible from data still on disk. |
| **Observed** | Behavior seen in real sessions, recorded, but not controlled or repeated. |
| **Rationale** | A design argument. No measurement. It may still be right; it is not evidence. |
| **Hypothesis** | A belief about behavior that has not been tested. |
| **Not proven** | Something that was tested and did *not* come out demonstrated. |

No number on this page was estimated, extrapolated, or invented. Where a number
is missing, it says so.

---

## 1. Context-efficiency layer — `run-captured`

**Class: Measured.** Source: `ledger.tsv` in the capture directory, written by
the helper itself, one row per invocation with bytes captured and bytes
surfaced.

Window: **2026-09-06 → 2026-09-13** (7 days of ordinary work across several
repositories), **659 invocations**.

| | Rows | Bytes captured | Bytes surfaced | Surfaced share |
|---|--:|--:|--:|--:|
| All invocations | 659 | 4,642,746 | 802,539 | 17.3% |
| Invocations that were actually reduced | 124 | 4,171,166 | 330,959 | 7.9% |
| Invocations passed through verbatim | 535 | 471,580 | 471,580 | 100% |

By command label, for the reduced invocations only:

| Label | Runs | Captured | Surfaced | Reduction |
|---|--:|--:|--:|--:|
| `test` | 16 | 1,973,895 | 62,582 | 97% |
| `python` | 19 | 917,508 | 60,398 | 93% |
| `pytest` | 15 | 432,703 | 88,714 | 79% |
| `docker` | 37 | 227,192 | 29,313 | 87% |
| `vitest` | 8 | 135,293 | 20,372 | 85% |
| `ruff` | 3 | 30,636 | 5,284 | 83% |
| `build` | 2 | 29,103 | 2,063 | 93% |

### What this does and does not establish

It establishes that **when output is large, the helper surfaces a small
fraction of it** — 92% less on the 124 invocations where the size threshold was
crossed — while keeping the whole thing retrievable on disk.

It does **not** establish:

- **Tokens saved.** Bytes are not tokens, and the harness independently spills
  any single Bash result above ~30k characters to a file anyway. The real
  counterfactual for a 446 KB test log is "the harness truncates it and I read
  the file", not "446 KB enters context".
- **A controlled comparison.** There is no A/B arm. Without the helper the model
  might have run a narrower command instead, or read the spill file, or both.
- **That 81% of invocations were useful.** 535 of 659 runs (81%) were small
  enough to pass through verbatim — for those the helper is a no-op with a small
  process-spawn cost. That is by design (an unexpectedly small result must cost
  nothing extra), but it means the average invocation saves nothing.
- **Anything about quality.** Compactness is not correctness. The helper's real
  guarantees — exit status propagated, failures never over-compressed, every
  failing test name preserved — are design invariants, not measurements.

**Not measured:** a `/context` breakdown (Bash-result tokens vs Read-result
tokens vs MCP share) before and after the layer was added. That is the
measurement that would actually settle the question, and it has not been taken.

---

## 2. Dead-code audit skill

**Class: Mixed — see each line.** A small controlled experiment was run on a
purpose-built fixture.

### Setup

- **Fixture:** a 12-file Python package with a two-commit history, where the
  second commit removed a module so downstream code *looked* orphaned.
- **Ground truth:** 1 genuinely dead function, plus **4 traps** that look
  equally dead to a text search but are live — an adapter reachable only through
  a string-keyed registry, a CLI entry point reachable only via
  `[project.scripts]`, a database migration, and an aggregation `__init__`
  import.
- **Arms:** 4 copies of the fixture, one subagent per copy, identical
  time-pressured prompt ("delete the dead code, we ship in 20 minutes… be
  decisive"). Subagents ran on a mid-tier model; the orchestrator on the top
  model.
- **Measurement:** the resulting `git diff`, inspected independently of what
  each agent claimed it had done.
- **n = 1 per arm.**

### Results

| Claim | Class | Detail |
|---|---|---|
| An uninformed agent discovers and invokes the skill from its description alone | **Measured** | One arm intended as a no-skill baseline self-invoked the skill twice, from its description. That voided it as a control — but it is direct evidence that discovery works. |
| Structured reporting improved | **Measured** | The skill arm emitted scope, the tools that actually ran, three confidence classes, and an explicit validation line. The clean control produced ad-hoc prose with no confidence classification. |
| Confidence classification improved | **Measured** | Same source: proven-dead / likely-dead / retained-by-class appeared only in the skill arm. |
| **Safer deletion decisions** | **NOT PROVEN** | The skill arm's diff was −5 lines: the one genuinely dead function, all four traps intact. The clean control produced **the same diff**, and even executed the dynamically-dispatched path to prove it was live. The skill did not change the deletion decision on this scenario. |

### Why "not proven" and not "disproven"

The fixture was too easy. With the registry sitting ten lines from the call site
in a twelve-file package, a careful agent finds the trap without help. A
mechanism cannot be shown to fix a failure that the control does not exhibit.

**What a real test would need:** a repository large enough that the reference is
not visible from the call site — dynamic dispatch across module boundaries, a
framework-discovered entry point in a different directory, a string key built at
runtime — several independent scenarios, and more than one run per arm. That
benchmark has not been built.

**So the demonstrated value of this skill is auditability and the required
disclosure, not proven deletion-safety.** It is kept because the report it
forces is cheap and the failure it guards against (deleting live code on the
strength of an empty grep) is expensive — that part is *rationale*, not measured.

---

## 3. Ponytail review

**Class: Observed** (real findings across six sessions that invoked the review),
plus **third-party Measured** numbers for the persona, cited not reproduced.

### Third-party benchmark (not ours)

The Ponytail project publishes its own benchmark: 3 arms × 3 models × 5
everyday tasks, 10 runs per cell, median reported, with a reproduction recipe.
Its headline result is a large reduction in generated lines of code (e.g. a
median of 693 → 44 lines on one model/arm pair) with lower cost and latency.

Those numbers are **theirs, measured on greenfield single-task prompts, for the
persona mode.** They say nothing about the review mode used here, and nothing
about review quality on an existing codebase. They are cited because they are
the reason the tool was worth trying — not as evidence for this setup. See the
project's `benchmarks/` directory for the methodology.

### What was actually observed here

Anonymized, with project-specific detail removed.

**Findings applied** (the cut was clearly beneficial):

- a hook method that existed only to clear a transient UI error — the behavior
  was already reproduced by an existing conditional (−9 lines);
- a 9-line derivation collapsed to 6 by introducing a named comparator;
- a string derivation cut from 8 lines to 4;
- duplicated state flags and fields nothing read, deleted;
- a duplicated formatting helper folded into an existing guarded one;
- a struct field no producer ever populated, dropped;
- a normalization helper duplicated across three adapters, consolidated into one.

**Findings rejected, and why** (this is the more informative half):

| Proposed cut | Rejected because |
|---|---|
| Remove a "premature optimization" pre-filter | Measurement: 6.0 ms → 1.8 ms per call, ~3× on the hottest path. Evidence beats the heuristic. |
| Inline a small named helper | A doc-commented name beats an inlined non-obvious regex. Maintainability (6) outranks Ponytail (7). |
| Drop a response field | Public API surface, pinned by a test. |
| Drop a validity guard | Removing it would silently degrade results one layer down; a test pins the contract. |
| Inline a one-caller wrapper | Its body documents a deliberate architectural constraint. |
| Remove an explicit null check | It is the narrowing the type checker needs. |
| Use a shorter encoding | The value is human-read. |
| Extract shared CSS across components | Out of scope for the change under review. |
| Remove a response cap and truncation flag | They bound an unauthenticated response. Security (3) outranks Ponytail (7). |

One review concluded **"Applied: none"** — every proposed cut traded a stated
correctness property for lines. Validation was re-run and reported green after
each session that applied anything.

**What this shows:** the priority ladder is doing real work. A complexity
reviewer with authority to act would have removed a measured 3× optimization, a
security bound, and a public API field. It is advisory for a reason.

**What this does not show:** that the review improves the codebase on net. There
is no controlled comparison, no measure of what the applied cuts saved, and the
sample is small and self-selected.

---

## 4. Graphify lazy-init hook

**Class: Observed**, single run, recorded at the time the hook was built.

- A 45-file Python repository built its graph in ~3 seconds, with zero LLM
  invocations (verified with a shim that would have caught one).
- The common path — hook fires, decision already cached, nothing to do — cost
  roughly 35 ms.

Single measurements on one machine, one repository. Enough to establish the hook
is not expensive on the common path; not enough to characterise build time in
general. The thresholds (50 tracked source files / 10k LOC / skip above 6000
files) are **rationale**, not tuned against data.

---

## 5. Ponytail flag leak

**Class: Measured** (direct reproduction), and it is the most important finding
here because it is a *defect*, not a benefit.

Ponytail's active mode lives in a single file under the Claude config directory.
It is **machine-global**, shared by every concurrent session — not session state.
Typing `/ponytail-review` writes `review` into it, and while it is set the
plugin's subagent hook injects the "delete code" persona into unrelated
subagents.

**Reproduced by running the plugin's hooks directly: a `security-judge`
subagent received the ponytail context.**

A simplification persona reaching a security or correctness reviewer inverts
what that reviewer is for, and because the file is shared, it crosses session
boundaries invisibly — a review in one terminal can alter a judge in another.

Three independent containment layers are in place. See
[security.md](security.md#the-ponytail-flag-leak).

**Not measured:** whether the containment is complete. The sentinel matcher, the
guard hook and the plugin's own session-start clear are each individually
verified to do what they claim; there is no test proving no fourth path exists.

---

## 6. UI/UX Pro Max design-system generator

**Class: Measured** (direct reproduction) for what the tool returns. That the
output is off-target is a judgement, but the evidence for it is quoted below, so
you can check it yourself.

Run on 2026-09-27 against `nextlevelbuilder/ui-ux-pro-max-skill` at `09170ee`, the
head of the default branch, which is what a plugin install fetches. Its manifests
still say 2.13.0, and the newest tag, `v2.15.0`, points at an earlier commit
(`a38d04c`; check with `git ls-remote --tags`). The search script is
standard-library Python over bundled CSV files. It makes no network calls, so the
output is deterministic:

```bash
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill && cd ui-ux-pro-max-skill
git checkout 09170ee
S=.claude/skills/ui-ux-pro-max/scripts/search.py
python3 "$S" "grocery price comparison unit price nearby stores" --design-system --density 8 -f markdown
python3 "$S" "AI agent wallet security firewall onchain policy audit console" --design-system --density 7 -f markdown
python3 "$S" "used car marketplace inspection reports trust" --design-system -f markdown
python3 "$S" "price comparison search results list" --domain product -n 3
```

| Product described | What came back |
|---|---|
| Consumer grocery price comparison | Pattern "Real-Time / Operations Landing" with a "Start trial / Contact" CTA; style "Dark Mode (OLED)" with light mode marked not recommended; Inter headings over a Playfair Display body; palette note "Dark luxury + bid green + outbid red + urgency"; anti-pattern "No bid state". This is an auction profile. |
| Security console for AI-agent wallets | Pattern "Hero + Testimonials + CTA" with a testimonials carousel; style "AI-Native UI" with typing indicators; palette note "AI purple + generation pink" (`#7C3AED`, `#EC4899`). |
| Used-car marketplace with inspection reports | "Hero + Testimonials + CTA" again; Inter over Playfair Display again; palette note "Trust purple + transaction green". |
| `--domain product` lookup, price-comparison results list | Patient Portal / Health Records; Patent / IP Database; Gift & Wishlist. |

Installing it as a plugin adds seven skills, because its manifest points at the
whole `.claude/skills/` directory: `ui-ux-pro-max`, `design`, `design-system`,
`brand`, `ui-styling`, `banner-design`, and `slides`. Together their descriptions
are 2,663 characters. The two design skills here have 385.

**What this establishes:** what the generator returns for these descriptions at
this commit, and that two of the three results are templates this layer is built
to avoid.

**What it does not establish:** that the tool never helps. That would take more
products and more queries. Its UX-guideline rows are generic checklists rather
than wrong ones.

---

## 7. Design-layer micro-tests

**Class: Observed**, placed one step down on purpose. The runs were more
rigorous than the class needs: five fresh-context runs per arm, with inputs
identical except for the text under test. But as with §3, a reader cannot rerun
them from this repository. The fixtures and transcripts are not published, the
review arm's inputs are a private project's, and every report was scored by hand
by a single scorer who also made the change.

Run on 2026-09-27 with the `opus` alias the judge definitions use. Each control
arm ran before the text under test changed.

**Build path: the failure did not reproduce, so nothing was added.** The task was
a brief for a fictional grocery price-comparison app. Context was the current
rule plus `frontend-quality` and `frontend-design`. Each run was asked for layout
wireframes of the home and results screens at 375 and 1280px. For five runs the
product's data was stated in the brief. For the other five it appeared only in
API types and a test-fixture summary.

| Scored | Data in brief | Data only in codebase |
|---|---|---|
| First viewport shows real product data | 5/5 | 5/5 |
| The store holding 7 of the 10 cheapest offers is stated once | 5/5 | 5/5 |
| Desktop adds information (matrix, columns, side panel) | 5/5 | 5/5 |

This is weaker than it looks. Both fixtures stated the data's shape outright
("7 of the 10 cheapest" are at one branch), which invites grouping. The shipped
screens in the review arm did fail, but they were following a brief that mandates
the repeated strip, on an API whose only price query is a per-staple search. So
the runs show that the defaults compose from the data when the data and its shape
are in view. They do not show that the build path cannot fail. No builder run used
that real brief. A builder that follows it would reproduce the strip by design,
and a builder rule cannot outrank the brief.

Motion used the same method: five runs, on three interactions CSS can do (an
expand/collapse, a dialog, and a re-sort in a React 19.3 app with no animation
library). All five chose CSS (`@starting-style`, `transition-behavior:
allow-discrete`, `grid-template-rows`) and added no dependency. All five also
left the re-sort unanimated, but the fixture brief limited motion to open, expand
and confirm, so that part followed the brief. The other half of the policy was
not tested: reaching for Motion when the platform cannot do the job.

**Review: a failure found, fixed, and checked against a negative control.**
`visual-design-judge` reviewed two real 1280px renders of a price-comparison app
against that product's brief. One was a home screen with an instruction above
half a screen of empty space. The other was a results list in which four of five
cards carry an identical store strip and a wide empty gap, which the judges put
at 650 to 800px.

| Raised as a finding | Before | Three questions + fix recipe | + owner-cost sentence | Final wording |
|---|---|---|---|---|
| First viewport lacks data the product already has | 0/5 | 5/5 | 5/5 | 5/5 |
| Identical content repeated across sibling cards | 0/5 | 2/5 | 5/5 | 5/5 |
| Desktop width answered with information, not by narrowing | 0/5 | 5/5 | 5/5 | 5/5 |

Before the change, no run raised the empty home screen as a finding, and two
explicitly accepted it ("fine for an empty state", "which the brief's restraint
allows"). Four of five proposed capping or narrowing the width, and the fifth
left the gap to the brief's owner with no direction. With the three questions
alone, two of five raised the repeated strip. One run that missed it explained
why: "the brief requires a strip on every card, so I note this but don't score
it." With the owner-cost sentence, all five raised it, as a question for the
brief's owner. The final wording swaps an example that named the fixture ("the
same store") for a neutral one, and adds the packet's data line. All 20 review
runs, in every arm, also reported the findings the judge already made: accent
overuse and the missing price-history action.

The negative control used the final wording and the fictional brief on three
deliberately good renders:
- a home screen full of data;
- results grouped by store, with columns at desktop;
- a first-visit ZIP screen, where showing no data is correct.

The criteria were fixed before the runs. By those criteria, no run raised any of
the three checks falsely. Some said so explicitly: "the main question is answered
with data, not a prompt"; "asking for a ZIP first is justified, since none is
stored". The repetition that runs did raise was content that really was
identical, such as "sold by weight" in every banana cell. The first-viewport
question still leans one way. Four of five runs suggested, at low severity, that
the first-visit screen name what gets compared, and two noted its empty space.
That is reasonable copy advice, but it shows the lens tilts toward adding content
even where no data is owed. All five also found two flaws built into the renders
by accident: columns that don't line up across store groups, and counts that
don't match the rows. Four of five caught that the two screens disagree on the
cheapest eggs.

**What this establishes:** on these fixtures, the review lens now raises what it
used to miss, and it does not raise the three defects against screens that lack
them. It does lean toward suggesting more content.

**What it does not establish:** that the result generalizes beyond one product
domain. It also does not establish that a fixed review leads to a better shipped
page, since the loop was not run end to end, or anything about models other than
the one tested. Every run shared the same ambient context the harness loads
automatically, identical across arms.

---

## 8. Frontend research trigger and three-way build

**Class: Observed** for why 21st.dev's MCP went unused and for what the fix
changed in tool selection. **Not proven** for the claim that component research
improves the rendered page: it was tested once, and did not come out ahead.
The step down from Measured is deliberate. Every count comes from a recorded
run, but a reader cannot rerun them from this repository. Each condition is one
build, the builds were judged by one model run, and the original tool-selection
probes' transcripts were not kept (the follow-up's are kept, unpublished). The prompts,
counts, render checks, judge report, composition plans, follow-up probe results
and side-by-side boards are in
[benchmarks/frontend-abc](benchmarks/frontend-abc/README.md).

Run on 2026-09-29 and 2026-09-30 with Claude Code 2.1.285 on `claude-opus-5-5`,
headless, with the full global configuration loaded.

**The question.** 21st.dev's MCP had a valid key and answered every call, yet no
frontend session called it, and built pages looked generated. Why, and does
calling it help?

**Why it went unused.** Scope and routing were checked directly. Discovery is a
contributing condition that no arm isolated.

- **Scope.** It had been added from the home directory, so its local scope was
  the home directory's. No session opened in a repository loaded it.
- **Routing.** `design-brief`'s research step named only Refero and Mobbin.
  Neither was signed in, so the step was skipped. The legacy build said so:
  "the Mobbin and Refero design-reference tools need authorizing … I set the
  visual direction without them." `frontend-quality` mentioned 21st.dev only as
  a place to look when one element is the hard part.
- **Discovery.** MCP tools are deferred, so a session sees their names only, and
  this server sends no instructions.

Tool-selection probes, with 21st connected in every arm. The substantial prompt
asked for a used-car marketplace frontend (hero, search, filtered listings,
detail view). The trivial prompts were a footer font-size bump and a one-line
copy change. The two middle arms appended earlier drafts to the system prompt
and disallowed `get_component`. The second draft still limited research to React
and Tailwind projects, and its lists of substantial and trivial work were
shorter. Only the installed arm ran the text this repository ships.

| Arm | Substantial prompt called 21st | Trivial fix called 21st |
|---|---|---|
| As configured (all three loaded `design-brief` and `frontend-quality`) | 0/3 | not run |
| + a first draft of the trigger rule in the system prompt | 2/2 | 0/1 |
| + a later draft of the skill text in the system prompt | 2/2 | 0/1 |
| Installed: the shipped skills, 21st at user scope, no flags | 2/2 | 0/2 |

Every probe that called 21st made one `get_inspiration` and three `search`
calls. The two installed substantial runs were stopped after those calls, so
that the composition test below could run alone. The two installed trivial runs
loaded no skill at all. They show that 21st at user scope is not called for a
small fix, not that the skill's small-fix exclusion causes it. That exclusion was
never in context in any trivial run.

**Three builds from one product.** Same scaffold, data, photos and model, each
built in its own directory without sight of the others. What differed was the
prompt:

| | legacy-auto | control | 21st |
|---|---|---|---|
| Prompt | An ordinary request, configuration as it was, 21st connected but not mentioned | A detailed brief with an avoid-list, 21st forbidden | The same brief, plus heavy 21st use |
| 21st calls | 0 | 0 | 40 (22 `search`, 7 feedback, 4 `get_inspiration`, 2 `get_component`, 2 `get_theme`, 2 `search_logo`, 1 `get_usage`) |
| Tool calls, including subagents | 359 | 476 | 447 |
| Cost | $14.80 | $19.19 | $26.52 |
| Page height at 1440px | 3,362px | 7,838px | 9,213px |
| Mobile menu | none | full-screen | full-screen, with car thumbnails |
| Blind judge, mean of 13 criteria | 5.8 | 7.8 | 7.1 |

All three pass `npm run build` and lint (rerun on 2026-09-30), and render with
no horizontal overflow or broken images. Every scripted interaction step
completed, except legacy-auto's mobile menu, which does not exist. "Completed"
means the control was found and the action performed within 8 seconds; the check
does not confirm what the action did. The judge saw anonymized screenshots and
ranked control first, 21st a moderate gap behind, and legacy-auto a large gap
behind that. By its account legacy-auto has the best-built filters and detail
modal, but only three sections (hero, inventory, footer) and no mobile
navigation.

What 21st contributed is recorded call by call in the build's log. Its two code
retrievals became the hero filmstrip and the list-with-image-preview used for
collections, and searches set the filter rail, the price histogram, the drawer
motion and the mobile menu. Its catalog was thin for this product. Template and
theme searches for automotive or editorial returned nothing, and searches for a
car hero, an editorial bento and a spec sheet returned only SaaS components. The
one automotive result, a video-scrub hero from `get_inspiration`, needed video
frames the build did not have. The judge's weakest decision in that build, the
colour-tinted hero, is the retrieved hero's background re-grade, applied with
each car's paint colour. Its strongest, the mixed-size gallery, was built by hand
after 21st's bento results were rejected.

All three converged on a warm off-white page, a wide display typeface, a left
filter sidebar beside a three-column grid, a round heart top-right on every
photo, and a mobile sheet with "Clear all" and "Show N cars". Control and 21st
also both named the site "Chicane".

**The composition paragraph: a plan-level test that could not reach it.**
`design-brief` gained a paragraph against stacking (hero, one grid, footer). The
protocol was fixed before any run: five fresh sessions per arm, with the
paragraph removed or present. The prompt was the legacy request's product and
feature list, without its prepared scaffold, data and photos, plus "only plan the
homepage's sections". Writes were disallowed.

No run in either arm invoked `design-brief`, or any skill, so the paragraph never
entered context. By the protocol, all ten runs are uninformative.

The same ten runs are also a tool-selection result for the shipped
configuration. 21st was connected and the shipped `frontend-quality` was
installed, yet 0/10 called 21st, because a request to plan loaded no skill. All
ten noted that Mobbin and Refero needed signing in; none mentioned 21st.

One further observation came out. All ten plans proposed seven or eight
sections, none a stack, and all ten named a mobile menu. Legacy-auto shipped
three sections and no menu. That suggests the stacking happens during the build
rather than in the plan, but the build also had four skills loaded and a fixed
12-car dataset, so either could explain it. The paragraph needs a full-build
test.

**Follow-up: planning, fallback and established systems.** The 0/10 above, and
the owner's decisions after the first review, changed the route:
- `frontend-quality`'s description names planning, including a request for
  advice on what a page should contain, and a request for a plan takes the route
  of the work it plans;
- substantial frontend work is defined once, in `frontend-quality`. Its
  description repeats the list, because the description decides whether the
  skill loads. `design-brief` and `rules/frontend.md` refer to it;
- in a product with an established design system, research runs only when the
  structure, an interaction pattern or the visual direction is genuinely new.
  Since round 3, `frontend-quality`'s "Research" is the only statement of that
  rule. It also sets what the no-tool fallback covers, and it judges eligibility
  from the request, not from features added while planning;
- with no research tool connected, `design-brief` writes an internal art
  direction instead of skipping the step (structure only in an established
  system);
- `record_inspiration_feedback` is denied.

Two rounds of probes followed, each with pass criteria fixed before its runs
([protocol](benchmarks/frontend-abc/followup-protocol.md)).

Round 1 ran an intermediate text. A four-judge review then found problems in
both the text and the arms. The two most serious: the fallback's worked example
was the probe's own domain, and the established-system prompts told the model the
answer. The text and the arms were revised.

Round 2 ran the text as it stood before round 3's fixes, 25 runs, with 21st at
user scope (connected at start in every run that needed it) and `get_component`
disallowed:

| Arm | Passed | Result |
|---|---|---|
| Substantial planning: the marketplace (3), a veterinary-clinic app (2) | 5/5 | Both skills loaded, then one `get_inspiration` and three `search` calls. Before the change: 0/10 on the marketplace prompt |
| A substantial plan asked as a question ("What should the homepage … include?") | 2/2 | The same |
| Substantial build | 2/2 | 21st called before the first write |
| Trivial fix (2), trivial question (2), small new component (1), plan for a small fix (1) | 6/6 | No 21st call, and no skill loaded, in any of the six. For the component that is also a miss: the "New component" route should have loaded `frontend-quality`, and the run checked only the desktop layout |
| Established system, a pattern the site lacks (a comparison view) | 2/2 | Researched with 21st; styles kept from the site |
| Established system, a saved-cars page | **0/2** | Both added interactions the site lacks (a side-by-side view; one also an undo) and searched 21st, including for the page layout. One run called the page a new screen |
| No research tool, greenfield: the marketplace (2), the clinic app (2) | 4/4 | An internal art direction with all four elements, and references from each product's own world |
| No research tool, established system | 2/2 | Structure only; all styling from the site, and no new signature element |

In the greenfield fallback runs, each product got references from its own world:
- **the cars:** a window sticker, a service book, an auction catalogue;
- **the clinic:** an appointment book, a kennel card, a treatment-room
  whiteboard.

The skill's own example is a wine shop; no reply used it. The fallback runs were
scored by the person who made the change, from the replies, which are published.

The saved-cars result is a failure against its pre-fixed criterion. Round 1's
pass on the same page came from a prompt that said the page reuses existing
patterns. So the gate has not been shown to hold when the model must judge. The
comparison-view pass does not show the gate discriminates either, because a text
that always researched would pass it too. Two things may have contributed:
- the site's saved drawer already says "Compare them in the inventory", and both
  runs searched for comparison tables;
- `rules/frontend.md`, which loads when component files are read, summarizes the
  route without the established-system exception.

Each failing run made two metadata calls.

Every probe's working directory is under a folder whose name contains "21st".
That could prime a research arm; it cannot explain a run with zero 21st calls.

**Round 3** fixed the four open issues listed at the end of this section. It
reran a focused set on the final text, and the owner stopped it once the
practical questions were answered (11 runs,
[protocol](benchmarks/frontend-abc/followup-protocol.md)):

| Case | Passed |
|---|---|
| Established system, the saved-cars page | 3/3 with no 21st call, each planned from the site's existing parts (round 2: 0/2) |
| Established system, the comparison view | 2/2 researched with 21st |
| Component-system cleanup in the established site | 1/1 with no 21st call, and no visual change planned |
| Substantial planning | 2/2 researched |
| Trivial fix | 2/2 with no 21st call |
| No tool, established system, no research due | 1/1: planned from the existing system, with no art direction |

Two things make these results weaker than they look:
- The Research rule's example of a page that introduces nothing new is "a saved
  list", the same case as the saved-cars probe. So 3/3 shows the example works
  there, not that the eligibility rule generalizes.
- The cleanup prompt itself says "without changing how the site looks".

Some cases were not rerun on the final text:
- the build and the no-tool new product, which round 2 covered on the text
  before round 3;
- the no-tool cases where the request opens new structure or a new look;
- a new component system with no existing visual language. A review found that
  route missing its direction step; it was fixed in text after the runs.

**What this establishes:** the MCP went unused because of scope and routing, not
because of the key or the server. With the scope fixed and the route in
`frontend-quality` saying when to research, substantial work calls it:
- planning: 5/5 in round 2 and 2/2 in round 3, against 0/10 before;
- a plan asked as a question: 2/2;
- builds: 2/2.

Small work does not call it: 0/6 in round 2 (trivial fixes, questions, a small
component, a plan for a small fix), 0/2 in round 3, and 0/4 in the original
probes. With no research tool, a run states an internal art direction instead
of skipping the phase (6/6 in round 2, greenfield and established). No run without the new paragraph was
made, so this does not show the paragraph causes it. In an established system,
the round-2 text did not hold research back for the saved-cars page (0/2); the
final text does (3/3), and still researches the comparison view (2/2). On this
product, a detailed design brief changed the rendered result more than adding
21st to that brief did.

**What it does not establish:** that component research improves a page. The one
build that did it scored below the one that did not, and its worst decision came
from a retrieved component. Nor does it show that the composition paragraph, the
narrow-viewport navigation check or the internal art direction changes a built
page (§9).

The judge was told all three had the detailed brief; legacy-auto did not, so its
section score measures the gap to what the owner wants, not a failure to follow
its prompt.

Several behaviors were never exercised:
- a small fix that loads `frontend-quality`. No trivial run loaded a skill, so
  the small-fix exclusion itself was never in context;
- research tools that are listed but unauthenticated, as Refero and Mobbin were
  in the original failure. The fallback ran only with every server absent;
- a major redesign, a significant UX restructuring, and a mid-size change such
  as a form or a modal (component-system work ran once, in round 3);
- 21st together with Refero or Mobbin. Both were unauthenticated in every run;
- `get_component` limited to React and Tailwind projects. It was disallowed in
  every probe;
- the `record_inspiration_feedback` deny rule, beyond the tool's absence from the
  session's tool list;
- builds for any product besides a used-car marketplace.

One model, one to five runs per probe cell (ten in the composition test), and one
build per condition.

**The four open issues from round 2, resolved in round 3:**
- **Style in an established system with no tool connected.** "Research" now sets
  what the fallback covers: structure and behavior, and style only where the
  request opens it. This is a text fix; round 3 ran only the no-research-due case
  (1/1).
- **`rules/frontend.md`** now points to `frontend-quality` for the route and the
  established-system exception instead of restating them, and it says "small
  fix". This is a text fix.
- **Component-system work** has its own route, which takes precedence (1/1).
- **Research earned by added scope.** Eligibility now comes from the request and
  the product's existing requirements. The saved-cars page went from 0/2 to 3/3.

---

## 9. Claims made with no measurement at all

Stated plainly so they are not mistaken for results:

| Claim | Class |
|---|---|
| Path-scoped rules cost less context than global ones | **Rationale** — mechanically true (they don't load), but the size of the effect on output quality is untested. |
| Blind, parallel judges reduce anchoring and sycophancy relative to a single self-review | **Hypothesis** — well-motivated, and the protocol is built for it, but not measured here. |
| Resolving by evidence rather than vote count produces better outcomes | **Rationale** — the argument (correlated blind spots) is sound; no A/B exists. |
| `test-judge` on a cheaper model loses little | **Hypothesis** — a cost judgement, never tested. |
| The read-budget advisor changes read behavior | **Hypothesis** — the hook fires; nobody measured whether the model then reads narrower. |
| The large-output advisor changes command choice | **Hypothesis** — same. |
| One-hint-per-session-per-class is the right frequency | **Rationale** — chosen to avoid nagging, never tuned. |
| Telling `visual-design-judge` what data the product already holds makes its first-viewport check fire when no other render shows that data | **Hypothesis**. In testing, the data was visible in a second render; the packet line itself was not tested. |
| The screen-reference hook, used only when Refero or Mobbin is connected, leads to principle-level references rather than copied screens | **Rationale**. No reference server was signed in during testing. |
| Component research adapts rather than pastes | **Rationale**. One self-reported instance (§8): the 21st build's log says it restyled both retrieved components and removed behaviors that did not fit. The component source is not published, the build was told to use 21st heavily, and the re-grade it kept from the retrieved hero was the judge's weakest decision. |
| Requiring component research for substantial frontend work | **Rationale**. It is the owner's stated policy. It was tested once (§8) and did not come out ahead; what the step fixes is that research never ran at all. |
| Researching two or three shipped products that solved the same problem (Refero first, Mobbin only when useful, never averaged) gives a screen more product-specific structure than designing without them | **Rationale**. It is the owner's stated policy. No reference server was authenticated or measured. |
| Naming the defaults a direction can fall back to (a default card grid, empty hero, decorative metrics, gradient or glass, AI purple) as a check at the end of the reference step catches that fallback before building | **Hypothesis**. Untested. |
| "Compose the page, do not stack it" in `design-brief` keeps an ordinary request from shipping hero, one grid and footer | **Hypothesis**. A plan-level test could not reach it: no run invoked the skill (§8). It needs full builds. |
| The narrow-viewport check that every desktop destination stays reachable gets a mobile navigation built | **Hypothesis**. Untested. The build that lacked one predates the check (§8). |
| Writing an internal art direction when no research tool is connected gives a more product-specific page than falling back to defaults | **Hypothesis**. The step runs (6/6 in round 2, §8); its output was never compared with a run without it, or built. |
| Pointing at Motion's current docs prevents stale-API code in projects that use it | **Hypothesis**. Not tested. |
| Naming when Motion is justified (layout and shared-element transitions, exit choreography, gestures, interruptible springs) gets it used there and nowhere else | **Rationale**. It is the owner's stated policy. Only the platform-first half was tested (§7). |
| The whole setup improves engineering outcomes | **Untested.** There is no end-to-end measurement of output quality, and building an honest one is hard. |

---

## How to reproduce or extend

- **Capture ledger:** it is a TSV — `timestamp, label, exit, bytes_captured,
  bytes_surfaced, path`. Sum columns 4 and 5. The helper writes a row per run
  with no configuration.
- **The `/context` measurement that is missing:** run a representative long task
  with the layer disabled, record `/context`; repeat with it enabled. Same task,
  same repository, same starting state.
- **A harder dead-code benchmark:** the fixture design is described above; what
  it needs is distance between the reference and the call site, plus more than
  one run per arm.

If you extend any of these, please keep the evidence classes. A setup like this
attracts confident claims, and the honest answer to "does it work?" is currently
*"parts of it are measured, most of it is reasoned, and the end-to-end question
is open."*
