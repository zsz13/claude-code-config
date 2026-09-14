# Directory instructions — ~/github

Applies to every project under this directory. A repository's own `CLAUDE.md`
wins over anything here, and the engineering principles in `~/.claude/CLAUDE.md`
still apply.

## Ponytail

Ponytail is an optional complexity reviewer and must never override existing
project instructions, project conventions, security rules, tests, architecture
rules, or other agents and reviewers.

### When to review automatically

After implementing and initially validating a change, automatically run
`/ponytail-review` only when at least one of these is true:

- a new abstraction, service, helper, wrapper, adapter, provider, or similar layer was introduced;
- a new dependency was added;
- similar logic appears to already exist elsewhere;
- a relatively simple requirement caused a broad or multi-file implementation;
- substantial duplication was introduced;
- the implementation appears materially larger or more complex than the requirement justifies.

When reviewing, prefer deleting unnecessary code, reusing existing project
functionality, stdlib/native capabilities, and simplifying the implementation
while preserving good architecture.

### When not to

Do NOT automatically invoke Ponytail simplification for security/auth/authorization,
trust boundaries, validation, data integrity, database migrations, transactions,
concurrency, infrastructure, deployment, public APIs/contracts, compatibility
guarantees, or cases where an abstraction is clearly justified by the existing
architecture.

### Priority order

1. User requirements
2. Correctness and safety
3. Security and data integrity
4. Existing architecture and project conventions
5. Tests/type checks/linting
6. Maintainability
7. Ponytail simplification

Never enable `ultra` automatically. Do not sacrifice correctness, extensibility
that is already required, security, testability, readability, or established
architecture merely to minimize LOC.

### Workflow for applicable tasks

implement normally → validate/tests → dead-code audit when its own triggers
fire → Ponytail review → apply only clearly beneficial simplifications → rerun
relevant validation/tests → continue with normal reviewers.

Ponytail review is a quality gate, not an authority. Reject its suggestions when
they conflict with stronger requirements.

### Say that it ran (required)

The review is an instruction, not a hook: nothing executes it and nothing marks
it. With `defaultMode` at `off` there is no flag, no statusline badge and no
banner, and invoking the skill rather than typing the command bypasses the
plugin's prompt hook entirely — so a review that ran and found little is
indistinguishable in the transcript from one that never ran at all. Reporting is
the only evidence there is.

So whenever the automatic review runs, state in the transcript:

- that a **Ponytail review** ran, named as such;
- each finding, with its file and line;
- which findings were applied;
- which were rejected, and why — a rejection is a decision and needs its reason
  (it conflicts with something higher in the priority order, or the cost of the
  cut exceeds the lines it saves);
- that the relevant validation was rerun afterwards, and its result.

When the trigger conditions are **not** met, say so in one line and name the
reason, rather than staying silent. "No Ponytail review: no new abstraction,
dependency or duplication" is a fact a reader can check; silence is not.

### State hygiene (required)

Ponytail's active mode lives in `~/.claude/.ponytail-active` — a single
machine-global file shared by every concurrent session, not session state.
`/ponytail-review` writes `review` into it, and while it is set the plugin
injects the ponytail persona into unrelated subagents (adversarial-jury judges,
read-only Explore agents) in this session and in any other session running at
the same time.

- The default mode stays `off` in `~/.config/ponytail/config.json`. Never change
  the default, and never run `/ponytail default <mode>`.
- Wrap every automatic review so cleanup happens even on failure or interruption:
  1. before — `~/.claude/hooks/ponytail-guard.sh status`
  2. run the review
  3. after — `~/.claude/hooks/ponytail-guard.sh clear`, run even when the review
     failed, errored, or was interrupted, and before moving on to other work.
- Invoking the `ponytail-review` skill directly does not arm the flag (only a
  typed `/ponytail-review` prompt does). Verify with `status` regardless rather
  than assuming which path ran.
- Cleanup is also enforced outside the model, so an interrupted review cannot
  leave state behind: `Stop` and `SessionEnd` hooks run the guard, and the
  plugin's own `SessionStart` hook clears the flag whenever a session starts
  with the default `off`. The guard removes only a `review` flag; a level a
  human set deliberately (`lite`/`full`/`ultra`) is left alone.
- Subagents are protected structurally by `PONYTAIL_SUBAGENT_MATCHER` in
  `~/.claude/settings.json`, a never-matching sentinel that stops the ruleset
  reaching any subagent regardless of flag state. Do not remove it.
- Never end a session with the flag set. `~/.claude/hooks/ponytail-guard.sh force`
  clears it unconditionally.

## Dead-code audit

Reusable audit logic lives in the global `dead-code-audit` skill
(`~/.claude/skills/dead-code-audit/SKILL.md`); the model invokes it, or the user
types `/dead-code-audit`. Like Ponytail it is advisory and must never override
project instructions, project conventions, security rules, tests, architecture
rules, or other agents and reviewers. Nothing executes it: these rules are the
only trigger, and the report is the only evidence it ran.

### When to audit automatically

After implementing and validating a change, run the audit when at least one of
these is true:

- a feature, endpoint, page, screen, or integration was removed or replaced;
- a refactor moved, renamed, or re-homed code across modules or files;
- a migration to another library, API, or pattern completed and the old path is
  still in the tree;
- a feature flag was retired, or a rollout finished;
- duplicated implementations were consolidated onto one path;
- a schema or model change dropped a field, table, or entity;
- the change removed or bypassed the last call site of an existing helper;
- a dependency was dropped or replaced.

Scope is the blast radius of the change, not the repository. A whole-repo sweep
happens only when asked for one.

### When not to

- Small edits, bug fixes, copy, docs, formatting, dependency bumps, and purely
  additive changes.
- Mid-refactor. Code in flight is *supposed* to be temporarily unreferenced;
  audit once the refactor is complete and its gates are green.
- As a substitute for the change's own validation. The audit runs after tests
  pass, never instead of them.

Auditing is not deleting. The audit may report findings that sit in migrations,
public API surface, auth, or framework-discovered code; it never removes those
on its own authority (see the never-remove classes in the skill).

### Removal authority

Only **proven dead** candidates are removed, and only when the repository's own
gates stay green afterwards. Everything else is reported and left in place. An
empty grep is never sufficient evidence. When in doubt, retain and report.

### Priority order

The same ladder as Ponytail's. Removing proven-dead code is maintainability
(6); a likely-dead finding is advisory and outranks nothing. Correctness,
security, data integrity, existing architecture, and the test/type/lint gates
all win.

### Order with Ponytail and adversarial-jury

```
implement -> validate/tests -> dead-code audit -> Ponytail review ->
apply simplifications -> rerun validation -> adversarial-jury (non-trivial/high-risk)
```

Dead code goes first so Ponytail does not spend a review simplifying code that
is about to be deleted, and so the jury reviews the final diff with the
deletions in it. A deletion that is itself non-trivial — shared code, public
surface, more than a couple of files — goes to the jury like any other change.

### Say that it ran (required)

Whenever the automatic audit runs, emit the report from the skill's §7 in the
transcript: scope and tools, what was removed with file/line and the evidence,
what was retained and the reason, and the validation command and its result.
Empty sections stay, marked "none".

When the trigger conditions are **not** met, say so in one line and name the
reason — "No dead-code audit: additive change, nothing orphaned" — rather than
staying silent.

### No flag, no hook (by design)

The audit is stateless: no mode file, no `SessionStart`/`Stop` hook, nothing
machine-global, nothing that runs per tool call. There is nothing to leak
between concurrent sessions and nothing to clean up. An interrupted run leaves
only an unfinished report, and any uncommitted deletion is visible in
`git status`.
