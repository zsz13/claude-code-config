# Why this setup

The reasoning behind the non-obvious choices. If you only read one page before
adopting anything, read this one — most of these decisions are only defensible
once you know what they are trading away.

## The governing constraint

An AI coding agent has a fixed context window and a prompt cache. Every
always-loaded instruction is paid for in **every session**, competes with the
code you actually want it to read, and invalidates the cache when it changes.

So the design question is never "is this guidance good?" It is: **is this
guidance good enough to be worth what it costs in every session?** Most guidance
is not, and belongs one layer down — in a path-scoped rule, a skill, or a hook
that emits one line at the moment it matters.

That single constraint explains most of what follows.

---

## Why `Ponytail defaultMode = off`

Ponytail has two quite different faces:

- a **persona** that biases everything the session writes toward the minimal
  solution;
- a **one-shot review** that looks at a diff and reports what could be deleted.

Only the second one is wanted here.

A persistent minimalism persona is a bad default for maintenance work on
existing codebases, for three reasons:

1. **It is the wrong objective for most changes.** "Fewest lines" is a proxy for
   "simplest", and the proxy breaks exactly where it matters: a validity guard,
   an explicit null check the type checker needs, a response cap on an
   unauthenticated endpoint, a measured optimization. Real rejected findings of
   exactly these kinds are in [benchmarks.md](benchmarks.md#3-ponytail-review).
2. **It fights the architecture you already have.** An established codebase's
   conventions outrank a global aesthetic. A persona does not know which
   abstraction was deliberate.
3. **Its state is machine-global** (see below), so leaving it on is not a local
   decision.

Off by default costs one command (`/ponytail-review`) when the review is
actually wanted. Leaving it on costs a bias on every line written. `ultra` is
never enabled automatically under any circumstances.

## Why machine-global flag state is avoided

Ponytail's active mode lives in **one file, shared by every session on the
machine**. It is not session state. That has three consequences that are easy to
miss:

- **It crosses sessions.** Typing `/ponytail-review` in one terminal arms the
  flag for a session running in another terminal at the same time.
- **It crosses agent boundaries.** While the flag is set, the plugin's subagent
  hook injects the persona into subagents — including reviewers whose entire
  purpose is the opposite lens. This was reproduced directly: a `security-judge`
  subagent received the ponytail context.
- **It outlives failure.** A review that errors or is interrupted leaves the
  flag set. Nothing cleans it up on its own.

The general rule this produced: **prefer stateless mechanisms; where state is
unavoidable, assume it leaks and contain it in layers.** The dead-code audit was
then deliberately designed with *no* state at all — no mode file, no hook,
nothing machine-global, nothing to clean up. An interrupted run leaves an
unfinished report and nothing else.

Containment for the flag that does exist is three independent layers, described
in [security.md](security.md#the-ponytail-flag-leak). They are independent on
purpose: do not remove one on the assumption that another covers it.

## Why session isolation matters

Two sessions on one machine are two independent pieces of work. Shared mutable
state between them produces failures that are nearly impossible to attribute:

- the affected session shows no cause — the trigger happened somewhere else;
- the effect is a *bias*, not an error, so nothing fails loudly;
- it is timing-dependent, so it does not reproduce.

The same reasoning applies inside a session. The read-budget advisor keys its
state by **session id *and* agent id**, so a subagent's reads never count as the
parent's re-reads, and vice versa. A shared counter there would produce
mysterious "you already read this" hints for a file the parent never saw.

## Why no machine-global automatic review hook

The obvious implementation of "automatically review after implementing" is a
hook. It was considered and rejected:

- **A hook cannot tell whether the triggers fired.** "A new abstraction was
  introduced", "a relatively simple requirement caused a broad implementation",
  "similar logic already exists elsewhere" — these are semantic judgements about
  intent and about the rest of the codebase. A hook sees a tool call, not a
  reason. It would fire on every edit, and a guard that fires on everything gets
  disabled.
- **Hooks run on tool events, not at the end of a task.** There is no reliable
  "implementation is finished and validated" event. `Stop` fires when the model
  yields — including to ask a question mid-task.
- **A hook that invokes a review is machine-global**, and would therefore reach
  concurrent unrelated sessions. That is precisely the failure mode the whole
  setup is built to avoid.
- **Hooks that mutate shared state to communicate are worse than no hook.** The
  one place this setup accepts a machine-global hook is `ponytail-guard.sh` —
  and its only job is to *remove* state, never to create it.

So the triggers are **semantic rules the model evaluates**, and the hooks are
reserved for the two things a hook is genuinely good at: deterministic denial
(`block-destructive-iac.sh`, `block-git-no-verify.sh`) and cheap just-in-time
hints (the two advisors).

## Why instructions rather than hooks

The tradeoff is stated plainly because it is a real cost:

| | Hook | Instruction |
|---|---|---|
| Fires reliably | ✅ deterministic | ❌ model-dependent |
| Understands intent | ❌ sees tool calls | ✅ sees the whole task |
| Leaves evidence | ✅ visible in transcript | ❌ **only if the model says so** |
| Session-isolated | ❌ machine-global config | ✅ nothing shared |
| Can be wrong about *when* | ✅ frequently | ❌ less often, but silently |

For a *semantic* trigger, the instruction wins on two of the three axes that
matter and loses badly on one: **evidence**. That loss is what the reporting
requirement exists to repair.

## Why visible reporting of automatic reviews is required

This is the load-bearing rule of the whole arrangement.

Nothing executes the dead-code audit or the Ponytail review. There is no flag,
no statusline badge, no banner, no marker. Invoking a skill directly even
bypasses the plugin's own prompt hook. Therefore:

> A review that ran and found little is **indistinguishable in the transcript
> from one that never ran at all.**

The report is the only evidence there is. So every automatic review must state:
that it ran, named; each finding with file and line; which findings were
applied; **which were rejected and why**; and that validation was re-run, with
its result.

The rejection reasons matter most. A rejection is a decision — either it
conflicts with something higher in the priority ladder, or the cost of the cut
exceeds the lines it saves. Recording the reason is what stops the next session
re-litigating it, and what lets a human check whether the ladder was applied
honestly.

And when the triggers are *not* met, one line saying so, naming the reason:
*"No dead-code audit: additive change, nothing orphaned."* That is a fact a
reader can check. Silence is not.

This is an honesty mechanism, not a bureaucratic one. It converts an unverifiable
claim ("I reviewed it") into a checkable one.

## Why the trigger rules live in a directory-scoped `CLAUDE.md`

There were four candidate homes:

| Option | Why not |
|---|---|
| Global `~/.claude/CLAUDE.md` | These rules are about one installed plugin and one set of projects. Universal policy should be universal; this would be paid for in every session everywhere. |
| Each project's `CLAUDE.md` | Four copies of the same text, drifting apart. |
| A skill | Skills load on invocation — a trigger rule must be present *before* the model decides whether to invoke anything. |
| **A `CLAUDE.md` at the root of the code directory** | ✅ Loads for everything beneath it via parent-directory loading, duplicates nothing, leaves the global file and every project file untouched. |

The last one also keeps the blast radius honest: the rules apply to work in that
directory and nowhere else.

## Why there is no third router

Three things could plausibly route work: the workflow layer (Superpowers), the
review layer (`adversarial-jury`), and the main model as orchestrator. A fourth
component that also wants to route — an "engineering orchestrator" skill, a
plugin whose agents say "use PROACTIVELY" — does not slot in underneath. It
competes, and the model picks between two routers instead of doing the work.

So: **Superpowers owns workflow routing. `adversarial-jury` owns reviewer
routing. The main model is the only orchestrator.** Anything that wants to be a
router is either not installed, or has its routing stripped.

## Why code intelligence is not stacked

A knowledge graph, an LSP, and text search answer different questions:

- **graph** — architecture, dependencies, call and data flow, change impact;
- **LSP** — exact symbols, definitions, references, diagnostics;
- **search** — a known string.

Running two graph systems on the same question costs twice and answers once. The
discovery ladder is: graph → symbol lookup → targeted search → targeted reads →
whole files → traversal, and you **stop at the first tier that lets you
implement correctly**.

The graph is built lazily, by a hook, once, only for repositories big enough to
justify it, and only when a broad search is about to happen anyway — because
building it eagerly would tax every session for a benefit most sessions do not
need.

## Why the evidence ladder is written down

> reproducible runtime behavior > compiler/build > tests > type checker >
> static/security analysis > lint > concrete source evidence > LLM opinion

Without an explicit ladder, a confident reviewer argument beats a boring test
result, because the argument is more persuasive prose. The ladder makes that a
rule violation rather than a judgement call, and it is what
[`jury-arbiter`](../agents/jury-arbiter.md) applies when reviewers disagree.

Its corollaries are deliberately uncomfortable: **agreement among reviewers is
not proof**, and **neither is a passing test suite**.

## Why the judges are blind and parallel

A reviewer who can see the implementer's reasoning is a worse reviewer:
anchoring, sycophancy and self-preference all get stronger with context about
what the author believed. So each judge gets the requirement, the diff, the
relevant code and tests, and the deterministic results — and nothing about what
anyone thinks.

They are dispatched in one message so they run concurrently and cannot observe
each other. They are resolved by evidence, never by counting: judges share
training data, so their agreement is *correlated*, not independent
confirmation.

Cost is controlled by routing. Trivial changes get no jury at all. The panel
should be the smallest set that covers the real risk surface, because an
irrelevant reviewer produces noise findings that dilute the real ones.

## Why "never bypass a failing hook"

`git commit --no-verify` is the single most tempting action in an agent's
repertoire: it turns a red gate green instantly. It is also the action most
likely to ship a defect.

The policy — a failing hook gets investigated and fixed; bypassing is a
user-only action — is enforced deterministically by
[`block-git-no-verify`](../hooks/block-git-no-verify.py), which parses the
command with `shlex` so `-n` inside a quoted commit message is not mistaken for
a flag. If the hook itself is broken, the agent says so and the human runs the
bypass.

Same reasoning for [`block-destructive-iac.sh`](../hooks/block-destructive-iac.sh):
`terraform apply` and `destroy` mutate real infrastructure, and no amount of
good judgement makes an agent-initiated `destroy` acceptable. Read-only
Terraform operations are never blocked.

Both guards name themselves and say how to disable them in the denial message. A
guard the user cannot understand or remove is a trap.

## Why every advisory hook fails open

The two guards deny on a positive match. Everything else — both advisors, the
graph bootstrap, the ponytail guard — exits 0 and emits nothing on any error,
timeout, or parse failure.

A hint is worth a few tokens. A hook that breaks the session because a payload
did not parse is worth negative infinity. The advisors also have a cheap shell
`case` fast path before the Python classifier runs, so the common path costs
almost nothing.

## What this setup deliberately does not do

- It does not ship a house style, a palette, or a UI aesthetic. The design layer
  defines process and a quality floor; aesthetic authority is user direction >
  the project's existing design system > the project's own design brief.
  Below all three sits one default, the owner's taste: where the request
  leaves the visual register open, directions lean expressive but controlled
  (`design-brief` step 2). It asks for qualities (a focal point, layered
  composition, real motion) and rules out defaults (a flat grey dashboard, a
  dark console), but names no palette, typeface or layout, and a request, a
  system or a brief overrides it.
- It does not pin tool or language versions in global config. Versions are
  chosen at project creation or at a deliberate upgrade, by checking what is
  current *then*.
- It does not install a second security reviewer. `security-judge` owns that
  lens; a competing one dilutes it.
- It does not modernize a working repository as a side effect of an unrelated
  task. Poetry, mypy, npm and Biome that work are not gaps.
