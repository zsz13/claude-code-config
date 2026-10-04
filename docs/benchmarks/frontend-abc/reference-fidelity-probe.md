# Reference fidelity probe, end to end with 21st connected

Evidence for [benchmarks §8](../../benchmarks.md#reference-fidelity-probe-end-to-end-2026-10-01).
Run 2026-10-01 on Claude Code 2.1.286, every session on `claude-opus-5-5`.
Per-run data (tool sequences, every 21st call and result, both replies, both
judge packets and reports) is in
[reference-fidelity-probe.json](reference-fidelity-probe.json).

## What it checks

One failure mode, the one the [visual energy probes](visual-energy-probe.md)
could not reach: a visually rich, reference-led direction is selected, and the
implementation comes out flatter, more static or more generic than its
reference.

One run, every step of the direction gate:

1. A major redesign request whose user states a taste for visually rich work.
2. Real 21st.dev research.
3. Three directions with preview references.
4. Directions that differ in register or composition, not only in energy.
5. At least one strongly reference-led, expressive direction.
6. That direction selected.
7. The pre-build AI-slop and visual-energy check (`design-brief` step 5).
8. Enough of the page built to test fidelity.
9. `get_component` used to adapt the central reference, if its source is
   available.
10. The result rendered.
11. `visual-design-judge` given the selected references' previews beside the
    final renders.
12. Five verdicts: did the composition, the motion and interaction, the
    hierarchy and the visual richness survive, and did the build fall back to
    SaaS or dashboard defaults?

The five verdicts in step 12 and the record list below were fixed before any
run, by the request that asked for the probe.

## Fixture

Seedkeep, exactly as in the [visual energy probe](visual-energy-probe.md#fixture),
with `npm install` run and committed as a git repository.

As published there, the fixture renders a blank page: it has no
`vite.config.js`, so Vite's default JSX transform calls `React.createElement`
with no `React` in scope. The earlier probes never rendered it, so none saw
this. The build run below added a three-line `vite.config.js` that loads
`@vitejs/plugin-react`, which was already a dependency.

## Harness

The configuration under test is this repository's working tree, with
`skills/`, `agents/` and `rules/` copied into the fixture's project `.claude/`.
Each session is headless `claude -p` with `--setting-sources project,local` and
`--strict-mcp-config`, as in the earlier probes, so no user-level skill,
plugin, hook or MCP server loads.

Two servers are added with `--mcp-config`:

```json
{ "mcpServers": {
  "21st": { "type": "http", "url": "${TWENTYFIRST_MCP_URL}", "headers": { "x-api-key": "${TWENTYFIRST_API_KEY}" } },
  "plugin_playwright_playwright": { "type": "stdio", "command": "npx", "args": ["-y", "@playwright/mcp@latest", "--headless", "--isolated"] }
} }
```

**21st without copying its key.** The file holds only placeholders. The same
shell command that starts the session reads the URL and key from the existing
user-scope 21st entry into the child's environment, and Claude Code expands
them when it connects. The key is never written to a file or printed. After
every run, a scan for the key's value found it in 0 files: the probe
directory, the three subprocess session transcripts, and the orchestrating
job's task outputs.

**Playwright under the plugin's server name**, so the tool names match what
`frontend-quality` and `visual-design-judge` list
(`mcp__plugin_playwright_playwright__*`). Without it the build could not
render, and the judge would have only Read, Grep and Glob.

`get_component` was allowed; the earlier probes disallowed it. The account is
on the free tier: 2 retrievals a day, 2 remaining at the start.

```bash
# PROBE_ROOT holds fixture/ (the app plus .claude/), mcp.json, logs/
cd "$PROBE_ROOT/fixture"
TWENTYFIRST_API_KEY="$(jq -r '.mcpServers["21st"].headers["x-api-key"]' ~/.claude.json)" \
TWENTYFIRST_MCP_URL="$(jq -r '.mcpServers["21st"].url' ~/.claude.json)" \
claude -p "$PROMPT" --setting-sources project,local --strict-mcp-config \
  --mcp-config "$PROBE_ROOT/mcp.json" --permission-mode acceptEdits \
  --output-format stream-json --verbose \
  --allowedTools mcp__21st mcp__plugin_playwright_playwright "Bash(curl:*)" "Bash(npm:*)" \
    "Bash(npx:*)" "Bash(ffmpeg:*)" "Bash(mkdir:*)" "Bash(ls:*)" WebFetch \
  < /dev/null > "$PROBE_ROOT/logs/$NAME.jsonl"
# Run 2 adds: --resume "$RUN1_SESSION" --fork-session, and
#   "Bash(cat:*)" "Bash(echo:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(grep:*)"
# The final judge runs from a directory that holds only .claude/agents/visual-design-judge.md
# and the evidence images, with Playwright alone in its MCP config:
claude -p "$(cat packet.md)" --agent visual-design-judge <same isolation flags>
```

Running the judge with `--agent` from that directory uses the working-tree
agent text with its own tool list (13 tools: Read, Grep, Glob and its ten
Playwright tools), and keeps the fixture's source out of its reach. The judge
the orchestrating session could spawn is the installed copy, which differs
from the working tree.

## Prompts

| Session | Prompt |
|---|---|
| Run 1, proposal | Seedkeep needs a major redesign: a whole new look and layout for the app. My taste runs to visually rich, expressive interfaces: bold typography, layered composition and real motion, the kind of site people bookmark for its design. Not a plain admin dashboard. |
| Run 2, a fork of run 1 | Go with A, the Packet Drawer. Build it. |
| Final judge | The packet in the JSON (`final_judge.packet`): product, data held, the user's taste, direction A verbatim with its scores and Adapts list, the four product-specific decisions the build named to its own judge, the reference evidence, the build evidence, and the five verdicts asked for. |

## Record

### 21st calls

| # | Session | Tool | Input | Result |
|---|---|---|---|---|
| 1 | run 1 | `get_inspiration` | "Expressive, visually rich lending tracker for a neighbourhood seed library …" | 10 components |
| 2 | run 1 | `search` | "editorial bento grid bold typography collection", component, limit 8 | 8 |
| 3 | run 1 | `search` | "stacked cards drawer index card catalog animated", component, limit 8 | 8 |
| 4 | run 1 | `search` | "horizontal timeline scroll seasons calendar", component, limit 8 | 8 |
| 5 | run 2 | `get_component` | id 26717 (Layered Stack) | source, 1 retrieval left |

The orchestrating session made one more call, `get_usage`, before run 1, to
read the quota. No session called a generation tool.

Run 1 took 22 turns, 1.5 minutes and $0.74. Of the 34 results, it opened 7
preview images: every reference it later showed. Every one of those 7 also
has a preview video. Run 1 opened none of them.

### References shown

| Direction | Scores | References (21st id) |
|---|---|---|
| A, The Packet Drawer (reference-led) | Energy 3 · Density 2 · Motion 3 · Fidelity high | Layered Stack (26717), Motion Card Stack (24669) |
| B, The Season Almanac | Energy 2 · Density 3 · Motion 2 · Fidelity medium | Project Index (30554), Editorial Testimonial (9637), Product Timeline (26930) |
| C, Seed to Seed | Energy 4 · Density 1 · Motion 4 · Fidelity medium | Stacking Cards (25275), Grainient Images Section (26179) |

Each reference was shown as a link to its 21st.dev page. A's Adapts list had
all six entries, with hierarchy and visual treatment "not taken". The three
energies differ, and with the user's stated taste the most restrained is a 2.
The compositions differ: a pile that re-sorts into a grid; large type rows
beside a season strip; full-width panels that pin and stack on scroll. Two of
the three share a print register: A on kraft paper, B in ink on cream. C is
full-colour and scroll-driven. As in every earlier text-3 and final proposal,
the reference-led direction is the most or second-most restrained of the
three, here the second. Unlike those, it is at Energy 3 and built on two
shipped components rather than the library's own paperwork. Run 1 wrote no
product file.

### Selected reference

Direction A, with both its references: Layered Stack for composition, spacing
and motion, Motion Card Stack for the interaction model and motion.

### `get_component`

Used once, as run 2's first call after the choice, for Layered Stack: a
1,727-character React component, built on GSAP and the shadcn `cn` helper. It
was not used for Motion Card Stack, the interaction-model reference, although
one retrieval remained.

The port follows `frontend-quality`'s "Component libraries". No Tailwind and
no GSAP were added, and no dependency at all. The mechanism is the source's:
cards keep their grid slots and are translated onto one pile, and spreading
clears the transforms. GSAP tweens became CSS transitions (520 ms, a settling
curve, 30 ms stagger). As in the source, hovering spreads the pile. The port
added focus, search and a "Keep spread out" toggle as further triggers.

Changed from the source: the source piles every card on one point with a
random rotation up to ±15°. The build fans the packets down a column, 46 px
apart, with a fixed rotation up to about ±3.7°, so that each flap's variety
name stays readable. That change came after the build's own judge reviewed it
(below).

### The pre-build check (step 7)

**Not visible.** Run 2's first visible text after the choice says "Next I'll
write the plan and the pre-build check, then build". The next text says
"Writing the build now", and four files were written. Neither the plan nor any
answer to questions 1 to 11 appears in the transcript. The packet that run 2
later gave its own judge lists "product-specific decisions the pre-build check
named", so a check may have run in the model's thinking. Thinking blocks are
redacted in the log (972 visible characters across 29 blocks), so this cannot
be decided either way. Question 11 ("is the plan flatter than the selected
references?") has no visible answer.

### The build's own review loop

Run 2 rendered at 1280 and 375 in its own browser, fixed layout problems it
saw, and spawned its `visual-design-judge` (47 tool calls). It gave that judge
the two references' **static** preview images, not their videos. The judge
returned ten findings. Run 2's reply says it fixed all ten; no second judge
pass checked that, and the final judge still found one of them (finding 6
below, the alternating button fills).

That judge's top finding was that the gathered pile showed one loan of six. Its stated
evidence was that "the Layered Stack reference keeps every card's label
visible even when piled". In the reference's video, the piled state shows only
the top card. The static preview shows the cards near their grid positions,
slightly tilted mid-transition, and never shows the pile. The fix, a fan, is
justified by the product's data either way, and it moved the composition
further from the reference.

Run 2 ended at 134 turns, 11.6 minutes and $4.53. The changes: `index.html`
(Google Fonts link), `src/App.css`, `src/App.jsx`, a new `src/motifs.jsx` (crop
line drawings) and the new `vite.config.js`. The sample data went from three
loans to nine, and `returned` became a date. The production build passed. Its
reply names one motion it gave up: when a packet leaves, the rest jump into
place instead of sliding.

### Final review (step 11)

The orchestrating session rendered the build at 1280×900 and 375×812 (touch
emulation), recorded the browser, and cut 8-frame strips of the spread, the
re-gather and the return flight. It also cut 8-frame strips from both
references' preview videos and composed three side-by-side boards: both
previews beside the build's first viewport, Layered Stack's frames above the
build's spread frames, and Motion Card Stack's frames above the build's return
frames. The judge read all three boards and five renders, and checked the live
app with Tab (20 turns, 57 s, $0.38).

The judge's verdicts, condensed:

| Asked | Verdict | Its evidence |
|---|---|---|
| Composition | **Partly survived** | The tilted, offset pile and its snap into a grid are there. It listed search as not triggering the snap, and marked that unverified. |
| Motion and interaction | **Survived at 1280, partly at 375** | The packet lifts off the pile, changes shape in flight and files into the drawer with weight. At 375 the drawer is about 1,000 px further down the page, so the filing and the stamp are never seen. |
| Hierarchy | **Partly survived** | The wordmark and the front packet are deliberate; "hierarchy from packet size" never appears (all six packets are one size), and at rest the loans are mostly unreadable. |
| Visual richness | **Survived** | "Richer than either reference": paper grain, printed colour, line drawings, wood grain, brass plate, stamp. |
| Generic defaults | **Mostly avoided** | No pills, no admin bar; the undo bar is a standard snackbar in the theme's dress, and badly placed. |

Its findings, most severe first:

1. **High:** at rest the pile hides the borrower and the date of five of the
   six loans. At 1280 it is a column of about 270 px with empty kraft on
   either side. ([1280 first viewport](boards/refprobe-1280-first-viewport.jpg))
2. **High, 375:** the signature return happens off-screen; only a counter
   changing from 3 to 4 confirms it. ([375 return frames](boards/refprobe-375-return-flight-frames.jpg))
3. **Medium:** the undo bar covers another packet's "Mark returned".
   ([1280 return frames](boards/refprobe-1280-return-flight-frames.jpg))
4. **Medium:** no hierarchy by packet size, although the direction said that is
   where hierarchy comes from.
5. **Low:** the stamp shows on the front drawer tab only, not "on each filed
   packet".
6. **Low:** "Mark returned" alternates light and dark fills between packets;
   "SEEDKEEP" repeats on every packet header.
7. **Low:** the mobile eyebrow leaves "2026" alone on a line.

**Checked by the orchestrating session**, because the judge's definition
rules out typing, clicking and scripts:

- **Search does trigger the grid.** Typing "tomato" spreads the pile, with 2
  packets shown. The loss the judge listed as unverified does not hold.
- **The spread can be interrupted.** Leaving the pile 200 ms into a spread
  sends the packets back from where they are, with no snap: the first packet
  went from translate 268 px to 35 px, then back to 173 px 80 ms later, and
  ended at 268 px.
- **The re-flow after a return is not animated.** In the 1280 return strip,
  the next packet already sits in the vacated slot by frame 3, while the
  returned one is still in flight. The judge did not report it. The build's
  reply did.

### Preserved and lost

Preserved:

- Layered Stack's mechanism, ported from its fetched source: the grid-to-pile
  translation, hover to spread, staggered settling, interruption.
- The weighted lift of a card off a pile, from Motion Card Stack, as the
  return flight into the drawer with the stamp landing after it, seen at
  1280. The reference itself cycles one stack (its caption: "Swiped photos
  move to the back of the stack"); "moving between stacks" is how run 1's
  direction read it, and the judge's "survived" was judged against that
  reading.
- Visual richness at or above the references, in the judge's view.
- No fallback to the SaaS defaults that `design-brief` names. The one stock
  pattern is the undo snackbar.

Lost or weakened:

- The tight, tossed deck became a near-straight fan (±3.7° against the
  source's ±15°). This followed a finding of the build's own judge that
  misdescribed the reference. The pile at rest still hides most of the data.
- Motion Card Stack's gesture, a drag that sends the top card to the back, was
  not taken, and its source was never fetched. A button and a flight replace
  it.
- Against the direction rather than the reference: the re-flow after a
  return snaps instead of moving with weight. Layered Stack's source has no
  removal handling, so this is not something its port dropped.
- The signature moment at 375, whose destination is off-screen.
- Hierarchy by packet size, which the direction named and the build never
  made.

## What this does not show

- It is one run on one fixture with one prompt. Every result here is
  **Observed**, and n = 1.
- There is no rebuild-from-preview arm, so nothing here says `get_component`
  kept the reference better than rebuilding it would have.
- The harness chose direction A, as the probe required; no user chose it.
- The orchestrating session knew the failure mode under test. It wrote the
  judge's packet, asked the five questions directly, and wrote the
  preserved-and-lost summary from the judge's report, its own checks and the
  build's source, which the judge never saw.
- Whether the pre-build check ran in redacted thinking cannot be determined;
  the record says only that it was not visible.
- Some failed calls were harness artefacts: the allowlist refused compound
  shell commands in run 1 and an edit to `.git/info/exclude` in run 2. The
  build kept its saved previews and screenshots in untracked folders inside
  the fixture.
- The references' preview images and video frames, and the boards that
  contain them, are third-party and are not published here. Only the three
  build-only renders linked above are.
