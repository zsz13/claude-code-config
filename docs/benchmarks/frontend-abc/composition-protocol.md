# Composition paragraph: plan-level before/after test

Fixed before any run.

**Question.** Does the `design-brief` paragraph "Compose the page, do not stack
it" change how an ordinary frontend request gets planned?

**Arms.** Five fresh headless Claude Code sessions per arm, same model and global
configuration. The only difference is `~/.claude/skills/design-brief/SKILL.md`:

- `before`: the new version with only the composition paragraph removed;
- `after`: the version with the composition paragraph.

`frontend-quality` is the new version in both arms. The live file is swapped for
the `before` arm only while its runs execute, with no other headless session
running, and restored immediately after.

**Prompt.** The legacy-auto build prompt's request, plus a planning-only
instruction (see [prompts/composition-plan.md](prompts/composition-plan.md)). Writes are disallowed.

**Scored per run.**

1. `sections`: homepage sections between the header and the footer.
2. `stack`: yes when the plan is a hero plus the inventory grid, with at most
   generic bands (newsletter, CTA, stats, testimonials, trust badges) and no
   other section with a composition of its own.
3. `mobile_nav`: yes when the plan names a mobile menu or equivalent.
4. `design_brief_invoked`: whether the session invoked `design-brief` at all.
   A run that did not is uninformative for this test.

Scored by one person (the one who made the change), from the plan text.

## Result

Added after the runs; everything above is unchanged.

| Scored | before | after |
|---|---|---|
| `design_brief_invoked` | 0/5 | 0/5 |
| `sections` | 8, 7, 8, 7, 8 | 8, 7, 7, 7, 8 |
| `stack` | 0/5 | 0/5 |
| `mobile_nav` | 5/5 | 5/5 |

No run invoked `design-brief` or any other skill, so the paragraph never entered
context in either arm, and by point 4 all ten runs are uninformative. The plans
are in [composition-plans.md](composition-plans.md).
