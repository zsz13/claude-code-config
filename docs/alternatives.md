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
| **A large style/palette catalog plugin** | Healthy, popular and MIT — and precisely the failure mode this layer exists to prevent: picking an aesthetic from a list of named styles instead of deriving it from the product. Its routing description would also compete with the official design skill, and it cannot be subordinated by configuration. Worth installing *per project* if you want it; not globally. |
| **Installing a living external guidelines document** | The install path was an unvetted third-party CLI, and the document changes. Fetching it on demand during a UX audit is always current, costs zero always-on context, and adds no new CLI. |
| **Reviewing UI from the source diff** | Source is not visual evidence. A screenshot is. The rendered-interface judge is explicitly told it has no finding if it has not looked at a render. |
| **A global house style** | Nothing global should outrank the product's own design system. |

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
