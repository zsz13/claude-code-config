# Follow-up probes: planning route, trivial work, established systems, fallback

Fixed before any run, 2026-09-30.

**Configuration.** Every run uses the live global configuration after the
follow-up change: the new `frontend-quality` and `design-brief`, 21st.dev at user
scope, and `record_inspiration_feedback` denied. `mcp__21st__get_component` is
disallowed in every run, to keep the free-tier retrieval quota; it does not
decide whether research starts. Runs are fresh headless sessions (`claude -p`,
`--permission-mode auto`, stream-json). Transcripts are kept in `logs/`
on the owner's machine and are not published.

**Measured per run:** skills invoked, `mcp__21st__*` calls by tool, Refero and
Mobbin calls, whether the 21st calls came before the first file write, and the
run's result and cost.

| Arm | Runs | Where | Prompt | Pass when |
|---|---|---|---|---|
| A. Substantial planning | 3 | empty dir | `plan-market.md` | `frontend-quality` or `design-brief` invoked, and at least one `get_inspiration` or `search` call |
| A. Substantial planning, other domain | 2 | empty dir | `plan-vet.md` | same |
| B. Substantial build | 2 | empty dir | `build-market.md` | at least one `get_inspiration` or `search` call before the first Write |
| C. Trivial fix | 2 | copy of a finished probe app | `fix-font.md`, `fix-copy.md` | zero `mcp__21st__*` calls |
| D. Trivial plan or question | 2 | same app | `ask-font.md`, `ask-where.md` | zero `mcp__21st__*` calls and `design-brief` not invoked |
| E1. Established system, existing patterns | 1 | copy of the control build | `est-saved.md` | zero `mcp__21st__*`, Refero and Mobbin calls |
| E2. Established system, new interaction pattern | 1 | copy of the control build | `est-compare.md` | informational: research is allowed here; record whether it ran |
| F. Fallback, no research tool | 2 | empty dir, `--strict-mcp-config` with no servers | `plan-market.md` | `design-brief` invoked, and the reply states an internal art direction with all four elements: references from the subject's own world, structure per section, rejected defaults, a signature element |

Arms A, D, E and F disallow Write, Edit and NotebookEdit. F is scored by one
person (the one who made the change) from the reply text.

## Amendment, before the reruns

E1 and E2 ran on a copy of the control build, whose `NOTES.md` (experiment
metadata, not product documentation) says "control build, no 21st". Both runs
cited that note as a reason not to use 21st, so both are recorded as confounded.
They are rerun twice each (E1b, E1c, E2b, E2c) on the same copy with `NOTES.md`
removed. Nothing else in that fixture mentions 21st. The pass criteria are
unchanged.

## Round 1 result (intermediate skill text)

Added after round 1's runs. Round 2 below replaces it for the final text.

| Arm | Passed | What happened |
|---|---|---|
| A. Substantial planning | 5/5 | Both skills loaded, then one `get_inspiration` and two or three `search` calls |
| B. Substantial build | 2/2 | One `get_inspiration` and one `search` before the first write |
| C. Trivial fix | 2/2 | No 21st call, and no skill loaded |
| D. Trivial plan or question | 2/2 | No 21st call, and no skill loaded |
| E1. Existing patterns (E1b, E1c) | 2/2 | No outside research; the prompt itself said the page reuses existing patterns |
| E2. New interaction pattern (E2b, E2c) | informational | Both researched with 21st |
| E1, E2 | not scored | Each cited the fixture's "no 21st" note, and 21st was still `pending` at init |
| F. No research tool | 2/2 | All four elements; but the references matched the skill's own example, which was the probe's domain |

## Round 2, fixed before its runs

A four-judge review of round 1 found problems in both the skill text and the
arms. The skill text was revised, so every arm is rerun on the final text. Round
1's results stay as the record of the intermediate text; only round 2 counts for
the final text.

What the review found:
- The fallback's worked example was the probe's own domain (used cars).
- The established-system prompts told the model the answer.
- E2 had no pass criterion.
- Nothing tested over-triggering, a substantial plan phrased as a question, or
  the fallback in an established system.
- Round 1's E1 and E2 also started with 21st "pending", not connected.

Round 2 transcripts are `logs/r2-*.jsonl`. A run in an arm that needs 21st, whose
init does not show 21st `connected`, is reported and not counted. Refero and
Mobbin are unauthenticated in every run, so no criterion depends on them.
Batches are at most six runs, to avoid the pending state.

| Arm | Runs | Where | Prompt | Pass when |
|---|---|---|---|---|
| A. Substantial planning | 5 | empty dir | `plan-market.md` ×3, `plan-vet.md` ×2 | `frontend-quality` or `design-brief` invoked, and at least one `get_inspiration` or `search` call |
| H. Substantial plan asked as a question | 2 | empty dir | `ask-homepage.md` | same as A |
| B. Substantial build | 2 | empty dir | `build-market.md` | at least one `get_inspiration` or `search` call before the first Write |
| C. Trivial fix | 2 | probe app | `fix-font.md`, `fix-copy.md` | zero `mcp__21st__*` calls |
| D. Trivial question | 2 | probe app | `ask-font.md`, `ask-where.md` | zero `mcp__21st__*` calls and `design-brief` not invoked |
| G. Boundary: small new component, plan for a small fix | 2 | control build without NOTES.md; probe app | `add-remove-all.md` (writes allowed), `plan-small.md` | zero `mcp__21st__*` calls and `design-brief` not invoked |
| E3. Established system, page the model must judge (saved cars) | 2 | control build without NOTES.md | `est-saved-open.md` | zero `mcp__21st__*` calls |
| E4. Established system, a pattern the site lacks (comparison) | 2 | control build without NOTES.md | `est-compare-open.md` | at least one `get_inspiration` or `search` call |
| F. No research tool, greenfield | 4 | empty dir, no MCP servers | `plan-market.md` ×2, `plan-vet.md` ×2 | `design-brief` invoked; the reply states an internal art direction with all four elements; its references are not the skill's example (wine shop) |
| EF. No research tool, established system | 2 | control build without NOTES.md, no MCP servers | `est-compare-open.md` | the reply keeps the site's existing style: no new signature element, and no new references for type or texture |

Arms A, H, D, E3, E4, F, EF and G's plan disallow Write, Edit and NotebookEdit.
F and EF are scored by one person (the one who made the change) from the reply
text. Every run disallows `mcp__21st__get_component`.

## Round 2 result

Added after the runs. Every run in an arm that needs 21st started with it
`connected`.

| Arm | Passed | What happened |
|---|---|---|
| A. Substantial planning | 5/5 | Both skills loaded; one `get_inspiration` and three `search` calls each |
| H. Substantial plan asked as a question | 2/2 | Both skills loaded; one `get_inspiration` and three `search` calls each |
| B. Substantial build | 2/2 | 21st called before the first write |
| C. Trivial fix | 2/2 | No 21st call, and no skill loaded |
| D. Trivial question | 2/2 | No 21st call, and no skill loaded |
| G. Small new component; plan for a small fix | 2/2 | No 21st call, and no skill loaded. The component was built and checked in a browser |
| E3. Established system, saved-cars page | **0/2** | Both loaded `frontend-quality`, called the page a new screen, added new interactions (a side-by-side view, an undo), and searched 21st |
| E4. Established system, comparison view | 2/2 | Searched 21st; styles kept from the site |
| F. No research tool, greenfield | 4/4 | All four elements in every reply, with references from each product's own world; none from the skill's example |
| EF. No research tool, established system | 2/2 | Structure only, styling from the site, no signature element |

## Where the published files are

The prompts are in [prompts/followup/](prompts/followup/). The exception is
`plan-market.md`, which is the same text as
[prompts/composition-plan.md](prompts/composition-plan.md). Per-run counts for
both rounds are in [followup-probes.json](followup-probes.json). The scored
fallback replies (round 2's F and EF) are in
[followup-fallback-plans.md](followup-fallback-plans.md). "Fixed before the runs"
is the author's own statement; nothing timestamps it independently.
