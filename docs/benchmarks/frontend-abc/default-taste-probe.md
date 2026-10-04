# Default taste probe

Evidence for [benchmarks §8](../../benchmarks.md#default-taste-probe-2026-10-03).
Run 2026-10-03 on Claude Code 2.1.289, every session on `claude-opus-5-5`.
Per-run data (tool sequences, every 21st call, each reply in full, the blind
scorer's packets and its scores) is in
[default-taste-probe.json](default-taste-probe.json).

## What changed

The owner's default taste is now written into the existing flow, with no new
skill or agent:

- **`design-brief` step 2** states the default register: where the request
  leaves open how strongly the design speaks, it is expressive but controlled.
  It lists what that asks for (a first viewport with one focal point and a
  visible primary action, layered composition, contrast between sections,
  bold typography, real motion, one memorable interaction) and the defaults it
  rules out (restrained enterprise UI, flat grey dashboards, white cards on
  neutral everywhere, a generic SaaS template, a dark technical console, and
  others). The register is not open when the request asks for restraint, when
  the chosen references are deliberately minimal, when the work keeps an
  established design system's look, or when the proposal names a product
  reason intensity would harm.
- **Step 3** prefers visually excellent references among those that fit. A
  plain one can calibrate a direction but not lead one. When nothing that
  fits is also strong, the search widens to an adjacent problem. No
  branding, logos, illustrations, photography or copy is taken from a
  reference.
- **Step 4**, under the default register:
  - The three directions sit at energies 2, 3 and 4, so none is a 1.
  - They differ in composition and in visual register. Each direction's
    Visual character now starts by naming its register. No two may share
    one, however they name it: two paper-and-ink directions share one.
  - The energy scale names its floor: a screen whose main unit is rows of a
    table or ledger on a plain surface is a 1, whatever its paper tint or
    typeface.
  - The reference-led direction is at 3 or 4.
  - Its Adapts entries take motion when the reference has it. Hierarchy,
    spacing rhythm and visual treatment are taken unless a product reason is
    named.
- **Step 5**:
  - A reference-led, high-fidelity plan keeps its references' composition,
    interaction, motion, hierarchy, rhythm and richness.
  - The visual-energy questions now also ask:
    - what moves;
    - what gives the interface its energy;
    - whether the plan has collapsed into a dashboard.
  - A first viewport that reads as a generic form, card grid or dashboard is
    revised before code.
- **`frontend-quality`**:
  - The direction gate states the 2-3-4 default.
  - An autonomous choice takes the expressive-but-controlled direction, not
    the safest.
  - Component research keeps the visually strongest results that fit.
  - "Motion" makes an open register move by default. The selected direction's
    Motion score sets how much, and reduced motion replaces movement rather
    than making the default static.
- **`visual-design-judge`**, for an expressive or reference-led direction,
  also judges energy, richness, hierarchy, rhythm and dynamism. It may return
  "technically correct but visually too bland", "reference richness was lost",
  "interaction energy was flattened" or "composition drifted back to Claude
  defaults". Restraint findings stay about dilution, not energy.
- **`rules/frontend.md`** names the default register, for substantial work
  only.

## Order of work

1. **Baseline.** Three redesign proposals on the text before the change,
   which this page calls *base*.
2. **Text 1.** The first version of the change, then three proposals on it.
3. **Review.** A blind spec review and a blind adversarial review of text 1.
   Nine findings were accepted, one of them raised by both reviewers:
   - The design-system exception switched the default off even for a
     redesign that asks for a new look.
   - "Adapt closely" covered every selected reference, against fidelity low
     and the mix rule.
   - The rule line and the skill's first line still said there is no default.
   - The judge's energy check needed a score that may not exist.
   - The motion default ignored the chosen direction's Motion score.
   - The rule did not limit the default to substantial work.
   - A pronoun in the rule pointed at the wrong skill.
   - There was no fallback when no strong reference fits.
   - The restraint clarification could hide dilution.
4. **The register slot.** By this session's reading, two directions shared
   one paper-and-ink look in two of the three text 1 replies; the later blind
   scorer found a shared paper or print register in all three. A required register slot in Visual character
   was added with the review fixes. That made *text 2*.
5. **Criteria.** The criteria below were written down while the text 2 runs
   ran, before any text 2 result was read. Base and text 1 had already been
   read, so they were judged against criteria written after their results
   were seen.
6. **Text 2 runs:** three redesign proposals, two small fixes and one calm
   request.
7. **Blind scoring, round 1,** of all nine redesign proposals so far (base,
   text 1, text 2). Text 2 missed two of the criteria:
   - One of its three proposals had only one direction the scorer rated 3 or
     4.
   - Every new proposal kept at least one direction the scorer called muted,
     most often a ruled ledger on paper. The runs had rated those directions
     2, and once 3.

   Register, reported separately rather than as a criterion, differed only
   "partly" in two of the three.
8. **The final text** adds two sentences:
   - On the energy scale: a screen whose main unit is table or ledger rows on
     a plain surface is a 1.
   - On the register slot: two paper-and-ink directions share one register,
     whatever they are called.
9. **Final runs:** the same three redesign prompts and the calm request.
10. **Blind scoring, round 2,** by a fresh scorer, of the final three and of
    the three base proposals again.

The two sentences in step 8 answer what the round 1 scorer found, and were
tested on the same fixture and prompts, so the final result is in-sample.

## Criteria

For each redesign proposal, on every text:

- **C1.** It stops with three directions and a question, and no product file
  changes. Saved reference previews and Playwright output do not count as
  product files.
- **C2.** Self-rated energies: none at 1, and at least two of the three at 3
  or 4.
- **C3.** A reference-led direction (fidelity high, one or two references) is
  at Energy 3 or 4. Its lead reference is a shipped product or component, not
  a physical-world object, and is shown with a preview image or URL.
- **C4** (text 2 and final, since the slot is new). Each direction names its
  register first, and no two names match.

**Blind scoring.** A fresh scorer session on `claude-opus-5-5` scored the
redesign proposals in each round, two sessions in all: round 1 the nine of base, text 1 and text 2; round
2 the three final ones and the three base ones again.
- It knew nothing of the arms or the change. The labels were shuffled, and
  each proposal was cut to its three direction sections with their score
  lines removed.
- It was told to Read every cited 21st component's preview image, which the
  packet downloaded beside the text. One text 1 proposal (t1-r2a) reached
  round 1 with previews for only two of its six components. Its other four
  URLs ended in a full stop, which the packet builder did not strip. Every
  other packet was complete.
- For each direction it gave:
  - its own energy, 1 to 4, on the skill's scale;
  - a *muted* flag: a data table or ledger on a neutral surface, generic SaaS,
    flat grey, white cards on neutral, or a dark console;
  - whether the direction is reference-led and ambitious: built on a shipped
    reference, and scored 3 or 4.
- For each proposal it gave:
  - whether composition differs, and whether register differs (yes, partly or
    no);
  - how many of the three directions are strong.

**Small fixes** (text 2). Exactly the one line asked for changes, no skill
loads, and no `.design/` is created.

**Calm request** (text 2 and final). Three directions, at least one at Energy 1 and
none at 4. The reply does not argue the user out of calm.

## Fixture

Seedkeep, as in the [visual energy probe](visual-energy-probe.md#fixture),
with `npm install` run and the three-line `vite.config.js` committed, as in
the [gate probes](gate-hardening-probes.md#fixture). Each cell is a fresh copy,
committed as its own git repository, with the configuration under test in its
project `.claude/`.

## Harness

The harness is the one in the [reference fidelity probe](reference-fidelity-probe.md#harness):
- `claude -p` with `--setting-sources project,local` and `--strict-mcp-config`;
- 21st over HTTP, with its URL and key passed through environment
  placeholders and never written to a file;
- Playwright MCP under the plugin's server name;
- `--permission-mode acceptEdits`, `--max-turns 60`;
- `mcp__21st__get_component` disallowed, since no run went past the proposal.

The arms differ only in what is copied into `.claude/`. *Base* is a copy of
`skills/`, `agents/` and `rules/` taken before the change. *Text 1*, *text 2*
and *final* are copies of the working tree at those points. The published
files are the final text, rewrapped: with whitespace collapsed, they match
word for word. Claude Code's own bundled
skills (among them one named `design`) were listed in every session; no run
invoked any of them.

## Prompts

| Run | Prompt |
|---|---|
| `b-`, `t1-`, `f-`, `g-` `r1a` and `r1b` (base, text 1, text 2, final) | Completely rethink Seedkeep's frontend visual design and UX while preserving its existing functionality. |
| `b-`, `t1-`, `f-`, `g-` `r2a` | Seedkeep needs a major redesign: a whole new look and layout for the app. Go ahead and build it. |
| f-t1 | The footer copyright text is too small to read. Bump it to 14px. |
| f-t2 | The button on each loan says 'Return'. Change its label to 'Mark returned'. |
| f-calm, g-calm | Seedkeep needs a major redesign: a whole new look and layout for the app. Keep it calm, minimal and utility-first: volunteers use it at a busy lending table and just need to get through the queue. |

The redesign and small-fix prompts are the earlier probes' prompts. None of
them states a taste, so the default register is what is being tested.

## Result

Every redesign run read `design-brief`: through the Skill tool, Read, or a
shell `cat`. Neither small fix did.

### From the replies

Energies are each reply's own ratings, in the order A-B-C, for runs r1a, r2a
and r1b.

| Text | Runs | C1: stopped, no product file | C2: no 1, two at 3+ | C3: reference-led at 3+ on a shipped reference | C4: registers named, all different | Energies |
|---|---|---|---|---|---|---|
| Base | 3 | 3/3 | 1/3 | 1/3 | (no slot) | 1-3-4, 2-3-4, 1-2-4 |
| Text 1 | 3 | 3/3 | 3/3 | 3/3 | (no slot) | 3-2-4, 2-3-4, 2-4-3 |
| Text 2 | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 2-3-4, 4-3-2, 2-3-4 |
| Final | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 3-2-4, 2-4-3, 4-3-2 |

**Base.** In two of the three base proposals, the reference-led direction was
the Energy 1 one: a ledger of loans built on data-table components (Data Table,
Records Table, Streaming Data Rows). One of those replies called it "efficient
but plain". The third base proposal led with a Kanban board at Energy 4.

**The new texts.** In all nine proposals, the reference-led direction was at
3 or 4. Its first-listed references were stack, card and ticket components:
Admit One Ticket, Stacked Activity Cards, Layered Stack (twice), Engraved
Ticket, Stacking Cards, Card Hand Gallery, Tracker Card and Hover Stack.

No reference-led direction was built on a table.

**C4 holds in form.** Every text 2 and final direction named its register
first, and the names differed. Five of the six replies used the slot's own
examples as register names, nearly word for word:
- all three text 2 replies: "ink on cream paper" twice, "dark ink on cream
  ledger paper" once, and "bold flat colour blocks" once;
- two of the three final replies: "dark ink on cream paper", "bold, flat
  colour blocks" and "bold flat blocks of colour".

One final reply met C4 in form but broke the final text's own rule, with two
paper-and-ink directions ("kraft paper and ink", "green ink on linen").

### Blind scorer

Energies here are the scorer's, in the same order.

| Text | Round | Energies | Directions at 3+ | Proposals with two at 3+ | Muted directions | Proposals with a reference-led, ambitious direction | Composition differs | Register differs |
|---|---|---|---|---|---|---|---|---|
| Base | 1 | 1-2-3, 1-2-2, 1-2-2 | 1/9 | 0/3 | 5/9 | 0/3 | 3/3 yes | 0/3 yes, 3 partly |
| Base | 2 | 1-2-3, 1-2-2, 1-2-2 | 1/9 | 0/3 | 5/9 | 0/3 | 3/3 yes | 0/3 yes, 3 partly |
| Text 1 | 1 | 3-2-3, 1-3-3, 2-3-2 | 5/9 | 2/3 | 3/9 | 3/3 | 3/3 yes | 0/3 yes, 3 partly |
| Text 2 | 1 | 2-3-3, 3-2-2, 2-3-3 | 5/9 | 2/3 | 4/9 | 3/3 | 3/3 yes | 1/3 yes, 2 partly |
| Final | 2 | 3-2-3, 2-3-2, 3-3-2 | 5/9 | 2/3 | 2/9 | 3/3 | 2/3 yes, 1 partly | 2/3 yes, 1 partly |

**The two scorer sessions agreed.** Both scored the three base proposals, and
gave the same energies, the same muted flags and the same verdicts on
composition and register.

**The scorers rated lower than the replies did.**
- On the new texts, all nine directions their replies called Energy 4 came
  out at 3. In base, the three 4s came out at 3, 2 and 2.
- Four more new-text directions came out a level below their replies:
  - a text 1 ledger, from 2 to 1;
  - a text 1 card catalogue, from 3 to 2;
  - a text 2 ledger, from 3 to 2;
  - a final card-catalogue drawer, from 3 to 2.
- No direction came out higher.

**Muted directions.** On text 2, 4 of 9 directions were muted: three ledgers
of rows, and one set of lanes in muted earth tones. On the final text, 2 of 9 were
muted:
- a list of specimen labels in ruled sections;
- a season strip over a list.

Both were their proposals' Energy 2 direction.

**Against the criteria,** the final text meets:
- a reference-led, ambitious direction in every proposal: 3/3;
- no Energy 1 by either count.

It falls short on:
- two directions at 3 or 4 by the scorer: 2/3;
- no muted direction: 1/3;
- composition that differs: 2/3. The third had two directions built on
  layered packet cards.

Register, reported separately, differed in 2/3.

### Small fixes and the calm request

| Run | Text | Result |
|---|---|---|
| f-t1 | text 2 | 2/2 for the pair. f-t1 changed one line, the `.footer small` font size from 11px to 14px. No skill loaded, no `.design/`, $0.13 |
| f-t2 | text 2 | One line, the button label. No skill loaded and no `.design/`. It also ran `npm run build` as its own check, $0.14 |
| f-calm | text 2 | Energies 1-2-3, no 4. It said "You asked for calm, minimal and utility-first, so all three options stay low-key", and recommended the Energy 2 direction. Its score line drifted from the literal format ("Bold 1 · Dense 3 …") |
| g-calm | final | Energies 1-2-3, no 4, in the literal format. Under the Energy 1 direction it wrote "Energy 1 is allowed here because you asked for calm, minimal and utility-first". It recommended B or A and did not argue for more energy |

The small-fix runs ran on text 2. The final text changes only `design-brief`
step 4, which a small fix never loads.

### Cost

16 runs, $10.22 in total by the runs' own result events:
- $1.86 for base;
- $2.18 for text 1;
- $3.42 for text 2, small fixes and calm included;
- $2.76 for the final text.

The reviewers' and scorers' sessions are not included.

## What this does not show

- **Nothing was built.** The probe stops at the proposal. Whether a page built
  from a stronger proposal is richer, whether the motion default and the
  sharper pre-build questions change a plan, and whether the judge uses its
  new verdicts were not run.
- **Energy is a model's judgement.** The replies rate themselves, and one
  scorer model rates them again. That scorer was blind to the arms, but it
  shares training with the model that wrote the proposals. No person scored
  them.
- **Small and in-sample.** Three runs per text, on one fixture and two
  prompts. The final text's two sentences answer what the round 1 scorer
  found, on those same prompts.
- **The same session ran everything.** It made the change, wrote the
  criteria, ran the arms and wrote this record.
- **The paper register persists.** Seedkeep's own world pulls toward paper,
  ink and packets. Every text, base included, kept at least one
  paper-and-ink direction, and register differed fully in two of three final
  proposals at best.
- **Untested.** None of these was probed:
  - the exceptions other than an explicit calm request: minimal references,
    an established system's look, a named product reason;
  - the fallback when no strong reference fits;
  - the autonomous choice;
  - the closer adaptation after a choice;
  - the judge.
- **Reference previews landed in the project.** They went into
  `.design/refs/`, `.refs/`, `.playwright-mcp/` or dot-files at the project
  root. Previews captured with the browser's screenshot tool go to
  `.playwright-mcp/`, which `frontend-quality` names as that tool's output
  directory. Downloaded previews landed in the project because no run could
  write outside it, though the skill names a temp directory for them. The
  base runs did the same.
