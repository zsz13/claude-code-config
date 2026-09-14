---
name: adversarial-jury
description: Independent blind review of a change by risk-matched reviewer lenses, resolved on evidence. Use before completing non-trivial or high-risk work, or when you would otherwise be the only reviewer of your own change.
---

# Adversarial jury

Independent judges review a change blind, then evidence — not consensus —
decides. This exists to defeat anchoring, sycophancy, self-preference, and
confirmation bias, all of which get worse when the reviewer can see the
implementer's reasoning.

You (the parent) run this protocol. You do not participate as a judge.

## 1. Route by risk

Pick the smallest set that covers the actual risk surface. Adding an irrelevant
reviewer costs tokens and produces noise findings that dilute the real ones.

| Risk | Reviewers |
|---|---|
| **Trivial** — typo, comment, docs, obvious one-line internal fix | No jury. Run the relevant deterministic check. `/code-review` if you want a second pass. |
| **Normal** — ordinary feature or fix | `correctness-adversary`, `test-judge` |
| **Significant** — non-obvious logic, multiple call sites, shared code | `spec-judge`, `correctness-adversary`, `test-judge`; add `architecture-judge` if structure or contracts moved; `jury-arbiter` only if they conflict |
| **High-risk** | Up to all five, then `jury-arbiter` |

High-risk means: authentication, authorization, cryptography, payments or money
movement, database migrations, public API changes, infrastructure/IaC,
permissions, destructive or irreversible data operations, concurrency,
security-sensitive input handling, cross-service contracts.

Route by what the change touches, not by its size. A one-line change to an
authorization check is high-risk.

## 2. Produce deterministic evidence first

Run the checks that apply — build, tests, type check, lint, static analysis —
**before** dispatching judges, and put the results in the packet. Judges are
read-only and cannot run anything; they interpret evidence, they do not generate
it. Reviewing a change whose build is broken wastes a jury.

## 3. Dispatch blind, in parallel

Send every judge in one message so they run concurrently and cannot observe each
other. Each gets its own packet containing only:

- the original requirement or specification, verbatim;
- the diff, with its base clearly identified;
- the relevant code paths (paths, or a bounded excerpt — not the repository);
- the relevant tests;
- the deterministic verification output.

Withhold, for every judge:

- your reasoning, your plan, or why you think the change is correct;
- your confidence, and any framing like "this should be fine" or "just check";
- which alternative you or the user prefer, and who wrote what;
- any other judge's findings.

Preserve the actual requirement and its constraints — blindness hides *opinion*,
never the spec. In a comparative review, label alternatives neutrally (A/B).

Judges must not talk to each other during this stage. If you cannot give a judge
a fresh context, say so in the final report: independence was limited.

See `packet-template.md` for the packet format.

## 4. Resolve

Wait for every report before reconciling anything.

- If the panel is small and unanimous with concrete evidence, reconcile yourself.
- If they conflict materially, or the risk is high, dispatch `jury-arbiter` with
  all reports plus the deterministic evidence.

Never resolve by counting votes. Judges share training data and therefore share
blind spots, so agreement is correlated rather than independent. Rank evidence:
reproducible behavior > build > tests > types > static analysis > source
evidence > reviewer judgement.

Reject findings that lack a plausible failure path, even if several judges raise
them. Accept a single well-evidenced finding over a confident majority.

## 5. Act

Fix the accepted, in-scope defects. Do not let review findings become a
refactoring project. Rerun the deterministic checks the fix affects. Re-review
only the part that changed, and only if the fix itself is non-trivial.

Report: accepted findings with their evidence, what you actually verified, what
you skipped, and what remains unproven. "No supported findings" is a real
outcome — a clean jury is not proof of correctness, and neither is a green suite.
