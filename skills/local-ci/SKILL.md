---
name: local-ci
description: Validate locally before anything reaches remote CI - discover a repository's own checks, run the fast relevant ones first and then the full gate, run affected GitHub Actions jobs locally with nektos/act where that helps, and record evidence tied to the exact content being published. Use before git push, creating or updating a PR, or starting a remote workflow; when remote CI failed and needs reproducing; and when changing a repository's CI triggers or cost.
---

# Local-first CI

The policy is "Local-first CI" in `CLAUDE.md`; this skill is the procedure.
Remote CI is final verification. Every push to a branch with a push-triggered
workflow, and every update to a PR, spends runner minutes, so a speculative fix
pushed "to see if CI passes" is the most expensive way to run a test.

Tool: `~/.claude/bin/local-ci` (Python standard library, no dependencies).
Evidence lives outside the repository, keyed by tree content, under
`~/.cache/claude-hooks/local-ci/`.

## 1. Discover (once per task)

```
~/.claude/bin/local-ci plan
```

It reads what the repository already defines: `package.json` scripts with the
lockfile's package manager, `pyproject.toml` tools (through `uv run`,
`poetry run` or `pdm run`), `go.mod`, `Cargo.toml`, Makefile targets,
`scripts/verify|check|test*`, Terraform, Dockerfiles, compose files, pre-commit,
git hooks and `core.hooksPath`, and every `.github/workflows/*.yml|yaml` with
each job classified and the commands its steps run. It installs nothing and
invents no command. A repository's README, CONTRIBUTING or own `CLAUDE.md`
outranks the plan when they disagree.

## 2. Validate, cheapest reliable check first

Record each check so the evidence is bound to the content it ran against:

```
~/.claude/bin/local-ci run -- <command>          # e.g. -- uv run pytest -q
~/.claude/bin/local-ci run --name unit -- 'pnpm run test -- --run'
```

Order: formatter check and linter on what changed, type check, the tests the
change affects, then the full relevant suite and the build before pushing
(`Quality gates` in `CLAUDE.md`). On a failure, fix locally and rerun only that
check; `run` refuses to repeat a check that already passed for identical
content (`--force` overrides). A check that modifies files is recorded as
`changed`, not a pass: inspect the change, stage it, rerun.

By stack, using only what the repository already has:

| Stack | Typical evidence |
|---|---|
| Python | `ruff format --check`, `ruff check`, `pyright` or the repo's `mypy`, `pytest`; `uv build` when packaging changed |
| JS/TS | the repo's `lint`, `typecheck`, `test` (run-once mode), `build` scripts through its package manager |
| Go | `gofmt -l`, `go vet ./...`, `golangci-lint run` if configured, `go test ./...`, `go build ./...` |
| Docker | `docker build` only when the image or its inputs changed; `docker compose config -q` |
| Terraform | `fmt -check`, `init -backend=false` + `validate`; plan only with the user's go-ahead for real backends; never apply (hook-enforced) |
| Workflows | `actionlint` if installed; `local-ci act --list` for what would run |

Do not install a tool the repository does not use when it has a working
equivalent. Cost is local time and resources too: run the expensive suite once,
at the end, not after every edit.

## 3. GitHub Actions jobs, locally (only where it adds something)

```
~/.claude/bin/local-ci act --list            # what would run, what is skipped and why
~/.claude/bin/local-ci act                   # affected, runnable jobs
~/.claude/bin/local-ci act --workflow ci.yml --job test
```

Use act when the workflow is the only definition of a check (a matrix leg, a
service container, a script only CI calls) or when the workflow itself changed.
When a job just runs `npm test`, run `npm test` directly: it is faster and the
same check. `plan` prints each job's commands for exactly this choice.

What `local-ci act` does:

- **Preflight.** It checks for `act`, the `docker` CLI and a reachable daemon
  (`docker info`). Any of them missing is recorded as *unsupported*, never as a
  failure and never as a pass. Install act on macOS with `brew install act`; on
  Linux, from the [act releases](https://nektosact.com/installation/). Docker
  Desktop, colima or dockerd provide the engine.
- **Selection.** Workflows with a `pull_request`, `push`, `merge_group` or
  `workflow_dispatch` trigger whose `paths`/`paths-ignore` filters match the
  files changed since the merge base with the default branch; within them,
  jobs classified *runnable*. `--workflow`/`--job` narrow it explicitly.
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
  mounts the socket for a workflow you trust that builds images.
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
  the step names and the log path; *unsupported* only when act or the engine
  failed (image pull, daemon, unsupported platform) before any step failed. An
  invalid workflow or an action that cannot be cloned is a *fail*: GitHub would
  reject it too. A failing step is never relabelled environmental; the summary
  says when one looks environmental, and the step's command, run directly,
  tells which. A later unsupported run (Docker stopped) never clears a failure.

A passing act run is **partial evidence**: those steps passed under act, on an
approximation of the runner image, without secrets. It does not show that the
other jobs, the remote images, or the required checks will pass.

## 4. Unsupported checks are reported, not passed

When a required check cannot run here (a credential, hardware, a hosted
service), record it and say so in the final report:

```
~/.claude/bin/local-ci unsupported --name e2e --reason "needs staging credentials"
```

It never counts as a pass, and a check that ran and failed cannot be relabelled
unsupported. A check is identified by its name, command and directory: running
something else under a failed check's name does not clear it; only that check
passing again does. Publishing still needs at least one passing check for that
content.

What the gate proves is narrow: *this exact content has recorded passing
evidence and no unresolved failure*. It cannot know which checks the repository
needs. Choosing them, by the order in §2, is the job, and the report says which
ran.

## 5. Publish exactly what was validated

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

## 6. What is enforced, and what is not

| Mechanism | Covers | Does not cover |
|---|---|---|
| `local-ci-gate` PreToolUse hook (deny) | `git push` with its refs (`--all`, `--tags`, `:`, `src:dst`), through `-C`, `--git-dir`, `cd`, `sh -c`, `sudo`/`env`/`timeout` wrappers and `$(...)`; `gh pr create`, `gh pr ready`, `gh pr update-branch`, `gh workflow run`, `gh run rerun`, `gh release create`, `gh api .../dispatches\|update-branch\|rerun` | a script file or a command assembled at run time; `env -C`/`sudo -D` directories; GitHub MCP tools (the hook sees Bash only); `gh pr merge`, deliberately (it follows remote checks); whether the right checks were chosen |
| Opt-in `pre-push` git hook | every `git push` from an agent session, through any wrapper or script, checked per pushed commit | `gh` operations that do not push; human pushes (not enforced); a command that deliberately unsets `CLAUDECODE` |
| This skill and `CLAUDE.md` | choosing the relevant checks, act use, reporting | nothing executes them |
| The repository's workflow triggers | whether remote CI runs at all after a push | this configuration cannot change them |

`local-ci hook install` adds the pre-push gate to a repository only when it has
no pre-push hook and no `core.hooksPath`; otherwise it changes nothing and
prints the line to add to the repository's own hook manager (pre-commit,
husky, lefthook). The gate is enforced only when `CLAUDECODE` (set in Claude
Code sessions) or `LOCAL_CI_ENFORCE=1` is present, so a human's push is the
human's call. A human who wants to publish unvalidated work runs the command
themselves; an agent never bypasses the gate, and never uses `--no-verify`
(hook-enforced).

## 7. Cutting remote CI minutes (repository changes, proposed not applied)

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

State the commands run with their result, `local-ci status` for HEAD, every
check recorded unsupported with its reason, act jobs run and skipped (and why),
and that remote CI is still to run. Never present local evidence as remote
proof.
