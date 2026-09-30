# Alternatives considered

What else was on the table for each layer, and why it was not chosen. Several of
these are good tools that were rejected for fit, not quality — that distinction
is kept explicit, because "we didn't pick it" is often read as "it's bad".

---

## Review orchestration

### Chosen: `adversarial-jury` — blind, parallel, risk-routed, evidence-resolved

| Alternative | Why not |
|---|---|
| **Self-review** (the model reviews its own diff) | It is the failure mode the jury exists to defeat. The reviewer has already committed to an interpretation, and re-reading your own work with the reasoning still in context mostly confirms it. |
| **A single "code reviewer" agent** | One lens, one set of blind spots, and no mechanism to decide what to do when it is wrong. Cheaper, and noticeably weaker on anything non-trivial. |
| **Sequential review** (each reviewer sees the last one's findings) | Cheaper on tokens and strictly worse: reviewer *n* anchors on reviewer *n−1*. Parallel dispatch in a single message is what makes the reports independent. |
| **Majority vote across reviewers** | Judges share training data, so agreement is correlated rather than independent. Three reviewers repeating an unsupported claim do not make it supported. `jury-arbiter` ranks evidence instead. |
| **Always run all five judges** | Token cost with no benefit on small changes, plus noise findings from irrelevant lenses that dilute the real ones. Hence risk routing. |
| **Off-the-shelf reviewer agent packs** | Their agents duplicate the built-ins and each other (one pack had `code-reviewer`, `debugger` and `test-automator` all overlapping existing capability), and several ship a second security reviewer, which dilutes the one that owns that lens. |

### Chosen: `jury-arbiter` only on conflict or high risk

The alternative — always arbitrate — costs an extra top-model pass to
rubber-stamp a unanimous, well-evidenced panel. The parent reconciles when the
panel is small and agrees with concrete evidence.

---

## Complexity review

### Chosen: Ponytail, review mode only, off by default

| Alternative | Why not |
|---|---|
| **Ponytail as a persistent persona** (`lite`/`full`/`ultra` as default) | Biases everything toward fewest lines, which is the wrong objective for maintenance work and actively dangerous around guards, validation and security bounds. Real examples of what it would have removed are in [benchmarks.md](benchmarks.md#3-ponytail-review). |
| **No complexity review at all** | Agents over-build: speculative abstractions, wrappers with one caller, dependencies for things the standard library does. Something has to ask the question. |
| **Build a custom simplification skill instead** | The existing plugin is MIT, maintained, has a published benchmark and a review mode that already does exactly this. Writing another one would be the same over-engineering it exists to catch. |
| **Give the review authority to act** | It would have removed a measured 3× optimization, a security bound on an unauthenticated response, and a public API field. Advisory, at the bottom of the priority ladder, is the correct authority level. |
| **`ponytail-audit` (whole-repo) on a schedule** | Different job. The per-change review is scoped to a diff; a repo-wide over-engineering sweep is a deliberate, explicitly requested activity. |

---

## Dead code

### Chosen: a skill with a confidence classification and narrow removal authority

| Alternative | Why not |
|---|---|
| **`knip` / `vulture` / `deptry` as the decision-maker** | They are excellent *candidate generators* and confidently wrong about exactly the classes that matter: string-keyed registries, framework-discovered files, packaging entry points, reflection. The skill uses them — as candidates, never verdicts. |
| **`tsc --noUnusedLocals` / `ruff F401` as proof** | File-scoped and import-scoped respectively. Neither knows who imports the module. |
| **"Delete it and see if the tests pass"** | A suite is not a caller census. Fine inside one process with full coverage; never across a network, a client, or another repository — that experiment runs in production. |
| **Adding a dead-code tool as a project dependency** | Needs the same justification as any dependency. An ephemeral `uvx` / `pnpm dlx` run adds nothing to the lockfile. |
| **A repo-wide sweep on every change** | Expensive and noisy. Scope is the blast radius of the change; a full sweep is a separate, explicitly requested job. |
| **Automatic removal of everything found** | The asymmetry decides it: an unremoved dead symbol costs one line of report; a removed live one costs an outage. |

---

## Context efficiency

### Chosen: `run-captured` + two advisory hooks + a playbook skill

| Alternative | Why not |
|---|---|
| **Rewrite tool output in a PostToolUse hook** | The harness does not let a hook rewrite a tool result. Savings have to come from the model choosing a narrower command or read — which is why the hooks are *advisors*, not filters. |
| **`\| head` / `\| tail` on everything** | Silently hides failures and search matches. The helper exists specifically so that compactness never costs diagnosability: full output stays on disk, failures are never over-compressed, every failing test name survives. |
| **Rely on the harness's own ~30k-character spill-to-file** | It already helps, and is the reason the measured byte savings overstate the token savings. But it is a blunt truncation with a preview; it does not surface *distinct* error lines with line numbers, or guarantee the tail of a failure. |
| **A wrapper that also changes the command** (adds `-q`, `--tb=short`) | Changing a command's semantics behind the user's back makes failures unreproducible. The helper runs the command exactly as given. |
| **Blocking large commands outright** | Punishes legitimate cases and teaches nothing. Hints fire once per session per class. |
| **A persistent MCP server for search/indexing** | A CLI that gives the same deterministic answer costs no always-on routing context. Prefer the CLI when both work. |

---

## Code intelligence

### Chosen: one knowledge graph, lazily built, plus LSP

| Alternative | Why not |
|---|---|
| **Stacking multiple graph/semantic-search systems** | They answer the same question at multiple costs. Use a second one only when the first is insufficient or offers a distinct capability. |
| **Eagerly indexing every repository** | Taxes every session for a benefit most sessions do not need. The bootstrap hook fires only on a broad search, only in a git repo, only above a size threshold, and caches its decision. |
| **The graph tool's own `install` command** | It rewrites `CLAUDE.md` and installs a hook that blocks raw reads. A skill plus explicit routing gives the same navigation benefit without another component editing global config or vetoing reads. |
| **Repomix as the default navigation tool** | It is a packaging utility for handing code to an external model, not a way to navigate a repository. Packing a repo to answer a question about three functions is the opposite of the discovery ladder. |
| **Committing graph artifacts** | The bootstrap keeps tracked files untouched: the merge-driver line goes in `.git/info/attributes` and the output directory in `.git/info/exclude`, not `.gitattributes`/`.gitignore`. Nobody else's repository state changes because you ran a hook. |

---

## Frontend and design

### Chosen: process skills (`design-brief`, `frontend-quality`) + real browser verification

| Alternative | Why not |
|---|---|
| **UI/UX Pro Max** (a large style/palette catalog plugin) | Healthy, popular and MIT, and re-evaluated on its output rather than on principle. Given three real product descriptions, its design-system generator returned an auction palette over a Playfair Display body for a grocery price tool, and a testimonials carousel in "AI purple + generation pink" for a security console ([reproduction](benchmarks.md#6-uiux-pro-max-design-system-generator)). It matches keywords to curated rows, so a product that shares words with the wrong row inherits that row's whole look. The plugin also installs seven skills, not one: about 2,700 characters of always-on descriptions, one claiming every interface task and another pointing every UI task at shadcn/ui and Tailwind. Claude Code's `skillOverrides` setting can now hide a skill from the model (its documentation does not say how plugin skills are keyed), so routing alone might no longer rule it out. The output does. |
| **Installing a living external guidelines document** | The install path was an unvetted third-party CLI, and the document changes. Fetching it on demand during a UX audit is always current, costs zero always-on context, and adds no new CLI. |
| **Reviewing UI from the source diff** | Source is not visual evidence. A screenshot is. The rendered-interface judge is explicitly told it has no finding if it has not looked at a render. |
| **A global house style** | Nothing global should outrank the product's own design system. |
| **Design plugins that bundle a routing skill** (21st.dev, Refero, impeccable, Superdesign, taste-skill) | Each ships a skill that claims the whole design task. Refero's calls itself the "Primary/default skill for UI design … even when live Refero MCP tools are not configured"; 21st.dev's triggers on any request for a component, with "a pricing section" and "a testimonials block" as its examples. Installed, each becomes a second design authority beside `frontend-design`. Where one has a capability this layer lacks, take its MCP server alone (below) and leave the skill. |
| **Component generators** (hosted UI generation, stock-block MCPs) | Generation returns the generator's look, and stock blocks are more template chrome: the failure this layer exists to remove. Discovery that returns source to adapt is a different thing, and is below. |
| **Motion's AI Kit, installed globally** | It adds a `/motion` skill and MCP servers. The free part is docs search; spring generation, audits and examples need a paid Motion+ sign-in. A global skill would pull every animation task toward a library the policy adds only when the platform cannot do the job. `frontend-quality` reads Motion's current docs on demand instead, in projects that already use it. |
| **Figma's MCP** | Only useful where Figma files are the source of truth, and a large surface. Per project, if ever. |
| **Density rules in the build path** (a line in `rules/frontend.md`, or a section in `frontend-quality` or `design-brief`) | Tested before writing, and the failure did not reproduce. Ten fresh-context plans for a price-comparison brief all put real prices in the first viewport, grouped the one store holding most of the cheapest offers, and used desktop width for comparison columns ([benchmarks](benchmarks.md#7-design-layer-micro-tests)). That is weaker than it sounds: the fixture showed the data and its shape outright. The shipped screens that did fail were following a brief that mandated the repetition, and a builder rule cannot outrank the brief. Surfacing a cost the brief imposes is a review job, so the review lens changed instead. The closing check of `design-brief`'s reference step, which names the defaults to go back from, is not such a rule: it is the owner's policy, sits where references are chosen, and is untested ([benchmarks](benchmarks.md#9-claims-made-with-no-measurement-at-all)). *Page composition* is the exception, and is now in `design-brief`: a full build from an ordinary request did fail there, shipping hero, one grid and footer with no mobile navigation ([benchmarks](benchmarks.md#8-frontend-research-trigger-and-three-way-build)). Whether the paragraph prevents that is untested. |
| **A motion rule** in `rules/frontend.md` | Five runs on interactions CSS can do all chose CSS (`@starting-style`, `grid-template-rows`), animated nothing on a re-sort, and added no dependency. The platform-first half needs no rule. The other half, when Motion is justified, is one sentence in `frontend-quality` and is untested. |

### Chosen: reference and component MCPs without their skills

Each server adds something the layer lacks; none of their bundled skills is
installed. `design-brief` (screen references) and `frontend-quality` (components)
use one only when it is connected, and only for structure, behavior and
principles, never for the product's look.

The screen-reference servers are at user scope, because the reference step lives
in the global `design-brief` and has to reach every project, and because the
accounts belong to a person, not a repository. User scope is as private as local
scope: it is `~/.claude.json`, never committed. Refero is searched first. Mobbin
is added only when Refero's coverage of a screen type is weak, when mobile-app
patterns are central, or when a second set would change the decision; querying
both by default would double the reference context for no stated gain. MCP tools
here load through tool search, so what every session pays for a user-scope server
is its tool names and any instructions it sends; check `/context` after signing
in.

shadcn's and Motion's servers are per project: each helps only where the project
uses its stack. 21st.dev's started out per project too and is now at user scope,
for two reasons found in a diagnostic run
([benchmarks](benchmarks.md#8-frontend-research-trigger-and-three-way-build)).
First, per project meant never: it had been added from the home directory, so
its local scope was the home directory's, and no session in a real repository
ever loaded it. A new project, where component research matters most, never has
it either. Second, its research tools (`search`, `get_inspiration`) return
metadata and preview images, which help any web stack. Only `get_component`
returns React and Tailwind source, and `frontend-quality` fetches code only in
such a project. In context, what user scope costs every session is the tool
names, since MCP tools load through tool search: the server sends no
instructions. Every session does connect to it with the key, though. When the
tools are called is decided by the route in `frontend-quality`: substantial
work researches, a small fix never does. With neither 21st.dev nor a reference
server connected, substantial work gets no outside research at all; nothing
replaces it ([benchmarks](benchmarks.md#8-frontend-research-trigger-and-three-way-build)).

Every 21st.dev tool that generates, publishes, or writes to the account's
profile, bookmarks or catalog entries is denied in user `settings.json`
([template](../config/settings.example.json)). One tool that sends data is left
allowed: `record_inspiration_feedback` records an accept or reject on an
inspiration result under the key, and feeds 21st.dev's ranking. The rules
match a server named `21st`: connect it with the command below rather than the
vendor's CLI, whose server name was not checked, or rename the rules.

| Tool | Where it applies | Setup |
|---|---|---|
| Refero MCP | Primary screen and flow references. Needs a paid plan (Pro, Team or Lifetime). Queries leave the machine | `claude mcp add --scope user --transport http refero https://api.refero.design/mcp`, the MCP only, not the plugin. Sign in with `/mcp`; with an API token instead, add `--header "Authorization: Bearer YOUR_TOKEN"` |
| Mobbin MCP | Second reference set, strongest on mobile apps. Pro, Team or Enterprise plan, not Free. Queries leave the machine | `claude mcp add --scope user --transport http mobbin https://api.mobbin.com/mcp`. Sign in with `/mcp` |
| 21st.dev MCP | Component and composition research for substantial frontend work, routed by `frontend-quality`. API key. `search`, `get_inspiration`, `get_theme` and `search_logo` are free metadata; on the free tier `get_component` (React and Tailwind source) allows two retrievals a day; hosted generation needs a paid AI entitlement and is denied here anyway | `claude mcp add --scope user --transport http 21st https://21st.dev/api/mcp --header "x-api-key: YOUR_API_KEY"`, the MCP only, not the plugin |
| shadcn MCP (official) | Projects that already use shadcn/ui; it reads registries from `components.json` and returns source | `npx shadcn@latest mcp init --client claude` (writes the project's `.mcp.json`) |
| Motion docs MCP | Projects that depend on Motion and want docs search in the session; otherwise `frontend-quality` points at motion.dev/docs. Free, no account | `claude mcp add --scope project --transport http motion https://mcp.motion.dev` |

Mobbin's command is its own documentation's, and Refero's is its documented
MCP-only form with the token header left off for OAuth (both as of 2026-09-28).
Both were run, and both servers answered with a sign-in challenge. 21st.dev
documents a CLI that writes a project `.mcp.json`; the command above pairs its
documented endpoint and header with Claude Code's `claude mcp add` syntax. On
2026-09-29 that endpoint and header answered `initialize` and `tools/list` with a
valid key (and 401 without one), and a Claude Code session called `get_usage` and
`search` through it. The live list had 34 tools, of which a session saw 23 once
the 11 denied tools the server offered were removed; `generate` and
`iterate_generation` were absent because the account had no AI entitlement, and
four catalog-review tools (`submit_component`, `withdraw_component`,
`resubmit_component`, `remove_component_from_catalog`) had appeared since the
deny list was written from the documentation. They are denied now. A deny rule
for a renamed tool silently stops matching, so compare the list with the tools
`/mcp` shows. The shadcn command is shadcn's own; Motion's transport is inferred
from its HTTPS endpoint.

---

## Infrastructure

### Chosen: one skill, one enforcement hook, zero new agents, zero global plugins

| Alternative | Why not |
|---|---|
| **Installing infrastructure agent packs at user scope** | Their agent descriptions are long and end in "Use PROACTIVELY". At user scope that loads into every session's routing context and pulls the agents into non-infrastructure work. The broad packs also duplicate each other heavily — one specialist agent appeared in three packs, another in four. |
| **Installing them per project instead** | This *is* the chosen path when the work needs them: narrow packs, `--scope project`, two or three agents, no skills. |
| **An infrastructure-specific security reviewer** | No second security reviewer. `security-judge` owns that lens; infra changes route to the high-risk tier and reuse it. |
| **Trusting the model not to run `terraform apply`** | It is a single command away from mutating production. Guards exist for exactly the cases where good judgement is not enough. |

---

## Tooling policy

### Chosen: one owner per job, no global version pins

| Alternative | Why not |
|---|---|
| **Black + isort + Flake8 alongside Ruff** | Overlapping owners for formatting and linting produce fights and double config. Ruff owns both. |
| **mypy alongside Pyright** | Two type checkers, two sets of ignores, no added truth. Pick one per repository. |
| **Pinning versions in global config** | A global pin silently ages into an EOL default. Versions get chosen at project creation or at a deliberate upgrade, by checking what is current at that moment. |
| **Migrating existing repositories to the preferred toolchain** | Churn with a real regression risk, as a side effect of unrelated work. Inspect first; Poetry, mypy, npm and Biome that work are not gaps. |
| **`pre-commit run --all-files` on every commit** | Slow enough that it gets bypassed, which is worse than not having it. Staged files at commit stage, expensive checks at push stage. |

---

## Process layer

### Chosen: Superpowers for workflow, nothing else routing

| Alternative | Why not |
|---|---|
| **A custom "engineering orchestrator" skill** | A third router competing with the workflow layer and the review layer. The model then picks between routers instead of doing the work. |
| **Writing custom brainstorming / TDD / debugging skills** | They already exist, maintained, in the official plugin. Rewriting them is the over-engineering the setup is supposed to catch. |
| **No process layer** | Jumping to implementation without establishing acceptance criteria is where most agent rework comes from. |

---

## Configuration distribution

### Chosen: a public repository + an idempotent installer with backups

| Alternative | Why not |
|---|---|
| **Symlinking a dotfiles repo into `~/.claude`** | Elegant until a tool rewrites a file in place, or you want to adopt three of eleven components. The installer copies, so partial adoption and local edits are both fine. |
| **A single `curl \| bash` bootstrap** | Nobody reads it, it cannot be dry-run, and it runs before you have seen what it does. The installer here defaults to showing you the plan. |
| **Automatically merging into an existing `settings.json`** | The one file where a bad merge silently changes every future session. The installer refuses to merge and writes a proposal file beside it instead. |
| **Publishing `~/.claude` verbatim** | It contains transcripts, session state, plugin caches, machine paths and third-party vendored code under a non-commercial licence. See [security.md](security.md). |
