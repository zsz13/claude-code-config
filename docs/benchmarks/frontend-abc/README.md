# Frontend research trigger: three-way build

Evidence for [benchmarks §8](../../benchmarks.md#8-frontend-research-trigger-and-three-way-build),
which states the conclusions and their evidence classes. This page describes the
setup and indexes the files.

## Setup

Run on 2026-09-29 and 2026-09-30 with Claude Code 2.1.285 on `claude-opus-5-5`
(1M context), headless (`claude -p`, `--permission-mode auto`, stream-json
output), with the owner's full global configuration loaded.

Each build started from the same scaffold: Next.js 16.3.7, React 19.2.8,
TypeScript and Tailwind CSS v4 from `create-next-app`. Each had the same 12-car
dataset and the same 20 Wikimedia Commons photos ([credits](CREDITS.md)). Each
was built in its own sibling directory, told not to look at the others, and no
build was changed after the comparison started.

| Build | Port | Prompt | 21st connected | 21st calls |
|---|---|---|---|---|
| legacy-auto | 3103 | [An ordinary request](prompts/build-legacy-auto.md): the product and its features, "production-quality and visually appealing". 21st neither requested nor forbidden, configuration as it was before the fix | yes (23 tools\*) | 0 |
| control | 3101 | [A detailed design brief](prompts/build-control.md) with an explicit avoid-list, 21st forbidden | no | 0 |
| 21st | 3102 | [The same brief](prompts/build-21st.md), plus: use 21st heavily and log every call | yes (23 tools\*) | 40 |

\* The server offered 34 tools; 11 of them were denied, which left 23.

The control and 21st prompts differ only in the working directory and port, the
"This side" section, and one line of the definition of done (the 21st build
also points at its call log). Every 21st call, with what it influenced, is in
the build's own [call log](21st-call-log.md).

## Boards

Each board puts the three builds side by side, in the order legacy-auto,
control, 21st, at the same viewport and state. A panel reading "NOT PRESENT ON
THIS SITE" means the state could not be reached: legacy-auto has no mobile menu.
The small round "N" is the Next.js dev indicator.

| Board | What it shows |
|---|---|
| [desktop-1440-first-viewport](boards/desktop-1440-first-viewport.jpg) | First viewport at 1440 × 900 |
| [laptop-1280-first-viewport](boards/laptop-1280-first-viewport.jpg) | First viewport at 1280 × 800 |
| [desktop-1440-inventory](boards/desktop-1440-inventory.jpg) | The inventory section, scrolled into view |
| [desktop-1440-filter-applied](boards/desktop-1440-filter-applied.jpg) | Inventory with one filter applied |
| [desktop-1440-details](boards/desktop-1440-details.jpg) | Vehicle detail view opened from a card |
| [mobile-390-first-viewport](boards/mobile-390-first-viewport.jpg) | First viewport at 390 × 844 |
| [mobile-390-menu](boards/mobile-390-menu.jpg) | Mobile navigation opened |
| [mobile-390-filter-sheet](boards/mobile-390-filter-sheet.jpg) | Mobile filter UI opened |
| [page-composition-1440-scroll](boards/page-composition-1440-scroll.jpg) | Consecutive 1440 × 900 frames scrolling down each page, reduced |

## Files

| File | Contents |
|---|---|
| [tool-counts.json](tool-counts.json) | Tool calls per build (21st by tool, ToolSearch, Playwright, skills, subagents, cost) and per tool-selection probe |
| [render-checks.json](render-checks.json) | Page height, horizontal overflow, console messages and broken images at 1440, 1280 and 390; pass or fail for each scripted interaction |
| [judge-report.md](judge-report.md) | The blind judge's prompt, the label mapping, and its report verbatim |
| [21st-call-log.md](21st-call-log.md) | The 21st build's log of all 40 calls |
| [composition-protocol.md](composition-protocol.md) | The composition plan test's protocol, fixed before the runs, and its scored result |
| [composition-plans.md](composition-plans.md) | The ten plans in full, each with the skills it invoked and its 21st calls |
| [followup-protocol.md](followup-protocol.md) | The follow-up probes (planning, trivial work, established systems, no research tool): both rounds' protocols, the amendment, and both results |
| [followup-probes.json](followup-probes.json) | Per-run counts for both follow-up rounds; round 2 ran the final skill text |
| [followup-fallback-plans.md](followup-fallback-plans.md) | The six round-2 replies from runs with no research tool, which the fallback scoring rests on |
| [prompts/](prompts/) | The three build prompts and the composition-plan prompt; `followup/` holds the follow-up probe prompts |
| [CREDITS.md](CREDITS.md) | Photo authors and licences |

Three things are not published:
- the build transcripts (stream-json, 27 to 41 MB each);
- the follow-up probe transcripts, which the owner keeps;
- the full-resolution screenshots.

The original tool-selection probes' transcripts (before the follow-up) were
kept in a session scratch directory that has since been cleared. For those
probes, `tool-counts.json` holds the counts recorded when each probe was counted.
The two installed substantial probes among them were stopped after their 21st calls, so that the composition test
could run with no other headless session; their totals are therefore partial.

## Reproduce

The builds are not deterministic, so a rerun reproduces the method, not the
pages.

1. Scaffold three sibling Next.js projects with the stack above, and copy the
   same data and photos into each.
2. For the tool-selection question, connect 21st at user scope (the setup row in
   [alternatives](../../alternatives.md#chosen-reference-and-component-mcps-without-their-skills)),
   run the substantial and trivial prompts from `tool-counts.json` with
   `claude -p ... --output-format stream-json --verbose`, and count
   `mcp__21st__*` tool calls.
3. For the builds, run each prompt in its own directory, serve each on its port,
   capture the same viewports and states from each, and judge them blind.
