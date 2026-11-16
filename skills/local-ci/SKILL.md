---
name: local-ci
description: Validate locally before anything reaches remote CI - `local-ci auto` derives a validation plan from a repository's own checks and the GitHub Actions jobs its change affects, runs them (jobs via nektos/act), and records evidence tied to the exact content being published; hooks start it automatically. Use when the Stop hook or the push gate asks for local validation, before git push, a PR or a remote workflow run, when remote CI failed and needs reproducing, and when changing a repository's CI triggers or cost.
---

# Local-first CI

The policy is "Local-first CI" in `CLAUDE.md`; this skill is the procedure.
Remote CI is final verification. Every push to a branch with a push-triggered
workflow, and every update to a PR, spends runner minutes, so a speculative fix
pushed "to see if CI passes" is the most expensive way to run a test.

Tool: `~/.claude/bin/local-ci` (Python standard library, no dependencies).
Evidence lives outside the repository, keyed by tree content, under
`~/.cache/claude-hooks/local-ci/`.

## 1. It starts on its own

Nobody has to ask for local validation, and no one types a CI command:

- **At the end of a turn** (`Stop` hook, `local-ci-auto.sh`): when the session
  changed a repository and that content has no complete validation, the stop is
  held once with the instruction to run `~/.claude/bin/local-ci auto`. Run it
  (Bash, 600000 ms timeout or in the background: act jobs take minutes).
- **At publication** (`PreToolUse` hook, `local-ci-gate.sh`): `git push`, PR
  creation and remote workflow runs are denied until the plan passed for the
  exact content being published. The denial says the same thing: run `auto`.

When implementation is ready, run `auto` before being asked; the hooks are the
backstop, not the trigger. Do not run it after every edit: once per batch of
changes, then again only after a fix.

## 2. `local-ci auto`: the plan, then the checks

```
~/.claude/bin/local-ci auto                # derive, record and run the plan
~/.claude/bin/local-ci auto --plan-only    # show it; run and record nothing
```

It reads what the repository already defines: `package.json` scripts with the
lockfile's package manager, `pyproject.toml` tools (through `uv run`,
`poetry run` or `pdm run`), `go.mod`, `Cargo.toml`, Makefile targets,
`scripts/verify|check|test*`, Terraform, Dockerfiles, compose files, pre-commit,
and every `.github/workflows/*.yml|yaml` with each job classified. It installs
nothing and invents no command. Every item becomes:

| Class | Meaning | Counts for publishing |
|---|---|---|
| required | runs here | must pass |
| unsupported | its tool, Docker, act, a secret or a GitHub token is missing; the exact reason is shown | reported unverified, never a pass |
| skipped | a path filter, or a plain job running the same command as a required local check; the reason is shown | no |
| remote only | deploy, release, publish, write permissions, release-only workflows | never run locally |

Below the root, a directory up to two levels down with its own `package.json`,
`pyproject.toml`, `go.mod` or `Cargo.toml` (a monorepo package) is planned too,
in its own directory, when the change touches it and the root has no manifest
of that stack (a root manifest is taken to drive its workspace). Workflows only
started by hand (`workflow_dispatch`) are skipped; a workflow is relevant when
any trigger a code change fires (`push`, `pull_request`, `merge_group`) matches
the changed files. Matrix legs act cannot run (macOS, Windows) are listed
unsupported next to the job's pass.

It records the plan against the content fingerprint, then runs whatever has not
passed for that content: the repository's commands cheapest first (format and
lint, types, tests, builds, e2e and image builds), then the workflow jobs under
act — deferred while a local check is failing (`--keep-going` runs them anyway).
A check that modifies files is recorded `changed`, not a pass, and stops the run.
A `docker build` is required only when a Dockerfile, compose file or dependency
manifest changed. It builds from the context a compose file declares for that
Dockerfile, otherwise from the Dockerfile's own directory, unless what its
`COPY`/`ADD` lines name exists only from the repository root (a wildcard
matching nothing is optional, as in BuildKit). A compose
override (any compose file next to `compose.yaml` or another base file) is
validated merged onto the base, `docker compose -f base -f override config -q`,
as Compose uses it; alone, its services have no image and it is not a project.
A `uv run` check whose project sets a `required-version` the installed uv does
not satisfy is unsupported, both versions named (uv refuses to run, so the tool
is effectively missing); the plan names the required Makefile targets that run
the same tool through the repository's own toolchain. That applies only when
the merge base has the same `required-version`: one the change adds or edits
keeps its checks required, so a change cannot make its own checks unsupported.
Exit 0 means every
required check passed for exactly this content.

On a failure: read the log it names, fix the cause, run `auto` again. Checks
that passed for unchanged content are not rerun; a fix changes the content, so
what it could affect runs again. Never weaken a check, mark it unsupported, or
change the repository's workflow to get a pass. A README, CONTRIBUTING or the
repository's own `CLAUDE.md` outranks the plan when they name a check it cannot
see: run that one too with `local-ci run -- <cmd>` (any failure blocks).

A repository can state its checks in `.local-ci.json`:
`{"checks": ["<command>", ...], "exclude": {"<discovered command>": "<why it is not a check here>"}}`.
It is read only as committed at the merge base with the default branch, so it
takes effect once merged: a change can never loosen the checks that validate
it, and adding or editing the file is reported in the plan. Use it when
discovery guesses wrong (a script that needs an argument), not to skip a check
that fails; an exclusion without a reason makes the file invalid and ignored.

The single steps, for diagnosis: `plan` (what was discovered and why),
`run -- <cmd>` (one check, recorded; a one-string command is its own name, so it
is the plan's check), `act --list` / `act --workflow F --job J` (one job).

By stack, using only what the repository already has:

| Stack | Typical evidence |
|---|---|
| Python | `ruff format --check`, `ruff check`, `pyright` or the repo's `mypy`, `pytest`; `uv build` when packaging changed |
| JS/TS | the repo's `lint`, `typecheck`, `test` (run-once mode), `build` scripts through its package manager |
| Go | `gofmt -l`, `go vet ./...`, `golangci-lint run` if configured, `go test ./...`, `go build ./...` |
| Docker | `docker build` only when the image or its inputs changed; `docker compose config -q` |
| Terraform | `fmt -check`, `init -backend=false` + `validate`; plan only with the user's go-ahead for real backends; never apply (hook-enforced) |
| Workflows | `actionlint` if installed; the affected jobs under act |

Do not install a tool the repository does not use when it has a working
equivalent. A tool that is missing makes its check unsupported; install it only
when the repository expects it and the user agrees.

## 3. GitHub Actions jobs, locally

`auto` runs every affected, runnable job under act. It skips one only when
equivalence is established: a *plain* job (setup actions and run steps; no
matrix, container, services, env, working directory or shell) whose every check
command is the same command line as a required local check (`npm test` and
`npm run test` are the same). Anything less runs under act too. Jobs that use
Docker (§4) or a GitHub token are reported unsupported rather than run to a
certain failure. Matrix jobs run every Linux leg (`job-1`, `job-2`, ...); macOS
and Windows legs stay remote.

What act runs with, whether `auto` or `local-ci act` starts it:

- **Preflight.** It checks for `act`, the `docker` CLI and a reachable daemon
  (`docker info`). Any of them missing is recorded as *unsupported*, never as a
  failure and never as a pass. Install act on macOS with `brew install act`; on
  Linux, from the [act releases](https://nektosact.com/installation/). Docker
  Desktop, colima or dockerd provide the engine.
- **Selection.** Workflows with a `pull_request`, `push`, `merge_group` or
  `workflow_dispatch` trigger whose `paths`/`paths-ignore` filters match the
  files changed since the merge base with the default branch; within them,
  jobs classified *runnable*. `local-ci act --workflow/--job` narrows it by hand.
- **Never run, reported as `unsafe`:** jobs with a deployment `environment`,
  write permissions, deploy/release/publish names, steps that publish, push,
  deploy, sync files out or call a cloud CLI (`npm run deploy`, `make release`,
  `./deploy.sh`, `semantic-release`, ...), release-only workflows, and any job
  that `needs:` one of those, because `act -j` runs a job's dependencies too.
  Run them only remotely, through the repository's own process. The
  classification reads names, keys and step text; `--list` shows what would
  run before anything does.
- **Not run, reported as `unsupported`:** macOS/Windows/self-hosted runners,
  reusable-workflow jobs, jobs that read repository secrets, and jobs needing
  one of those.
- **Isolation.** act gets an allowlisted environment (no `GITHUB_TOKEN`,
  `GH_TOKEN`, cloud or registry credentials), a throwaway `HOME`,
  `XDG_CONFIG_HOME` and `GH_CONFIG_DIR`, and an *empty* `GITHUB_TOKEN` secret.
  Given no token, act fetches your own from `gh auth token` and hands it to the
  workflow; given a dummy, GitHub rejects the clone of every public action.
  Empty `--secret-file`, `--env-file` and `--var-file`, so a repository `.env`
  or `.secrets` is never read. No Docker socket inside job containers
  (`--container-daemon-socket -`), and `--container-options-policy restrict`
  where act supports it (0.2.97 does); on an older act, jobs that set container
  volumes or options, and jobs needing them, are skipped. `--docker-socket`
  mounts the socket (root on the machine) only when the user says so, and only
  on an isolated daemon (§4). Jobs run on act's host network: a job that
  connects to `localhost` ports can reach services the developer published.
- **Refusals.** act applies an actrc to every run: the repository's `.actrc`
  could switch the isolation off (`--bind`, `-self-hosted`, secrets, host
  paths), and a user-level actrc is read even with a throwaway `HOME` (on macOS
  from `~/Library/Application Support/act/actrc`). `local-ci act` refuses while
  either has content. It also refuses when a secret-looking file (`.env`, keys,
  `.netrc`, ...) is ignored only by global or `.git/info` excludes, because act
  copies the work tree honouring the repository's `.gitignore` alone.
- **Runners.** It maps `ubuntu-latest`, `-24.04` and `-22.04` to
  `catthehacker/ubuntu:act-*` images (several hundred MB on first pull;
  `--pull=false` still pulls a missing image, it only skips re-pulling);
  `--platform LABEL=IMAGE` chooses another, never `-self-hosted`. On Apple Silicon and other ARM hosts it runs
  `linux/amd64` containers to match GitHub's runners (`--native-arch` trades
  that fidelity for speed, and avoids act's amd64 image builds for Docker
  actions, which can fail with a platform mismatch on those hosts).
- **Events.** A generated payload for the workflow's own trigger
  (`pull_request` preferred, then `push`), with the current branch and HEAD.
- **Results.** *pass* when the job succeeded; *fail* on any failed step, with
  the step names and the log path; *unsupported* when act or the engine failed
  (image pull, daemon, unsupported platform) before any step failed, or when
  every failed step's own output shows a missing runner capability (§4). An
  invalid workflow or an action that cannot be cloned is a *fail*: GitHub would
  reject it too. Any other failed step is a *fail*, whatever environmental line
  sits next to it; the summary says when one looks environmental, and the
  step's command, run directly, tells which. A later unsupported run (Docker
  stopped) never clears a failure.

A passing act run is **partial evidence**: those steps passed under act, on an
approximation of the runner image, without secrets. It does not show that the
other jobs, the remote images, or the required checks will pass.

## 4. Docker-dependent jobs and missing runner capabilities

act is unsafe for a job that uses Docker, whether a step names it or reaches it
through a Makefile target or a repository script (`make test-all` ->
`check-tools` -> `docker info`; the plan prints the chain). With the socket,
the job is root on the daemon and sees every container and volume on it: a
compose project with a pinned name reuses the developer's containers and
database volumes. A running daemon does not make that safe. Neither does act's
default host network, where `localhost` reaches the developer's published
ports (measured: a job opened a dev database's port), so every job runs on a
bridge network of its own, created and removed per run, with
`host.docker.internal` and `gateway.docker.internal` pointed at itself (act
does not apply that to a job's own `container:`; there, and through Docker
Desktop's gateway IP, only a workflow addressing the host on purpose reaches
it). So:

- **Required locally:** the repository's own checks, and every affected job that
  uses no Docker, no service containers, needs no secret or token, and is not
  a deploy.
- **Unsupported locally, never run:** a Docker-using job (and anything that
  `needs:` it) without `--docker-socket`; a job with `services:` (GitHub reaches
  them at `localhost` on the host network, which local runs never get); a
  discovered local check (a Makefile target, a script) that starts Docker on
  the developer's daemon - run it yourself, or declare it in `.local-ci.json`.
  `--docker-socket` (the user's call, per run) mounts the socket into every
  job, so every job is refused unless `DOCKER_HOST` points at an engine that
  holds no container or volume act did not create; it is checked at planning
  and again right before act starts. The developer's daemon is refused, naming
  what it holds; there is no flag that accepts it.
- **Unsupported at runtime:** a job whose every failed step shows the runner,
  not the code, could not do it, in that step's own lines: act's own exec of
  the step could not find its program (`exec: "node": executable file not
  found` - act drops the image's tool path after a step adds to `PATH`), or the
  step reached for the Docker socket the job was not given, or the `Post`
  step of a setup or cache action (`actions/setup-*`, `actions/cache`,
  `astral-sh/setup-uv`, `ruby/setup-ruby`) could not save its dependency cache
  (`Path Validation Error`, cache service unreachable: act's cache server and
  work-tree volume are not GitHub's), with no other failure line (a failed
  test, an assertion, an error) next to it. Anything else, including `node`
  missing inside the code's own container, a cache error in a `Main` step, or
  the same message from any other action, is a *fail*.
- **Direct checks prove** that the same command passed on this machine for this
  content; the plan names the commands an unsupported job shares with a local
  check. They do not prove the job: not its runner image, services, Docker
  engine or secrets.
- **Only GitHub Actions verifies** every job listed unsupported or remote only.
  The gate's note and the final report name them; wait for them before
  merging.

**The push gate allows** publication when this exact content has a recorded
plan, every required check passed or (an act job) ran and was classified
unsupported from its own log, and no check is blocked. **It refuses** when any
check failed or changed the tree and has not passed since, a required check
never ran, the plan is missing, or the evidence belongs to other content.

Failures recorded before this classifier existed are reread from their own
logs by `auto`, printed, and superseded only when every failed step shows a
missing capability; the log, the old record and the new one stay in the
ledger. A failure recorded by the current classifier is final until the same
check passes.

Discovery fixes work the same way. When a plan from an older local-ci required
a check that the current plan no longer derives (it was derived wrongly: an
override validated alone, an image built from the wrong context, a `uv run`
under a uv the project rejects), `auto` records that check's failure for this
content as *superseded*, prints it with what the current plan does instead,
and `status` keeps listing it; it is never a pass. A failure stays blocking
when the current plan still requires the check, lists it unsupported or
skipped for any reason other than one the corrected discovery detects (a tool
or Docker now unavailable, a path filter, a declaration), was recorded after a
current plan existed for this content, or no older plan required it
(`local-ci run` by hand).

## 5. Unsupported checks are reported, not passed

When a required check cannot run here (a credential, hardware, a hosted
service), record it and say so in the final report:

```
~/.claude/bin/local-ci unsupported --name e2e --reason "needs staging credentials"
```

It never counts as a pass. A check that ran and failed cannot be relabelled
unsupported, and neither can a required check of the plan: it can run here, so
it must pass, or the user decides to publish without it. A check is identified
by its name, command and directory: running something else under a failed
check's name does not clear it; only that check passing again does.

What the gate proves: *this exact content has a recorded plan, every check it
requires passed, and nothing failed since*. A pass of some other check never
stands in for a required one. It cannot see a check the repository documents
only in prose; §2 says what to do about those.

## 6. Publish exactly what was validated

```
~/.claude/bin/local-ci status        # working tree and HEAD; HEAD is what a push sends
```

Evidence is keyed by a fingerprint of every tracked and untracked, non-ignored
file, and a push is checked against exactly the commits it sends. Validating
uncommitted work and then committing all of it keeps it valid; committing part
of it, leaving an untracked file out of the commit, or editing anything
afterwards makes it stale. Commit, check `status`, then push or open the PR
once. Group fixes into one push. Commits themselves are not gated: they are
local and free, and `Quality gates` already asks for the targeted checks first.

When remote CI then fails: read the failure (`gh run view <id> --log-failed`),
reproduce it locally, fix, revalidate, and push once. Rerun a remote job
(`gh run rerun --failed`) only for a failure shown to be infrastructure, and
say so. Never push again just to see whether it passes.

## 7. What is enforced, and what is not

| Mechanism | Covers | Does not cover |
|---|---|---|
| `local-ci-auto` SessionStart + PreToolUse(file tools) + Stop hook | the end of every turn that changed a repository the session started in or edited with a file tool, while its content is not validated and not already on a remote branch: held once per content state, at most three times in a row | a repository the session changed only through Bash commands and did not start in; a session with `LOCAL_CI_AUTO=0` |
| `local-ci-gate` PreToolUse hook (deny) | `git push` with its refs (`--all`, `--tags`, `:`, `src:dst`), through `-C`, `--git-dir`, `cd`, `sh -c`, `sudo`/`env`/`timeout` wrappers and `$(...)`; `gh pr create`, `gh pr ready`, `gh pr update-branch`, `gh workflow run`, `gh run rerun`, `gh release create`, `gh api .../dispatches\|update-branch\|rerun` | a script file or a command assembled at run time; `env -C`/`sudo -D` directories; GitHub MCP tools (the hook sees Bash only); `gh pr merge`, deliberately (it follows remote checks); whether the right checks were chosen |
| Opt-in `pre-push` git hook | every `git push` from an agent session, through any wrapper or script, checked per pushed commit | `gh` operations that do not push; human pushes (not enforced); a command that deliberately unsets `CLAUDECODE` |
| `local-ci auto` | which checks are required, act selection, equivalence, reporting what is unsupported | checks the repository documents only in prose |
| This skill and `CLAUDE.md` | fixing failures, reporting | nothing executes them |
| The repository's workflow triggers | whether remote CI runs at all after a push | this configuration cannot change them |

`local-ci hook install` adds the pre-push gate to a repository only when it has
no pre-push hook and no `core.hooksPath`; otherwise it changes nothing and
prints the line to add to the repository's own hook manager (pre-commit,
husky, lefthook). The gate is enforced only when `CLAUDECODE` (set in Claude
Code sessions) or `LOCAL_CI_ENFORCE=1` is present, so a human's push is the
human's call. A human who wants to publish unvalidated work runs the command
themselves; an agent never bypasses the gate, and never uses `--no-verify`
(hook-enforced).

## 8. Cutting remote CI minutes (repository changes, proposed not applied)

A configuration cannot stop a repository's workflows from triggering on push.
That is decided by each repository's `.github/workflows`, which belong to that
repository. Change them only in the repository being worked on, as a reviewed
change of their own, never across unrelated repositories. Check, in order of
usual payoff:

1. **Duplicate runs.** `on: [push, pull_request]` runs everything twice for a
   PR branch. Use `push: branches: [main]` plus `pull_request`.
2. **Superseded runs.** At workflow level, for PR and branch builds:
   `concurrency: {group: ${{ github.workflow }}-${{ github.ref }}, cancel-in-progress: ${{ github.event_name == 'pull_request' }}}`.
   Never cancel in-progress deploys or default-branch runs whose result matters.
3. **Irrelevant runs.** `paths-ignore` for docs-only changes, or `paths` for a
   component. A *required* check that a path filter skips stays pending and
   blocks merging; use a changes-detection job and an always-running final job
   that the branch protection requires instead.
4. **Drafts.** `pull_request: types: [opened, synchronize, reopened, ready_for_review]`
   with `if: github.event.pull_request.draft == false` on expensive jobs.
5. **Caching.** `actions/setup-node|setup-python|setup-go` `cache:` inputs, or
   `actions/cache` keyed on the lockfile.
6. **Tiering.** Fast checks on every PR; slow integration, browser or
   cross-platform matrices on `merge_group`, the default branch, a label, a
   schedule, or `workflow_dispatch`. Keep the matrix legs that catch real
   breakage; trim the rest on PRs.
7. **Bounds.** `timeout-minutes` on every job, so a hung job cannot burn hours.

Keep remotely what needs GitHub: secrets-backed integration, platform runners
the machine lacks, security scanning, release and deploy, and the checks branch
protection requires. Never add `[skip ci]` to get past CI, disable a required
check, or change branch protection to save minutes. Workflow edits are
infrastructure: they go through `infrastructure-quality` (pinned actions,
minimal `permissions`).

## Report

State what `auto` ran and its result, every check recorded unsupported with its
reason, act jobs run, skipped and remote-only (and why), any failure reread
from its log, and that GitHub Actions is still to run. Never present local
evidence as remote proof.
