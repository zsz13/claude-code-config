# Review packet template

One packet per judge. Fill every section; write "none" rather than omitting a
heading. Keep it bounded — paths and excerpts, never a repository dump. Strip
secrets, tokens, and credentials from diffs, logs, and config before sending.

```
## Requirement
<the original requirement/spec, verbatim, plus acceptance criteria. No commentary.>

## Change under review
Base: <sha or ref>    Head: <sha or ref>
Changed files: <complete `git diff --name-status BASE..HEAD` manifest>
<the diff, or a bounded excerpt of it — split by file/subsystem when large; never omit a changed file>

## Relevant code
<paths, and excerpts only where the diff is not self-contained>

## Tests
<relevant test files/paths, and the tests that cover this change>

## Deterministic results
Build:      <pass/fail + exact output or failure lines>
Tests:      <counts, names of failures, exact output>
Types:      <pass/fail + errors>
Lint/static:<pass/fail + findings>
Not run:    <checks skipped, and why>

## Your task
<the single lens question for this judge — nothing about the other judges>
```

## What must never enter a packet

- Your plan, your reasoning, or why you believe the change is correct.
- Your confidence, or softeners: "this should be fine", "just a sanity check",
  "I already verified this".
- Which option you or the user prefer; who authored which alternative.
- Another judge's report, or the fact that another judge found nothing.
- Prior review rounds' conclusions — for a re-review, send the new diff and the
  specific finding being retested, not the debate that produced it.

## Comparative reviews

Label alternatives `A` and `B`. Randomize which is which. Do not indicate origin,
authorship, recency, or preference. Position bias is real: if you can, vary the
order across judges.
