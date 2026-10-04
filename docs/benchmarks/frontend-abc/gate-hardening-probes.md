# Pre-build gate and motion fidelity probes

Evidence for [benchmarks §8](../../benchmarks.md#pre-build-gate-and-motion-fidelity-probes-2026-10-01).
Run 2026-10-01 on Claude Code 2.1.286, every session on `claude-opus-5-5`.
Per-run data (tool logs with millisecond timestamps, every 21st call, the
replies, each `.design/prebuild.md`, the build's judge packet and report, and
the motion check) is in [gate-hardening-probes.json](gate-hardening-probes.json).

## What changed

The [reference fidelity probe](reference-fidelity-probe.md) found two gaps,
and the text was changed for each:

1. **The pre-build check left no trace.** The build announced it and then wrote
   four product files. `design-brief` step 5 now writes the check to
   `.design/prebuild.md`. The file holds only the selected direction, its
   references, the answers to questions 1 to 11 and what the check revised.
   No product UI file may be written before it exists, in headless and
   autonomous runs too, and it must be written in the current task.
   `frontend-quality`'s "Direction gate" and `rules/frontend.md` say the same.
2. **A motion-led reference was judged from a still.** Neither run of that
   probe opened a preview video, and the build's own judge misdescribed a
   deck's resting state. When a selected reference's motion or gesture
   matters, `design-brief` step 5 now requires its video, its live demo or
   its source before implementation. It also requires a behavior note in the
   plan: trigger, motion, timing, mobile, reduced motion. A high-fidelity
   reference-led direction keeps a ledger of each adapted aspect: preserved,
   intentionally changed or lost, with the reason for each change or loss.
   `frontend-quality`'s "Review integration" gives `visual-design-judge` the
   notes and frames of the reference and of the build at both widths, plus
   the intentional changes, but not the builder's own verdicts. The judge
   reports each aspect, and motion fidelity at desktop and at mobile
   separately.

A blind spec review and a correctness review of the text ran before any
probe, and their accepted findings were applied first. These were:
- a stale file from an earlier direction would have satisfied the gate;
- there was no fallback when motion cannot be inspected;
- an intentional change made because it was simpler to build is now a loss;
- the rule's scope missed a request that names its own references;
- the motion trigger was worded more narrowly than the request;
- an unrequested "keep it out of commits" line was removed;
- the score line is required only where the direction has one;
- "project root" is defined for a monorepo.

Every probe below ran the final text. After the runs, `diff -rq` showed that
each fixture's `.claude/` matched the working tree.

## What each probe checks

The checks come from the request that asked for the probes, and were set
before any run.

**Probe 1, the pre-build gate.**
- A major redesign leaves `.design/prebuild.md`.
- The file is written before the first product UI write.
- Small UI fixes do not create it.

A product UI file is `index.html` or anything under `src/` or `public/`. The
order is read from a tool log with millisecond timestamps, and checked
against the files' birth times. The log records the file's completed write
(PostToolUse) and the first product UI write's start (PreToolUse).

**Probe 2, motion fidelity.**
- A motion-led 21st.dev reference is selected.
- Before the first product UI write, the run inspects that reference's video,
  live demo or source, not only its preview image.
- The plan has a behavior note covering trigger, motion, timing, mobile and
  reduced motion.
- The final review reports each adapted aspect as preserved, intentionally
  changed or lost, and motion fidelity at desktop and mobile.

## Fixture

Seedkeep, as in the [visual energy probe](visual-energy-probe.md#fixture), with
`npm install` run. The three-line `vite.config.js` that the reference fidelity
build added is committed in the baseline: without it the published fixture
renders a blank page ([reference fidelity probe](reference-fidelity-probe.md#fixture)).
Each cell is a fresh copy, committed as its own git repository.

## Harness

The harness is the one in the [reference fidelity probe](reference-fidelity-probe.md#harness):
- `claude -p` with `--setting-sources project,local` and `--strict-mcp-config`;
- 21st over HTTP, with its URL and key passed through environment
  placeholders and never written to a file;
- Playwright MCP under the plugin's server name;
- `--permission-mode acceptEdits`.

Four things were added.

**A tool log.** A hook passed with `--settings` runs on every PreToolUse and
PostToolUse. It appends a timestamp, the event, the tool name and its input to
a log outside the fixture. It prints nothing and always exits 0, so the model
never sees it.

```python
# log-tool.py, run by both hooks
d = json.load(sys.stdin)
ti = json.dumps(d.get("tool_input", {}))[:400]
ts = datetime.datetime.now().isoformat(timespec="milliseconds")
open(os.environ["PROBE_TOOLS_LOG"], "a").write(f"{ts}\t{d['hook_event_name']}\t{d['tool_name']}\t{ti}\n")
```

**A stop for probe 1's builds.** A watcher stopped each of the two probe-1
redesign builds 20 s after its first completed product UI write. The gate is
decided by then, so the rest of the build was not run. Those two runs have no
cost or duration on record.

**`get_component` per probe.** It was disallowed in probe 1 and allowed in
probe 2. The account is on the free tier, and only one retrieval was left for
the day, so it was saved for the motion probe.

**`Bash(ffprobe:*)` in the allowed tools,** beside the earlier probe's list.

After the runs, a search for the key's value found it in 0 files. The search
covered the probe directory, the six subprocess transcript folders, the
orchestrating job's task outputs and `docs/`.

## Prompts

| Run | Prompt |
|---|---|
| p1-trivial-1 | The footer copyright text is too small to read. Bump it to 14px. |
| p1-trivial-2 | The button on each loan says 'Return'. Change its label to 'Mark returned'. |
| p1-chosen-r1 | Completely rethink Seedkeep's frontend visual design and UX while preserving its existing functionality. |
| p1-chosen-r2, a fork of r1 | Go with B. Build it. |
| p1-auto | Seedkeep needs a major redesign: a whole new look and layout for the app. I won't be around to answer questions, so choose the direction yourself and build it. |
| p2-motion-r1 | Seedkeep needs a major redesign: a whole new look and layout for the app. My taste runs to visually rich, expressive interfaces: bold typography, layered composition and real motion, the kind of site people bookmark for its design. Not a plain admin dashboard. |
| p2-motion-r2, a fork of r1 | Go with B. Build it. |

The trivial and redesign prompts are the earlier probes' prompts. p2-motion-r1
is the reference fidelity probe's run 1 prompt. Each B was picked after
reading that proposal:
- In p1-chosen, B was the low-fidelity direction, led by physical artifacts,
  with one 21st component used only for its status labels. It tests the gate
  without a reference-led build.
- In p2-motion, B was the reference-led, motion-led direction.

## Probe 1: the pre-build gate

| Run | Skills | `.design/prebuild.md` written | First product UI write | Lead | Words | Only the four items |
|---|---|---|---|---|---|---|
| p1-chosen-r2 (user chose B) | `frontend-quality`, `design-brief` (in r1) | 11:18:59.857 | 11:19:47.626, `src/App.jsx` | 48 s | 408 | yes |
| p1-auto (chose itself) | `frontend-quality`; `design-brief` read with Read | 11:18:13.223 | 11:18:33.015, `src/App.jsx` | 20 s | 633 | no: it also lists all three directions considered |
| p2-motion-r2 (user chose B) | both (in r1) | 11:20:20.341 | 11:21:41.533, `src/data.js` | 81 s | 764 | close: it adds the plan's Adapts table |
| p1-trivial-1 | none | none; no `.design/` | 11:17:12, `src/App.css` (one line) | n/a | n/a | n/a |
| p1-trivial-2 | none | none; no `.design/` | 11:17:10, `src/App.jsx` (one line) | n/a | n/a | n/a |

All three redesigns wrote the file before their first product UI write, and
both small fixes wrote one line and no file. In each redesign the file's birth
time matched the log to the second. Every fixture started without the file,
so each was written during its run and after the choice. In p1-chosen's fork
it was the run's first tool call. In p2-motion's fork it came after the
reference inspection below. In the autonomous run, it came after research and
before code.

Each file records who chose the direction:
- p1-chosen: "Chosen by the user ("Go with B. Build it.")".
- p1-auto: "Chosen by the agent; the user asked for an autonomous choice". It
  chose a mix: A's composition and interaction with B's visual language.
- p2-motion: "Chosen by the user".

Each file answers questions 1 to 11 and lists what the check revised:
- p1-chosen dropped status pills for a flap stamp, and moved the tally into
  the masthead.
- p1-auto dropped status pills, and styled the tabs as ledger index tabs.
- p2-motion limited the spread grid to a residual tilt with no pills, and
  added a button beside the drag-to-return gesture.

The proposal runs wrote no product file and no `prebuild.md`. p2-motion-r1
saved its reference previews in `.design/refs/`, the same folder, which the
text does not forbid.

## Probe 2: motion fidelity

### Research and the proposal

| # | Run | Tool | Input | Result |
|---|---|---|---|---|
| 1 | r1 | `get_inspiration` | "expressive editorial lending tracker for a community seed library …" | 8 components |
| 2 | r1 | `search` | "stacked cards swipe deck animation", component, limit 6 | 6, including "Card stack" (24669, shown as Motion Card Stack) and Layered Stack (26717) |
| 3 | r1 | `search` | "editorial kinetic typography hero large type scroll", component, limit 6 | 6 |
| 4 | r1 | `search` | "animated list filter search layout transition", component, limit 6 | 6 |
| 5 | r2 | `get_component` | id 24669 (Motion Card Stack) | source; the day's last free retrieval |

r1 read eight preview images and no video. It proposed three directions:

| Direction | Scores | References |
|---|---|---|
| A, Circulation Desk | Energy 2 · Density 3 · Motion 2 · Fidelity medium | Project Index, Editorial Testimonial |
| B, The Packet Deck (reference-led) | Energy 3 · Density 2 · Motion 3 · Fidelity high | Motion Card Stack, Layered Stack |
| C, Season Almanac | Energy 4 · Density 2 · Motion 4 · Fidelity low | Hero Shutter Text, Stacking Cards, Interactive List Preview |

B is built on the same two components as direction A in the reference
fidelity probe. Its Adapts list takes composition and hierarchy from Motion
Card Stack, spacing from Layered Stack, and interaction and motion from both.
Visual treatment is "not taken". r1 recommended B.

### Inspection before the first product write

The first product UI write was at 11:21:41.533. Before it:

| Time | Event |
|---|---|
| 11:19:06 | `curl` both preview videos (`motion-card-stack.mp4`, `layered-stack.mp4`) |
| 11:19:11 | `ffmpeg … fps=3,scale=360:-1,tile=4x3` frame sheets of both |
| 11:19:15 | Read both frame sheets |
| 11:19:51 | `get_component` 24669, Motion Card Stack |
| 11:20:20 | `.design/prebuild.md` written |

Both references were inspected from their videos, and Motion Card Stack also
from its source. Layered Stack's source was not fetched; its note says why:
"Source not retrieved because the daily quota is spent".

### Behavior notes

Both are in `.design/prebuild.md`, and each covers all five fields.

**Motion Card Stack**, from its source:
- The trigger is an x-axis drag on the top card.
- The card rotates by its resting tilt plus 10° per 400 px.
- A drag past half the width, or a flick, sends it to the back while the next
  card scales up.
- Spring constants and the `sin(index) × 5°` resting tilt are given.
- The reference shows no mobile behavior. The note says this product's version
  drags by touch at ~375 and adds buttons.
- The reference has no reduced-motion handling. The product's version uses
  Motion's `reducedMotion="user"`.

**Layered Stack**, from frames:
- The trigger is hover.
- The grid converges into a fanned pile in about 0.5 s.
- At ~375 the product uses a two-column grid.
- With reduced motion, the switch is instant.

This note has the direction reversed. 21st's description of the component is
"fans children into a shuffled deck and re-stacks them into a neat grid on
hover". The earlier probe's fetched source agrees: hovering spreads the pile.
The frames show both states, but not which one hover produces, and the note
guessed wrong. That is the same kind of misreading the change was meant to
prevent, made this time from video instead of a still. The source would have
settled it, but the day's retrieval had gone to Motion Card Stack. The build
was not hurt here, because it opens on the pile and toggles to the grid, which
matches the reference's resting state anyway.

The build added `motion` as a dependency, which direction B had named in its
tradeoff.

### The build's review

The build rendered at 1280 and 375, captured motion frames and spawned
`visual-design-judge` once. The packet carried:
- shortened behavior notes: motion and timing for both references, with no
  mobile or reduced-motion fields;
- the six Adapts entries;
- three intentional changes, each with its reason: drag into the envelope to
  log a return, depth-based scale instead of the reference's formula, and a
  toggle instead of hover;
- eight motion frames at 1280 and four at 375.

It did not carry the builder's own verdict on what survived. Packet and report
are verbatim in the JSON.

The judge's per-aspect report:

| Aspect | Verdict |
|---|---|
| Composition | preserved |
| Hierarchy | preserved, with the named scale change |
| Spacing rhythm | preserved |
| Interaction model | swipe and toggle preserved; drag-to-return changed as named, but it arms in the wrong place on desktop |
| Motion | drag-to-rotate preserved; swipe-to-back **partly lost** (the card fades off to the right instead of tucking behind the stack); deck-to-grid **mostly lost** (too fast to see in its frames) |
| Visual treatment | changed as intended |

It gave motion verdicts for desktop and mobile separately. Both motion losses
are under desktop, from 1280 frames. On mobile, the judge called the swipe
faithful ("as in the reference"), did not assess the spread, and found the
drop target and the Undo bar below the first screen. It cannot drag, so the
swipe verdict rests on the builder's frames. For the Spread toggle it pressed
keys itself, but its screenshots caught only the end state.

It also listed eight defects, two marked High:
- the drop target arms away from the envelope;
- the backdrop name breaks into fragments.

Its "not verified" list includes a flick throw and real touch.

### After the review

The build made 28 edits to `src/`, and attempted one to `.git/info/exclude`,
which the harness refused. Between them it ran two scripted checks that took
screenshots, after 23 and after 26 of the edits. It read ten of those renders:
- at 1280: the deck, a drag onto the envelope and the drop that followed, the
  Undo notice, a frame 150 ms into the Spread switch, and Spread at rest;
- at 375: the deck, a drag, and the result after it.

The scripts also asserted that the drop does not arm on a plain downward drag
and that the arrows stay in place.

No swipe was re-captured, and the judge was not run again.

The final reply has a fidelity paragraph. It lists what was kept (the stacked
composition, the dominant top packet, the loose tilts, swipe-to-leaf and the
drag physics) and three changes made on purpose. It gives no reasons for
those changes there; they were in the judge packet. It has no "lost" entry,
and says the two motion losses the judge found were fixed.

### The orchestrator's motion check

The judge could not record motion, and nobody had re-captured the swipe after
the fixes. So the orchestrating session served the final build and recorded
it with Playwright's `recordVideo` at 1280 × 800 and at 375 × 812: a mouse
drag on the top packet, then a click on Spread. Frames came out at 30 fps;
[gate-hardening-motion-frames.jpg](boards/gate-hardening-motion-frames.jpg)
holds them. The rows are the 1280 swipe, the 1280 spread, then the 375 swipe
over the 375 spread. All are build frames only.

- **Swipe, both widths:** after release, the swiped packet slides back behind
  the new top packet within a few frames, on the order of 100 ms. It no longer
  fades out in place.
- **Spread, both widths:** the pile opens into the grid over about 6 frames,
  roughly 200 ms, with packets visibly between positions. The build's own note
  puts Layered Stack's transition at about 0.5 s, so the move is visible but
  quicker than the reference.

The recording's frames and the script's time marks are not aligned to the
frame, so these durations are approximate.
- **375:** the deck, the arrows and the "Log seed return" button now fit in
  the first screen. For one frame at the start of the morph, several packets'
  buttons overlap.

### Result

| Check | Result |
|---|---|
| Motion-led 21st reference selected | yes: B, on Motion Card Stack and Layered Stack |
| Inspected in motion before the first product write | yes: both videos as frame sheets, and one source |
| Behavior note with the five fields | yes, for both references. Motion Card Stack's matches its source. Layered Stack's, from frames, reverses which state hover produces |
| Final review reports preserved, changed and lost | **the judge, yes**: per aspect, with desktop and mobile motion separate. **The final reply, partly**: kept and changed on purpose, no reasons, no lost entry |
| Motion fidelity at desktop and mobile | the judge found two motion losses at 1280, called the 375 swipe faithful and did not assess the 375 spread. The build fixed both losses, and the recording shows the fixed behavior at both widths |

## What this does not show

- **Run counts.** There were three redesign runs for the gate, one per cell,
  on the fixture and prompts the earlier probes used, so the result is
  in-sample. Nothing enforces the rule beyond the text. A run that wrote code
  first would show in the log; none did, in 3 of 3.
- **Whether the check shaped the plan.** It cannot be told whether the file
  records a check that shaped the plan, or a write-up of a plan already made.
  The "revised" entries are the model's own account.
- **Contents.** "Only the four items" held strictly in 1 of 3 files.
- **Untested paths:**
  - a stale `prebuild.md` from an earlier direction (every fixture started
    without one);
  - the fallback when no video, demo or source exists;
  - a monorepo;
  - a component-system change;
  - a request that names its own references.
- **The small fixes** loaded no skill. They show that the file is not written
  outside the check's context, not that the sentence excluding small fixes
  works.
- **Fixes after the review.** No second judge pass ran after the build's fixes.
  The orchestrator's recording covers the two motion items. The other eight
  fixes rest on the build's own renders and its reply.
- **Reduced motion.** The behavior notes describe it, and nobody rendered it.
- **The judge's motion evidence.** It cannot drag, so its swipe verdict
  rests on frames the builder chose; here they were enough to find a real
  loss. Its key presses caught only end states.
- **Video frames can mislead too.** Inspecting the video did not stop one
  behavior note from reversing its reference's trigger. Only the source, or a
  live demo where the trigger is driven, shows which state an input produces.
- **No control arm.** The reference fidelity probe used the same two
  references with static previews only. That probe's direction, plan and text
  differ in more than this change, so it is context, not a control.
- **Independence.** The session that changed the text also ran and scored the
  probes.
