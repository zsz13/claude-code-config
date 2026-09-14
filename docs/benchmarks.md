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

## 6. Claims made with no measurement at all

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
