# The review pipeline

Every quality mechanism in this repository is a stage in one ordered pipeline.
The order is not decorative: each stage exists to stop the next one from wasting
effort, and reordering them produces measurably worse work.

```
implement
   ↓
validate (tests, types, lint, build — the repository's own gates)
   ↓
dead-code audit          ← only when its triggers fire
   ↓
Ponytail review          ← only when its triggers fire
   ↓
apply simplifications
   ↓
re-validate
   ↓
adversarial jury         ← non-trivial or high-risk changes
   ↓
report
```

## Why this order

**Validation before any review.** Judges and reviewers are read-only; they
interpret evidence, they do not produce it. Reviewing a change whose build is
broken burns a review on a question the compiler already answered. The evidence
ladder that governs the whole setup —

> reproducible runtime behavior > compiler/build > tests > type checker >
> static/security analysis > lint > concrete source evidence > LLM opinion

— means the cheap deterministic stages run first, always.

**Dead code before simplification.** A dead-code audit may delete a whole
module. Running the complexity reviewer first would spend a review simplifying
code that is about to disappear.

**Simplification before the jury.** The jury should review the diff that will
actually ship, deletions included. Sending the jury a pre-simplification diff
means re-reviewing after every cut.

**Re-validation before the jury.** A simplification is a code change. It gets
the same gates as any other code change.

## What each stage is, and is not

| Stage | Question it answers | Authority |
|---|---|---|
| **Tests / types / lint / build** | Does it work? | Blocking. Nothing ships past a failing gate. |
| **Dead-code audit** | What did this change orphan? | Advisory. Removes only *proven dead* code; everything else is reported. |
| **Ponytail review** | Is this more complex than the requirement justifies? | Advisory. Lowest rung of the priority ladder. |
| **Adversarial jury** | Is it correct, specified, tested, structurally sound, secure? | Advisory findings, resolved on evidence — never on vote count. |

These are complementary lenses, not redundant ones. A green test suite is not a
caller census (dead code). A clean jury is not proof of correctness. An empty
`rg` is not proof of death. Each stage is explicitly told what its own evidence
cannot prove.

## Priority ladder

When two stages disagree, this order decides:

1. User requirements
2. Correctness and safety
3. Security and data integrity
4. Existing architecture and project conventions
5. Tests / type checks / linting
6. Maintainability
7. Ponytail simplification

Deleting proven-dead code is maintainability (6). A "likely dead" finding is
advisory and outranks nothing. The complexity reviewer sits at the bottom on
purpose: it is the stage most likely to be wrong in a way that costs something.

---

## Stage 1 — Dead-code audit

Skill: [`skills/dead-code-audit`](../skills/dead-code-audit/SKILL.md).

**Runs automatically when** the finished change did at least one of:

- removed or replaced a feature, endpoint, page, screen, or integration;
- moved, renamed, or re-homed code across modules or files;
- completed a migration to another library, API, or pattern while the old path
  is still in the tree;
- retired a feature flag, or finished a rollout;
- consolidated duplicated implementations onto one path;
- dropped a field, table, or entity in a schema or model change;
- removed or bypassed the last call site of an existing helper;
- dropped or replaced a dependency.

**Does not run for** small edits, bug fixes, copy, docs, formatting, dependency
bumps, purely additive changes, or mid-refactor — code in flight is *supposed*
to be temporarily unreferenced.

**Scope** is the blast radius of the change, never the whole repository. A
whole-repo sweep only happens when asked for.

**Removal authority** is deliberately narrow. Only *proven dead* code is
removed, and only when the repository's gates stay green afterwards. Everything
else is reported and left in place. An empty grep is never sufficient evidence:
registries, string dispatch, framework discovery, config, SQL, templates, CI and
external clients are all invisible to static search. Migrations, public API
surface, CLI entry points, framework-discovered files, fixtures and
registration imports are never removed on the audit's own authority.

## Stage 2 — Ponytail review

Plugin: [ponytail](https://github.com/DietrichGebert/ponytail) (MIT), invoked as
`/ponytail-review`.

**Runs automatically when** the implementation did at least one of:

- introduced a new abstraction, service, helper, wrapper, adapter, or provider;
- added a new dependency;
- duplicated logic that appears to already exist elsewhere;
- answered a relatively simple requirement with a broad or multi-file change;
- introduced substantial duplication;
- came out materially larger or more complex than the requirement justifies.

**Never runs automatically for** security, auth/authorization, trust boundaries,
validation, data integrity, database migrations, transactions, concurrency,
infrastructure, deployment, public APIs and compatibility guarantees, or where
an abstraction is clearly justified by the existing architecture. A
simplification persona is exactly the wrong lens for those, and "fewer lines"
is exactly the wrong objective.

`ultra` intensity is never enabled automatically.

## Stage 3 — Adversarial jury

Skill: [`skills/adversarial-jury`](../skills/adversarial-jury/SKILL.md).
Reviewer definitions: [`agents/`](../agents/).

Independent judges review the change **blind** — each in its own context, in
parallel, without the implementer's reasoning, confidence, preferences, or any
other judge's findings — and then evidence, not consensus, decides.

Routing by risk:

| Risk | Reviewers |
|---|---|
| Trivial | No jury. Run the deterministic check. |
| Normal | `correctness-adversary`, `test-judge` |
| Significant | `spec-judge`, `correctness-adversary`, `test-judge`; `architecture-judge` if structure or contracts moved; `jury-arbiter` only on conflict |
| High-risk | Up to all five, then `jury-arbiter` |

High-risk is decided by what the change *touches*, not by its size: auth,
crypto, payments, migrations, public APIs, IaC, permissions, destructive data
operations, concurrency, cross-service contracts. A one-line change to an
authorization check is high-risk.

**Never resolve by vote count.** Judges share training data, so their agreement
is correlated rather than independent — three reviewers repeating an unsupported
claim do not make it supported, and one reviewer with a reproducible
counterexample outweighs four dissenting opinions.

---

## How the four review mechanisms differ

| | What it is | Scope | When | Persistent? |
|---|---|---|---|---|
| **Ponytail persona mode** | A coding *persona* that biases all output toward the minimal solution | Everything the session writes | Only when a human sets `lite`/`full`/`ultra` deliberately | Yes — machine-global flag. Off by default here. |
| **Ponytail review** | A one-shot review pass that only hunts over-engineering | One diff | Triggered per change (see Stage 2) | No — flag cleared after |
| **Dead-code audit** | A reachability audit with an explicit confidence classification | Blast radius of one change | Triggered per change (see Stage 1) | No — stateless by design |
| **Adversarial jury** | Blind multi-lens review resolved on evidence | One diff, risk-routed | Non-trivial / high-risk changes | No |
| **Tests / static validation** | Deterministic proof of behavior | Whatever the suite covers | Always | n/a |
| **Superpowers** | Process skills — brainstorming, TDD, systematic debugging, plan execution | The approach itself, before implementation | Whenever a matching process applies | n/a |

Superpowers sits *before* implementation; the other four sit after it. They do
not compete: Superpowers owns workflow routing, `adversarial-jury` owns reviewer
routing, and there is deliberately no third router — see
[docs/why-this-setup.md](../docs/why-this-setup.md).

## Reporting is mandatory

Nothing on the machine executes the dead-code audit or the Ponytail review.
There is no hook, no flag, no status badge, no marker in the transcript. A
review that ran and found little is therefore **indistinguishable from one that
never ran at all** — unless the agent says so.

So every automatic review must state, in the transcript:

- that it ran, named;
- each finding, with file and line;
- which findings were applied;
- which were rejected, **and why** — a rejection is a decision and needs its
  reason (it conflicts with something higher in the priority ladder, or the cost
  of the cut exceeds the lines it saves);
- that the relevant validation was re-run afterwards, and its result.

And when the triggers are **not** met, one line saying so and naming the reason:
*"No dead-code audit: additive change, nothing orphaned."* That is a fact a
reader can check. Silence is not.

This is the whole enforcement mechanism. See
[docs/why-this-setup.md](../docs/why-this-setup.md#why-instructions-rather-than-hooks)
for why it is not a hook.
