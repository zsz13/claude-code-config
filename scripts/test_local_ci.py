#!/usr/bin/env python3
"""Regression scenarios for bin/local-ci, hooks/local-ci-gate.sh and the installer's handling of them.

Every scenario runs in throwaway git repositories under a temporary directory with an isolated HOME,
git config, state directory and PATH. `act`, `docker` and `gh` are stubs that log how they were
called; pushes go only to a local bare repository (GIT_ALLOW_PROTOCOL=file), so nothing here can
reach GitHub or start a real workflow. Run by scripts/verify.sh.

Usage: python3 scripts/test_local_ci.py [-v]
Exit:  0 = every check held, 1 = at least one did not.
"""
import hashlib
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
LOCAL_CI = REPO / "bin" / "local-ci"
GATE_HOOK = REPO / "hooks" / "local-ci-gate.sh"
NO_VERIFY_HOOK = REPO / "hooks" / "block-git-no-verify.sh"
IAC_HOOK = REPO / "hooks" / "block-destructive-iac.sh"
VERBOSE = "-v" in sys.argv[1:]
results: list[tuple[bool, str, str]] = []

# act stub: answers --version and --help (with or without --container-options-policy, per help.mode),
# logs every real invocation and its environment, and prints what act prints for each act.mode.
ACT_STUB = """#!/bin/sh
here=$(dirname "$0")
if [ "$1" = "--version" ]; then echo "act version 0.2.97"; exit 0; fi
if [ "$1" = "--help" ]; then
  [ "$(cat "$here/help.mode" 2>/dev/null)" = old ] || echo "  --container-options-policy string"
  exit 0
fi
printf '%s\\n' "$*" >> "$here/act.argv"
env > "$here/act.env"
case $(cat "$here/act.mode" 2>/dev/null) in
  pass)    echo "[CI/test] 🏁  Job succeeded"; exit 0 ;;
  fail)    echo "[CI/test]   ❌  Failure - Main npm test"; echo "[CI/test] 🏁  Job failed"; exit 1 ;;
  infra)   echo "Error response from daemon: pull access denied for catthehacker/ubuntu"; exit 1 ;;
  both)    echo "Error response from daemon: transient"; echo "[CI/test]   ❌  Failure - Main npm test"; exit 1 ;;
  noop)    echo "nothing to do"; exit 0 ;;
  depok)   echo "[CI/build] 🏁  Job succeeded"; exit 0 ;;
  invalid) echo "Error: workflow is not valid. 'ci.yml': Line: 3"; exit 1 ;;
esac
exit 1
"""
DOCKER_STUB = """#!/bin/sh
here=$(dirname "$0")
printf '%s\\n' "$*" >> "$here/docker.argv"
if [ "$(cat "$here/docker.mode" 2>/dev/null)" = up ]; then
  case "$*" in *"--filter network="*) cat "$here/docker.netcontainers" 2>/dev/null; exit 0 ;; esac
  case "$1" in
    ps) [ -f "$here/docker.psfail" ] && { echo "permission denied" >&2; exit 1; }; cat "$here/docker.containers" 2>/dev/null; exit 0 ;;
    volume) cat "$here/docker.volumes" 2>/dev/null; exit 0 ;;
  esac
  echo "29.0.0 x86_64"; exit 0
fi
echo "Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?" >&2
exit 1
"""
GH_STUB = """#!/bin/sh
printf '%s\\n' "$*" >> "$(dirname "$0")/gh.argv"
echo "gh stub: tests must never call gh" >&2
exit 1
"""

CI_YML = """name: CI
on:
  push:
    branches: [main]
  pull_request:
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm test   # the check
  db:
    runs-on: ubuntu-latest
    container:
      image: node:20
      volumes:
        - /:/host
    steps:
      - run: npm run test:db
  after-db:
    runs-on: ubuntu-latest
    needs: [db]
    steps:
      - run: npm run report
  mac:
    runs-on: macos-latest
    steps:
      - run: make test
  integration:
    runs-on: ubuntu-latest
    steps:
      - run: ./it.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
  deploy:
    runs-on: ubuntu-latest
    environment: production
    needs: [test]
    steps:
      - run: ./ship-it.sh
  pkg:
    runs-on: ubuntu-latest
    steps:
      - run: |
          npm run build
          npm publish
  smoke:
    runs-on: ubuntu-latest
    needs: [pkg]
    steps:
      - run: npm run smoke
"""
RELEASE_YML = """on:
  release:
    types: [published]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: make dist
"""
DOCS_YML = """on:
  pull_request:
    paths:
      - 'docs/**'
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: make docs
"""
# .yaml extension, `on: push` shorthand, runs-on list, and one unsafe or unsupported form per job.
MORE_YAML = """on: push
jobs:
  lint:
    runs-on: [ubuntu-latest]
    steps:
      - run: make lint
  rel:
    runs-on: ubuntu-latest
    steps:
      - uses: softprops/action-gh-release@v2
  perms:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - run: make x
  tf:
    runs-on: ubuntu-latest
    steps:
      - run: terraform apply -auto-approve
  bump:
    runs-on: ubuntu-latest
    steps:
      - run: npm run deploy:prod
  reuse:
    uses: ./.github/workflows/reuse.yml
    secrets: inherit
  selfhosted:
    runs-on: [self-hosted, linux]
    steps:
      - run: make
  dyn:
    runs-on: ubuntu-latest
    steps:
      - run: echo "${{ toJSON(secrets) }}" > /dev/null
"""


def check(ok: bool, name: str, detail: str = "") -> None:
    results.append((bool(ok), name, detail))
    if VERBOSE or not ok:
        print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f"\n        {detail}" if detail and not ok else ""))


class Sandbox:
    def __init__(self, base: pathlib.Path):
        self.base = base
        self.home = base / "home"
        self.state = base / "state"
        self.tools = base / "tools"   # git, python3, sh ... and nothing else from the host
        self.stubs = base / "stubs"   # act / docker / gh when a scenario wants them
        for d in (self.home, self.state, self.tools, self.stubs):
            d.mkdir(parents=True)
        for tool in ("git", "sh", "bash", "env", "cat", "dirname", "sed", "true", "false", "mkdir", "rm", "ls",
                     "uname", "find", "cmp", "mktemp", "date", "chmod", "cp", "tr", "sort", "grep", "head", "tail",
                     "test", "ln", "touch"):
            path = shutil.which(tool)
            if path:
                (self.tools / tool).symlink_to(path)
        (self.tools / "python3").symlink_to(sys.executable)
        gitconfig = base / "gitconfig"
        gitconfig.write_text("[user]\n\tname = ci\n\temail = ci@localhost\n[init]\n\tdefaultBranch = main\n"
                             "[commit]\n\tgpgsign = false\n[advice]\n\tdetachedHead = false\n")
        self.env = {"HOME": str(self.home), "PATH": f"{self.stubs}:{self.tools}", "LANG": "C.UTF-8",
                    "GIT_CONFIG_GLOBAL": str(gitconfig), "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_ALLOW_PROTOCOL": "file", "LOCAL_CI_STATE_DIR": str(self.state),
                    "LOCAL_CI_BIN": str(LOCAL_CI), "TMPDIR": str(base),
                    # sentinels: must never reach act
                    "GITHUB_TOKEN": "sentinel-github-token", "GH_TOKEN": "sentinel-gh-token",
                    "AWS_SECRET_ACCESS_KEY": "sentinel-aws"}

    def stub(self, name: str, text: str) -> None:
        p = self.stubs / name
        p.write_text(text)
        p.chmod(0o755)

    def mode(self, name: str, value: str) -> None:
        (self.stubs / f"{name}.mode").write_text(value)

    def act_calls(self) -> list[str]:
        p = self.stubs / "act.argv"
        return p.read_text().splitlines() if p.exists() else []

    def run(self, argv, cwd, stdin: str | None = None, extra: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(argv, cwd=cwd, input=stdin, capture_output=True, text=True,
                              env={**self.env, **(extra or {})}, timeout=120)

    def lci(self, cwd, *args, extra: dict | None = None) -> subprocess.CompletedProcess:
        return self.run([sys.executable, str(LOCAL_CI), *args], cwd, extra=extra)

    def git(self, cwd, *args, extra: dict | None = None) -> subprocess.CompletedProcess:
        return self.run(["git", *args], cwd, extra=extra)

    def repo(self, name: str, files: dict[str, str]) -> pathlib.Path:
        root = self.base / name
        root.mkdir()
        self.git(root, "init", "-q")
        for rel, text in files.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        self.git(root, "add", "-A")
        self.git(root, "commit", "-qm", "init")
        return root

    def hook_out(self, hook: pathlib.Path, command: str, cwd, tool: str = "Bash") -> dict | None:
        payload = json.dumps({"tool_name": tool, "tool_input": {"command": command}, "cwd": str(cwd)})
        r = self.run(["sh", str(hook)], cwd, stdin=payload)
        return json.loads(r.stdout)["hookSpecificOutput"] if r.stdout.strip() else None

    def hook(self, hook: pathlib.Path, command: str, cwd) -> str | None:
        out = self.hook_out(hook, command, cwd)
        return None if out is None else out.get("permissionDecision") or "note"

    def ok(self, root, *args) -> bool:
        return self.lci(root, "gate", *args).returncode == 0

    def validate(self, root) -> None:
        """The minimum that makes content publishable where the repository defines no check of its own:
        one recorded pass, and the validation plan recorded by `auto`."""
        self.lci(root, "run", "--", "true")
        self.lci(root, "auto")


def scenario_evidence(sb: Sandbox) -> None:
    """1-3: a pass allows publishing, a failure blocks it, changed content makes evidence stale."""
    root = sb.repo("evidence", {"a.txt": "one\n", "sub/k.txt": "k\n"})
    check(not sb.ok(root), "no evidence: gate refuses")
    counter = sb.base / "unit-runs"
    unit = f"echo run >> {counter}"
    r = sb.lci(root, "run", "--name", "unit", "--", unit)
    check(r.returncode == 0 and "PASS" in r.stdout, "passing check is recorded", r.stdout + r.stderr)
    check(not sb.ok(root), "a pass without a recorded validation plan is not enough")
    sb.lci(root, "auto")
    check(sb.ok(root), "1. passing evidence: gate allows the next stage")
    check(sb.hook(GATE_HOOK, "git push origin main", root) is None, "1. hook allows git push with evidence")
    r = sb.lci(root, "run", "--name", "unit", "--", unit)
    check("cached" in r.stdout and len(counter.read_text().splitlines()) == 1,
          "same check on unchanged content is not rerun", r.stdout)
    sb.lci(root / "sub", "run", "--name", "unit", "--", unit)
    check(len(counter.read_text().splitlines()) == 2, "the same command in another directory is a different check")

    flag = sb.base / "lint-fixed"
    lint = f"test -e {flag}"
    r = sb.lci(root, "run", "--name", "lint", "--", lint)
    check(r.returncode != 0 and "FAIL" in r.stdout, "failing check is recorded as a failure", r.stdout)
    check(not sb.ok(root), "2. failed required check: gate refuses despite another pass")
    check(sb.hook(GATE_HOOK, "git push origin main", root) == "deny", "2. hook denies git push after a failure")
    r = sb.lci(root, "unsupported", "--name", "lint", "--reason", "convenient")
    check(r.returncode == 1, "2. a failed check cannot be relabelled unsupported", r.stdout + r.stderr)
    sb.lci(root, "run", "--name", "lint", "--", "true")
    check(not sb.ok(root), "2. another command under the failed check's name does not clear it")
    flag.touch()
    sb.lci(root, "run", "--name", "lint", "--", lint)
    check(sb.ok(root), "the same check passing again clears its failure")

    (root / "a.txt").write_text("two\n")
    check(sb.ok(root), "uncommitted edit: HEAD (what a push sends) is still validated")
    sb.git(root, "commit", "-qam", "edit")
    check(not sb.ok(root), "3. committed change invalidates the old evidence")
    check(sb.hook(GATE_HOOK, "git push", root) == "deny", "3. hook denies push of unvalidated content")

    (root / "a.txt").write_text("three\n")
    (root / "new.txt").write_text("new\n")
    sb.validate(root)
    sb.git(root, "add", "-A")
    sb.git(root, "commit", "-qm", "validated work")
    check(sb.ok(root), "validated uncommitted work, committed whole: valid")

    (root / "a.txt").write_text("four\n")
    (root / "b.txt").write_text("b\n")
    sb.validate(root)
    sb.git(root, "commit", "-qam", "only a.txt")
    r = sb.lci(root, "gate")
    check(r.returncode == 1 and "untracked" in r.stdout,
          "3. a file present during validation but left out of the commit: stale, and says why", r.stdout)
    sb.git(root, "add", "b.txt")
    sb.git(root, "commit", "-qm", "b")
    check(sb.ok(root), "committing the rest makes HEAD the validated content")

    (root / "a.txt").chmod(0o755)
    sb.git(root, "commit", "-qam", "mode")
    check(not sb.ok(root), "3. a mode change is a content change")
    sb.validate(root)
    sb.git(root, "rm", "-q", "new.txt")
    sb.git(root, "commit", "-qm", "rm")
    check(not sb.ok(root), "3. a tracked deletion is a content change")
    (root / "link").symlink_to("a.txt")
    sb.validate(root)
    sb.git(root, "add", "link")
    sb.git(root, "commit", "-qm", "link")
    check(sb.ok(root), "a validated symlink, committed, matches")

    r = sb.lci(root, "run", "--name", "fixer", "--", "sh -c 'echo x >> a.txt'")
    check("CHANGED" in r.stdout and r.returncode != 0, "a check that modifies the tree is not a pass", r.stdout)
    sb.git(root, "checkout", "-q", "a.txt")
    check(not sb.ok(root), "a tree-modifying check blocks until it passes clean")

    procs = [subprocess.Popen([sys.executable, str(LOCAL_CI), "run", "--name", f"p{i}", "--", "true"], cwd=root,
                              env=sb.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(6)]
    for p in procs:
        p.wait(timeout=120)
    st = json.loads(sb.lci(root, "status", "--json").stdout)
    check(all(f"p{i}" in st["worktree"]["passes"] for i in range(6)), "concurrent checks lose no record",
          str(st["worktree"]["passes"]))

    lib = sb.repo("lib", {"l.txt": "1\n"})
    sup = sb.repo("super", {"a": "1\n"})
    sb.git(sup, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(lib), "lib")
    sb.git(sup, "commit", "-qm", "sub")
    (sup / "lib" / "l.txt").write_text("edited\n")
    sb.validate(sup)
    check(not sb.ok(sup), "3. uncommitted content inside a submodule is not what HEAD publishes")

    fm = sb.repo("filemode", {"run.sh": "echo 1\n"})
    sb.git(fm, "update-index", "--chmod=+x", "run.sh")
    sb.git(fm, "commit", "-qm", "exec")
    sb.git(fm, "config", "core.fileMode", "false")
    (fm / "run.sh").write_text("echo 2\n")
    sb.validate(fm)
    sb.git(fm, "commit", "-qam", "edit")
    check(sb.ok(fm), "core.fileMode=false: validated content keeps the index mode and stays valid")


def workflow_repo(sb: Sandbox, name: str) -> pathlib.Path:
    root = sb.repo(name, {".github/workflows/ci.yml": CI_YML, ".github/workflows/release.yml": RELEASE_YML,
                          ".github/workflows/docs.yml": DOCS_YML, "package.json": '{"scripts": {"test": "node t.js"}}',
                          "src/x.js": "1\n"})
    sb.git(root, "switch", "-qc", "feature")
    (root / "src" / "x.js").write_text("2\n")
    return root


def edit(root: pathlib.Path, n: int) -> None:
    (root / "src" / "x.js").write_text(f"{n}\n")


def scenario_act(sb: Sandbox) -> None:
    """4-5: Docker missing or down, unsupported and unsafe jobs, genuine vs environmental failure."""
    root = workflow_repo(sb, "gha")
    r = sb.lci(root, "act")
    check(r.returncode == 3 and "act is not installed" in r.stdout, "4. act missing: reported unavailable, exit 3", r.stdout)
    check("docker CLI is not installed" in r.stdout, "4. docker missing: reported", r.stdout)
    st = json.loads(sb.lci(root, "status", "--json").stdout)
    check(any(u["name"] == "act:ci.yml:test" for u in st["worktree"]["unsupported"]) and not st["worktree"]["blocking"],
          "4. unavailable act is recorded unsupported, never as a failure")
    check(not st["worktree"]["ok"], "4. unsupported evidence alone never makes content publishable")

    sb.stub("act", ACT_STUB)
    sb.stub("docker", DOCKER_STUB)
    r = sb.lci(root, "act")
    check(r.returncode == 3 and "Docker daemon is not running" in r.stdout, "4. Docker daemon down: unavailable", r.stdout)
    check(not sb.act_calls(), "4. act is not started without a reachable daemon")

    plan = json.loads(sb.lci(root, "plan", "--json").stdout)
    jobs = {j["id"]: j for w in plan["workflows"] if w["file"] == "ci.yml" for j in w["jobs"]}
    check(jobs["test"]["status"] == "runnable", "5. plain Linux job is runnable", str(jobs["test"]))
    check(jobs["mac"]["status"] == "unsupported" and "Linux" in jobs["mac"]["reasons"][0], "5. macOS job: unsupported")
    check(jobs["integration"]["status"] == "unsupported" and "API_KEY" in jobs["integration"]["reasons"][0],
          "5. job needing secrets: unsupported, secret named")
    check(jobs["deploy"]["status"] == "unsafe", "5. environment/deploy job: unsafe, never run")
    check(jobs["pkg"]["status"] == "unsafe" and any("publish" in x for x in jobs["pkg"]["reasons"]), "5. publish step: unsafe")
    check(jobs["smoke"]["status"] == "unsafe" and "needs `pkg`" in jobs["smoke"]["reasons"][0],
          "5. a job needing an unsafe job is unsafe (act -j runs its needs)", str(jobs["smoke"]))
    check(jobs["test"]["commands"] == ["npm test"], "workflow check commands extracted, setup skipped", str(jobs["test"]["commands"]))
    wfs = {w["file"]: w for w in plan["workflows"]}
    check(wfs["release.yml"]["event"] is None and "release" in wfs["release.yml"]["relevance"], "5. release-only workflow skipped")
    check(not wfs["docs.yml"]["relevant"] and wfs["ci.yml"]["relevant"], "paths filter: unaffected workflow not selected")
    r = sb.lci(root, "act", "--workflow", "ci.yml", "--job", "deploy", "--list")
    check("skip  ci.yml:deploy - unsafe" in r.stdout and "run   ci.yml:deploy" not in r.stdout,
          "5. naming an unsafe job explicitly still does not run it", r.stdout)

    sb.mode("docker", "up")
    sb.mode("act", "pass")
    sb.mode("help", "old")
    (sb.home / ".actrc").write_text("-s NPM_TOKEN=from-users-actrc --privileged\n")
    r = sb.lci(root, "act")
    check(r.returncode == 3 and "refusing" in r.stdout and not sb.act_calls(),
          "a user actrc with content is refused (act reads it whatever HOME is)", r.stdout)
    (sb.home / ".actrc").write_text("# comments only\n")
    r = sb.lci(root, "act")
    calls = sb.act_calls()
    check("db - `db` sets container volumes/options" in r.stdout and not any("-j db" in c for c in calls),
          "an act that cannot restrict container mounts skips jobs that set them", r.stdout)
    check("after-db - `db` sets" in r.stdout and not any("-j after-db" in c for c in calls),
          "...and jobs that need them, which act -j would run too", r.stdout)
    check(r.returncode == 0 and "PASS" in r.stdout, "act job success is recorded as a pass", r.stdout)
    check(len(calls) == 1 and "-j test" in calls[0], "only relevant, runnable jobs are run", str(calls))
    a = calls[0].split()
    check(a[0] == "pull_request", "event: pull_request when the workflow has it", calls[0])
    check("--secret-file" in a and "--env-file" in a and "--var-file" in a and "--container-daemon-socket -" in calls[0],
          "act gets empty secret/env/var files and no Docker socket", calls[0])
    check("GITHUB_TOKEN=" in a and a[a.index("GITHUB_TOKEN=") - 1] == "-s",
          "act gets an empty GITHUB_TOKEN: no fallback to gh's login, public actions still clone", calls[0])
    check("--pull=false" in a and "ubuntu-latest=catthehacker/ubuntu:act-latest" in calls[0],
          "default image mapping and no forced pull without an actrc", calls[0])
    arm = platform.machine().lower() in ("arm64", "aarch64")
    check(("--container-architecture linux/amd64" in calls[0]) == arm, "linux/amd64 containers exactly on ARM hosts")
    env = (sb.stubs / "act.env").read_text()
    check("sentinel" not in env, "tokens and cloud credentials never reach act's environment")
    seen = dict(line.split("=", 1) for line in env.splitlines() if "=" in line)
    check(all(seen.get(v, "").startswith(str(sb.base)) and not seen[v].startswith(str(sb.home))
              for v in ("HOME", "XDG_CONFIG_HOME", "GH_CONFIG_DIR")),
          "act runs with a throwaway HOME, XDG config and gh config: no user actrc, no stored login",
          str({v: seen.get(v) for v in ("HOME", "XDG_CONFIG_HOME", "GH_CONFIG_DIR")}))
    (sb.home / ".actrc").unlink()
    check("Partial evidence" in r.stdout, "a passing act run is reported as partial evidence")
    r = sb.lci(root, "act")
    check("cached" in r.stdout and len(sb.act_calls()) == 1, "a passed job is not rerun for unchanged content")
    sb.lci(root, "act", "--event", "push", "--job", "test")
    check(len(sb.act_calls()) == 2 and sb.act_calls()[-1].startswith("push"),
          "a pass under one event is not reused for another")
    sb.mode("docker", "down")
    sb.lci(root, "act", "--job", "test")
    st = json.loads(sb.lci(root, "status", "--json").stdout)
    check("act:ci.yml:test" in st["worktree"]["passes"]
          and not any(u["name"] == "act:ci.yml:test" for u in st["worktree"]["unsupported"]),
          "act becoming unavailable later does not erase a pass", str(st["worktree"]))
    sb.mode("docker", "up")

    sb.mode("help", "new")
    edit(root, 3)
    sb.lci(root, "act", "--job", "db")
    check("--container-options-policy restrict" in sb.act_calls()[-1], "mount-setting jobs run with options restricted")

    edit(root, 4)
    sb.mode("act", "fail")
    r = sb.lci(root, "act", "--job", "test")
    check(r.returncode == 1 and "FAIL" in r.stdout and "npm test" in r.stdout, "5. genuine step failure: FAIL", r.stdout)
    st = json.loads(sb.lci(root, "status", "--json").stdout)
    check("act:ci.yml:test" in st["worktree"]["blocking"], "act failure blocks publishing")
    sb.mode("docker", "down")
    sb.lci(root, "act", "--job", "test")
    st = json.loads(sb.lci(root, "status", "--json").stdout)
    check("act:ci.yml:test" in st["worktree"]["blocking"], "an act failure stays blocking when act later becomes unavailable")
    sb.mode("docker", "up")

    for n, (mode, want, what) in enumerate([
            ("infra", 3, "5. environment failure before any step: unsupported, not a test failure"),
            ("both", 1, "5. a step failure next to an environmental line is still a FAIL"),
            ("noop", 3, "act exiting 0 with no job run: unsupported, not a pass"),
            ("depok", 3, "only a dependency succeeded (the job itself skipped): not a pass"),
            ("invalid", 1, "an invalid workflow is a failure, not unsupported")], start=5):
        edit(root, n)
        sb.mode("act", mode)
        r = sb.lci(root, "act", "--job", "test")
        check(r.returncode == want, what, r.stdout)

    calls = len(sb.act_calls())
    (root / ".actrc").write_text("$NOPE-P ubuntu-latest=-self-hosted\n")
    edit(root, 20)
    r = sb.lci(root, "act", "--job", "test")
    check(r.returncode == 3 and "refusing" in r.stdout and len(sb.act_calls()) == calls,
          "a repository .actrc, which act applies to every run, is refused", r.stdout)
    (root / ".actrc").unlink()
    r = sb.lci(root, "act", "--job", "test", "--platform", "ubuntu-latest=-self-hosted")
    check(r.returncode == 2 and len(sb.act_calls()) == calls, "--platform never accepts -self-hosted", r.stderr)
    sb.mode("act", "pass")
    sb.lci(root, "act", "--job", "test", "--platform", "ubuntu-latest=node:20-bookworm")
    last = sb.act_calls()[-1]
    check("ubuntu-latest=node:20-bookworm" in last and "ubuntu-latest=catthehacker" not in last,
          "--platform chooses the image", last)
    calls = len(sb.act_calls())
    (root / ".git" / "info").mkdir(exist_ok=True)
    (root / ".git" / "info" / "exclude").write_text(".env\n")
    (root / ".env").write_text("API_KEY=x\n")
    edit(root, 22)
    r = sb.lci(root, "act", "--job", "test")
    check(r.returncode == 3 and ".env" in r.stdout and len(sb.act_calls()) == calls,
          "a secret ignored only outside .gitignore (act would copy it) is refused", r.stdout)
    (root / ".env").unlink()

    cl = sb.repo("classify", {".github/workflows/more.yaml": MORE_YAML})
    jobs = {j["id"]: j for w in json.loads(sb.lci(cl, "plan", "--json").stdout)["workflows"] for j in w["jobs"]}
    expect = {"lint": "runnable", "rel": "unsafe", "perms": "unsafe", "tf": "unsafe", "bump": "unsafe",
              "reuse": "unsupported", "selfhosted": "unsupported", "dyn": "unsupported"}
    got = {k: jobs.get(k, {}).get("status") for k in expect}
    check(got == expect, "5. .yaml workflow, shorthand forms, and each unsafe/unsupported form classified", str(got))


def scenario_stacks(sb: Sandbox) -> None:
    """6: projects without GitHub Actions use their own local checks; act is not required."""
    py = sb.repo("py", {"pyproject.toml": '[project]\nname = "x"\ndependencies = []\n[dependency-groups]\n'
                                          'dev = ["ruff", "pyright", "pytest"]\n[tool.ruff]\nline-length = 100\n',
                        "uv.lock": "", "tests/test_x.py": "def test_x():\n    pass\n"})
    plan = json.loads(sb.lci(py, "plan", "--json").stdout)
    cmds = [c for s in plan["checks"] for c in s["commands"]]
    check({"uv run ruff check .", "uv run pyright", "uv run pytest -q"} <= set(cmds), "6. python/uv commands from config", str(cmds))
    check(plan["workflows"] == [], "6. no workflows: none reported")
    r = sb.lci(py, "act")
    check(r.returncode == 3 and "act is not needed" in r.stdout, "6. act not required without workflows", r.stdout)

    bare = sb.repo("bare-py", {"pyproject.toml": '[project]\nname = "y"\n'})
    cmds = [c for s in json.loads(sb.lci(bare, "plan", "--json").stdout)["checks"] for c in s["commands"]]
    check(cmds == [], "6. no tool configured: no command invented", str(cmds))

    js = sb.repo("js", {"package.json": json.dumps({"scripts": {"lint": "eslint .", "typecheck": "tsc --noEmit",
                                                                 "test": "vitest", "build": "vite build"}}),
                        "pnpm-lock.yaml": ""})
    stack = json.loads(sb.lci(js, "plan", "--json").stdout)["checks"][0]
    check(stack["commands"] == ["pnpm run lint", "pnpm run typecheck", "pnpm run test", "pnpm run build"],
          "6. package manager and scripts from the repository", str(stack["commands"]))
    check(any("watch" in n for n in stack["notes"]), "6. watch-mode test script flagged")

    go = sb.repo("go", {"go.mod": "module x\n\ngo 1.23\n", "main.go": "package main\n",
                        "Makefile": "check:\n\tgo vet ./...\nother:\n\ttrue\n"})
    cmds = [c for s in json.loads(sb.lci(go, "plan", "--json").stdout)["checks"] for c in s["commands"]]
    check("go test ./..." in cmds and "go vet ./..." in cmds and "make check" in cmds and "make other" not in cmds,
          "6. go and Makefile check targets", str(cmds))

    tf = sb.repo("tf", {"main.tf": 'terraform {}\n', "Dockerfile": "FROM scratch\n"})
    cmds = [c for s in json.loads(sb.lci(tf, "plan", "--json").stdout)["checks"] for c in s["commands"]]
    check(any("fmt -check" in c for c in cmds) and not any("apply" in c for c in cmds), "6. terraform: validate, never apply", str(cmds))
    check("docker build -f Dockerfile ." in cmds, "6. Dockerfile build listed", str(cmds))


def scenario_git_hooks(sb: Sandbox) -> None:
    """7: existing hooks and hooksPath preserved and still run; pre-push gate enforces agent pushes."""
    custom = sb.repo("custom", {"a": "1\n"})
    marker = sb.base / "custom-hook-ran"
    existing = custom / ".git" / "hooks" / "pre-push"
    text = f"#!/bin/sh\ntouch {marker}\nexit 0\n"
    existing.write_text(text)
    existing.chmod(0o755)
    r = sb.lci(custom, "hook", "install")
    check(r.returncode == 3 and existing.read_text() == text, "7. existing pre-push hook left untouched", r.stdout)
    remote = sb.base / "custom-remote.git"
    sb.git(sb.base, "init", "-q", "--bare", str(remote))
    sb.git(custom, "remote", "add", "origin", str(remote))
    sb.git(custom, "push", "-q", "origin", "main")
    check(marker.exists(), "7. the repository's own pre-push hook still runs")

    hp = sb.repo("hookspath", {"a": "1\n"})
    sb.git(hp, "config", "core.hooksPath", ".husky")
    r = sb.lci(hp, "hook", "install")
    check(r.returncode == 3 and "core.hooksPath" in r.stdout and not (hp / ".husky").exists()
          and not (hp / ".git" / "hooks" / "pre-push").exists(), "7. core.hooksPath respected; nothing written", r.stdout)
    check(sb.git(hp, "config", "core.hooksPath").stdout.strip() == ".husky", "7. core.hooksPath value unchanged")

    root = sb.repo("pushing", {"a": "1\n"})
    remote = sb.base / "remote.git"
    sb.git(sb.base, "init", "-q", "--bare", str(remote))
    sb.git(root, "remote", "add", "origin", str(remote))
    r = sb.lci(root, "hook", "install")
    hook = root / ".git" / "hooks" / "pre-push"
    check(r.returncode == 0 and str(LOCAL_CI) in hook.read_text(), "pre-push gate installs, pointing at this local-ci")
    agent = {"CLAUDECODE": "1", "LOCAL_CI_BIN": ""}
    r = sb.git(root, "push", "-q", "origin", "main", extra=agent)
    check(r.returncode != 0 and "blocked" in r.stderr, "7. agent push without evidence rejected by git itself", r.stderr)
    r = sb.git(root, "push", "-q", "origin", "main", extra={"LOCAL_CI_ENFORCE": "1"})
    check(r.returncode != 0, "LOCAL_CI_ENFORCE=1 enforces outside agent sessions")
    r = sb.git(root, "push", "-q", "origin", "main")
    check(r.returncode == 0, "human push (no CLAUDECODE) unaffected", r.stderr)
    sb.validate(root)
    (root / "a").write_text("2\n")
    sb.git(root, "commit", "-qam", "two")
    r = sb.git(root, "push", "-q", "origin", "main", extra=agent)
    check(r.returncode != 0, "7. evidence for an older commit does not cover a newer one")
    sb.validate(root)
    r = sb.git(root, "push", "-q", "origin", "main", extra=agent)
    check(r.returncode == 0, "agent push with evidence for the pushed commit accepted", r.stderr)
    sb.git(root, "switch", "-qc", "wip")
    (root / "a").write_text("3\n")
    sb.git(root, "commit", "-qam", "wip")
    sb.git(root, "switch", "-q", "main")
    r = sb.git(root, "push", "-q", "origin", "wip", extra=agent)
    check(r.returncode != 0, "7. pushing an unvalidated branch other than HEAD is rejected")
    sb.git(root, "push", "-q", "origin", "main:gone")
    r = sb.git(root, "push", "-q", "origin", ":gone", extra=agent)
    check(r.returncode == 0, "deletion-only push is not gated", r.stderr)

    spaced = sb.base / "dir with space"
    spaced.mkdir()
    shutil.copy(LOCAL_CI, spaced / "local-ci")
    sp = sb.repo("spaced-repo", {"a": "1\n"})
    sb.git(sp, "remote", "add", "origin", str(remote))
    sb.run([sys.executable, str(spaced / "local-ci"), "hook", "install"], sp)
    r = sb.git(sp, "push", "-q", "origin", "main:spaced", extra=agent)
    check(r.returncode != 0 and "blocked" in r.stderr, "the pre-push hook finds a local-ci installed under a path with spaces",
          r.stderr)

    check(sb.hook(NO_VERIFY_HOOK, "git push --no-verify", root) == "deny", "7. no-verify guard still denies")
    check(sb.hook(IAC_HOOK, "terraform apply -auto-approve", root) == "deny", "7. IaC guard still denies")


# (expected decision, command, where): "v" runs in a validated repository whose `wip` branch and
# `v0` tag are not validated; "u" in an unvalidated one. {other} is the unvalidated repository.
GATE_TABLE = [
    ("deny", "git push", "u"),
    ("deny", "git push -u origin feature", "u"),
    ("deny", "git -C {other} push origin HEAD:main", "v"),
    ("deny", "cd {other} && git push", "v"),
    ("deny", 'bash -lc "cd {other} && git push origin main"', "v"),
    ("deny", "sudo -u me timeout 60 git -C {other} push", "v"),
    ("deny", "FOO=1 env git -C {other} push --force-with-lease", "v"),
    ("deny", "echo $(git -C {other} push)", "v"),
    ("deny", "git --git-dir={other}/.git push", "v"),
    (None, "git --work-tree {other} push", "v"),
    ("deny", "(cd {valid} && ls) && git push", "u"),
    ("deny", "pushd {valid}; popd; git push", "u"),
    ("deny", "gh\tpr create --fill", "u"),
    ("deny", "git push origin wip", "v"),
    ("deny", "git push origin wip:main", "v"),
    ("deny", "git push --all origin", "v"),
    ("deny", "git push origin :", "v"),
    ("deny", "git push --tags", "v"),
    ("deny", "gh pr create --fill", "u"),
    ("deny", "gh pr ready 12", "u"),
    ("deny", "gh pr update-branch 12", "u"),
    ("deny", "gh workflow run ci.yml --ref main", "u"),
    ("deny", "gh -R owner/repo run rerun 123 --failed", "u"),
    ("deny", "gh release create v1.0.0", "u"),
    ("deny", "gh api -X POST repos/o/r/actions/workflows/ci.yml/dispatches -f ref=main", "u"),
    ("deny", "gh api -X PUT repos/o/r/pulls/3/update-branch", "u"),
    ("deny", "gh api -X POST repos/o/r/actions/runs/9/rerun-failed-jobs", "u"),
    (None, "git push", "v"),
    (None, "git push origin main", "v"),
    (None, 'bash -lc "git push origin main"', "v"),
    (None, "git push origin HEAD:refs/heads/topic", "v"),
    (None, "git push origin main 2>&1 | tail -5", "v"),
    (None, "git push origin main >/dev/null 2>&1", "v"),
    (None, "git push 1>out origin main", "v"),
    ("deny", "git push origin wip 2>&1", "v"),
    (None, "git push --dry-run", "u"),
    (None, "git push -n origin main", "u"),
    (None, "git push origin :old-branch", "u"),
    (None, "git push --delete origin old", "u"),
    (None, "gh pr ready 12 --undo", "u"),
    (None, "gh pr view 12", "u"),
    (None, "gh run list", "u"),
    (None, "git status && git log --grep push", "u"),
    (None, 'echo "git push"', "u"),
    (None, "git commit -F - <<'EOF'\nfix: then git push and gh pr create\nEOF", "u"),
    (None, "ls  # git push later", "u"),
]


def scenario_gate_table(sb: Sandbox) -> None:
    """Command classification and target: wrappers looked through, the right repo and refs checked."""
    valid = sb.repo("table", {"a": "1\n"})
    other = sb.repo("other", {"b": "1\n"})
    sb.git(valid, "switch", "-qc", "wip")
    (valid / "a").write_text("2\n")
    sb.git(valid, "commit", "-qam", "wip")
    sb.git(valid, "tag", "v0")
    sb.git(valid, "switch", "-q", "main")
    sb.validate(valid)
    for want, cmd, where in GATE_TABLE:
        cwd = valid if where == "v" else other
        got = sb.hook(GATE_HOOK, cmd.format(other=other, valid=valid), cwd)
        check(got == want, f"gate [{where}]: {cmd!r} -> {want}", f"got {got}")

    outside = sb.base / "not-a-repo"
    outside.mkdir()
    check(sb.hook(GATE_HOOK, "gh workflow run ci.yml -R o/r", outside) is None, "outside a git repo: no decision")
    check(sb.hook_out(GATE_HOOK, "git push", other, tool="Read") is None, "non-Bash tools are ignored")
    r = sb.run(["sh", str(GATE_HOOK)], other, stdin="not json push")
    check(r.returncode == 0 and not r.stdout.strip(), "unparseable payload: fails open silently")

    sb.validate(other)
    sb.lci(other, "unsupported", "--name", "e2e", "--reason", "needs staging credentials")
    out = sb.hook_out(GATE_HOOK, "git push", other) or {}
    check("permissionDecision" not in out and "e2e" in out.get("additionalContext", ""),
          "allowed push still surfaces unverified checks", str(out))

    copy = sb.base / "lonely-hooks"
    copy.mkdir()
    for f in ("local-ci-gate.sh", "local-ci-gate.py"):
        shutil.copy(REPO / "hooks" / f, copy / f)
    out = sb.hook_out(copy / "local-ci-gate.sh", "git push", valid) or {}
    check("scanner" in out.get("additionalContext", "") and "permissionDecision" not in out,
          "scanner missing: fails open, and says so", str(out))
    out = sb.run(["sh", str(GATE_HOOK)], other, extra={"LOCAL_CI_BIN": str(sb.base / "missing")},
                 stdin=json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push"}, "cwd": str(other)}))
    check("not installed" in out.stdout and "deny" not in out.stdout, "local-ci missing: fails open, and says so", out.stdout)


def scenario_installer(sb: Sandbox) -> None:
    """8: dry run writes nothing; a temporary-target install places working, executable files."""
    target = sb.base / "install" / ".claude"
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(target)], REPO)
    check(r.returncode == 0 and "DRY RUN" in r.stdout and not target.exists(), "8. dry run writes nothing", r.stdout[-300:])
    check("bin/local-ci" in r.stdout and "hooks/local-ci-gate.sh" in r.stdout, "8. dry run lists the new files")
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(target), "--apply"], REPO)
    check(r.returncode == 0, "8. temporary-target install succeeds", r.stdout[-300:])
    for rel in ("bin/local-ci", "hooks/local-ci-gate.sh", "hooks/local-ci-gate.py"):
        check(os.access(target / rel, os.X_OK), f"8. installed {rel} is executable")
    settings = json.loads((target / "settings.json").read_text())
    cmds = [h["command"] for e in settings["hooks"]["PreToolUse"] for h in e["hooks"]]
    check(any(c == f"{target}/hooks/local-ci-gate.sh" for c in cmds), "8. settings render the gate with absolute paths")
    repo = sb.repo("installed", {"a": "1\n"})
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push"}, "cwd": str(repo)})
    r = sb.run(["sh", str(target / "hooks" / "local-ci-gate.sh")], repo, stdin=payload, extra={"LOCAL_CI_BIN": ""})
    check('"deny"' in r.stdout, "8. installed hook finds the installed local-ci and denies", r.stdout)
    auto_hook = target / "hooks" / "local-ci-auto.sh"
    sb.run(["sh", str(auto_hook), "start"], repo, stdin=json.dumps({"session_id": "inst", "cwd": str(repo)}),
           extra={"LOCAL_CI_BIN": ""})
    (repo / "a").write_text("2\n")
    r = sb.run(["sh", str(auto_hook), "stop"], repo, stdin=json.dumps({"session_id": "inst", "cwd": str(repo)}),
               extra={"LOCAL_CI_BIN": ""})
    check('"block"' in r.stdout and f"{target}/bin/local-ci auto" in r.stdout,
          "8. installed Stop hook finds the installed local-ci on its own", r.stdout)
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(target)], REPO)
    check(r.returncode == 0 and "0 to add" in r.stdout, "8. re-running the dry run is idempotent", r.stdout[-200:])

    old = sb.base / "existing" / ".claude"
    old.mkdir(parents=True)
    (old / "settings.json").write_text('{"model": "mine"}\n')
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(old), "--apply"], REPO)
    check((old / "settings.json").read_text() == '{"model": "mine"}\n'
          and (old / "settings.claude-code-config-proposed.json").exists(),
          "8. an existing settings.json is never rewritten; a proposal is written beside it", r.stdout[-300:])


# act stub for the automatic flow: the job comes from `-j`, a job listed in act.fail fails, the
# matrix job reports one Linux leg passing and a macOS leg skipped, as act does.
ACT_AUTO_STUB = """#!/bin/sh
here=$(dirname "$0")
if [ "$1" = "--version" ]; then echo "act version 0.2.97"; exit 0; fi
if [ "$1" = "--help" ]; then echo "  --container-options-policy string"; exit 0; fi
printf '%s\\n' "$*" >> "$here/act.argv"
job=$(printf '%s\\n' "$*" | sed -n 's/.* -j \\([^ ]*\\) .*/\\1/p')
if grep -qx "$job" "$here/act.skip" 2>/dev/null; then echo "[CI/$job] skipping: if condition false"; exit 0; fi
if grep -qx "$job" "$here/act.edit" 2>/dev/null; then echo "edited by $job" >> edited-during-act.txt; fi
name=$job; [ -f "$here/act.label.$job" ] && name=$(cat "$here/act.label.$job")
if grep -qx "$job" "$here/act.fail" 2>/dev/null; then
  echo "[CI/$job]   ❌  Failure - Main ./scripts/ci-only.sh"; echo "[CI/$job] 🏁  Job failed"; exit 1
fi
if [ "$job" = matrix ]; then
  echo "[CI/matrix-1] 🏁  Job succeeded"; echo "[CI/matrix-2] Skipping unsupported platform -- Try running with -P macos-latest"
  exit 0
fi
echo "[CI/$name] 🏁  Job succeeded"
"""
# npm stub: logs `npm run <script>`; a script named in npm.fail fails.
NPM_STUB = """#!/bin/sh
here=$(dirname "$0")
printf '%s\\n' "$*" >> "$here/npm.argv"
printf '%s %s\\n' "${PWD##*/}" "$*" >> "$here/npm.where"
if grep -qx "$2" "$here/npm.fail" 2>/dev/null; then echo "npm: $2 failed"; exit 1; fi
if grep -qx "$2" "$here/npm.edit" 2>/dev/null; then date > generated-report.txt; fi
exit 0
"""
AUTO_YML = """name: CI
on:
  pull_request:
  push:
    branches: [main]
jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm test
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/ci-only.sh
  hidden:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
      - run: |
          npm ci
          ./scripts/ci-only.sh
  matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    steps:
      - run: npm test
  integration:
    runs-on: ubuntu-latest
    steps:
      - run: ./it.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}
  api:
    runs-on: ubuntu-latest
    steps:
      - run: gh api repos/o/r
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  image:
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t x .
  deploy:
    runs-on: ubuntu-latest
    environment: production
    needs: [unit]
    steps:
      - run: ./deploy.sh
"""
# a push without a filter runs it even though the pull_request filter does not match
BOTH_YML = """on:
  push:
  pull_request:
    paths: ['docs/**']
jobs:
  bothjob:
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/ci-only.sh
"""
# a flow sequence over several lines
FLOW_YML = """on:
  pull_request:
    paths: [
      'src/**',
      'lib/**'
    ]
jobs:
  flowjob:
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/ci-only.sh
"""
MANUAL_YML = """on: workflow_dispatch
jobs:
  manual:
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/ci-only.sh
"""
NAMES_YML = """on: [pull_request]
jobs:
  node-20:
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/ci-only.sh
  fmt:
    name: Lint / Format
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/ci-only.sh
"""
AUTO_HOOK = REPO / "hooks" / "local-ci-auto.sh"


def scenario_auto(sb: Sandbox) -> None:
    """Automatic flow: Stop asks for `local-ci auto` once per content, auto derives and runs the plan
    (repository checks, then act jobs), and only the complete plan makes content publishable."""
    sb.stub("act", ACT_AUTO_STUB)
    sb.stub("npm", NPM_STUB)
    sb.mode("docker", "up")
    for f in ("act.argv", "act.fail", "act.skip", "act.edit", "npm.argv", "npm.where", "npm.fail", "npm.edit"):
        (sb.stubs / f).unlink(missing_ok=True)

    def lines(f: str) -> list[str]:
        p = sb.stubs / f
        return p.read_text().splitlines() if p.exists() else []

    def session(action: str, root, sid: str = "s1", extra: dict | None = None, active: bool = False,
                file: str | None = None) -> dict | None:
        payload = json.dumps({"session_id": sid, "cwd": str(root), "hook_event_name": action.title(),
                              "stop_hook_active": active, "tool_name": "Edit",
                              "tool_input": {"file_path": file} if file else {}})
        r = sb.run(["sh", str(AUTO_HOOK), action], root, stdin=payload, extra=extra)
        return json.loads(r.stdout) if r.stdout.strip() else None

    def jobs_run() -> list[str]:
        return [c.split(" -j ")[1].split()[0] for c in lines("act.argv")]

    # hidden: its real check sits behind a setup line; bothjob: push has no filter; flowjob: a flow
    # sequence over several lines; matrix: not plain. manual (workflow_dispatch only) never runs.
    JOBS = ["bothjob", "e2e", "flowjob", "hidden", "matrix"]
    root = sb.repo("auto", {".github/workflows/ci.yml": AUTO_YML, ".github/workflows/release.yml": RELEASE_YML,
                            ".github/workflows/docs.yml": DOCS_YML, ".github/workflows/both.yml": BOTH_YML,
                            ".github/workflows/flow.yml": FLOW_YML, ".github/workflows/manual.yml": MANUAL_YML,
                            "scripts/ci-only.sh": "true\n",
                            "package.json": json.dumps({"scripts": {"lint": "eslint .", "test": "node t.js"}}),
                            "src/x.js": "1\n"})
    remote = sb.base / "auto-remote.git"
    sb.git(sb.base, "init", "-q", "--bare", str(remote))
    sb.git(root, "remote", "add", "origin", str(remote))
    sb.git(root, "push", "-q", "origin", "main")
    sb.git(root, "switch", "-qc", "feature")

    check(session("start", root) is None, "SessionStart records a baseline silently")
    check(session("stop", root) is None, "Stop when the session changed nothing: no request, no checks")
    edit(root, 2)
    out = session("stop", root) or {}
    reason = out.get("reason", "")
    check(out.get("decision") == "block" and f"{LOCAL_CI} auto" in reason,
          "1-2. Stop after a change blocks once and asks for `local-ci auto` - no skill or user command", str(out))
    check(not lines("npm.argv") and not lines("act.argv"), "12. the hooks never run a check themselves")
    out = session("stop", root) or {}
    check("decision" not in out and "not validated" in out.get("systemMessage", ""),
          "the same unvalidated content is not blocked twice (no stop loop); the user is told once", str(out))
    check(session("stop", root) is None, "...and after that the stop is silent")
    check(sb.hook(GATE_HOOK, "git push origin feature", root) == "deny", "unvalidated content: push denied")

    asked = re.search(r"`([^`]*/local-ci auto)`", reason)
    cmd = asked.group(1) if asked else "false"  # exactly what the Stop hook asked for
    r = sb.run(cmd.split(), root)
    check(r.returncode == 0, "1. `local-ci auto` passes when every required check passes", r.stdout + r.stderr)
    check(lines("npm.argv") == ["run lint", "run test"], "4. repository checks run, cheapest first",
          str(lines("npm.argv")))
    check(sorted(jobs_run()) == JOBS, "1/3. exactly the relevant, runnable, uncovered jobs run under act",
          str(jobs_run()))
    plan = json.loads(sb.lci(root, "plan", "--json").stdout)["validation"]
    why = {x["name"]: x["reason"] for x in plan["unsupported"] + plan["skipped"] + plan["remote_only"]}
    check("npm run test" in why.get("act:ci.yml:unit", ""),
          "3. a plain job running the same command as a local check is not run twice", str(why))
    check("API_KEY" in why.get("act:ci.yml:integration", "") and "GITHUB_TOKEN" in why.get("act:ci.yml:api", "")
          and "Docker socket" in why.get("act:ci.yml:image", ""),
          "9. credential-dependent and Docker-in-job jobs: unsupported, with the exact reason", str(why))
    check(any(x["name"] == "act:ci.yml:deploy" for x in plan["remote_only"])
          and any(x["name"] == "release.yml" for x in plan["remote_only"]),
          "9. deploy job and release-only workflow: remote only, never run", str(plan["remote_only"]))
    check("paths filter" in why.get("docs.yml", ""), "3. path filters: an unaffected workflow is skipped", str(why))
    check("push or pull request" in why.get("manual.yml", ""), "a workflow_dispatch-only workflow is not required", str(why))
    check(any(n.startswith("act:ci.yml:matrix") and "macOS" in r for n, r in why.items()),
          "matrix legs act cannot run (macOS) are reported unverified, not hidden in the pass", str(why))
    check(session("stop", root) is None, "Stop is silent once the content is validated")
    sb.git(root, "add", "-A")
    sb.git(root, "commit", "-qm", "feature")
    out = sb.hook_out(GATE_HOOK, "git push origin feature", root) or {}
    check("permissionDecision" not in out and "act:ci.yml:integration" in out.get("additionalContext", ""),
          "10/11. validated, committed content: push allowed, unsupported jobs named", str(out))
    r = sb.git(root, "push", "-q", "origin", "feature", extra={"CLAUDECODE": "1"})
    check(r.returncode == 0, "the push reaches the local bare remote", r.stderr)

    calls = len(lines("act.argv"))
    r = sb.run(cmd.split(), root)
    check(r.returncode == 0 and len(lines("act.argv")) == calls and len(lines("npm.argv")) == 2,
          "12. rerunning auto on unchanged content runs nothing again", r.stdout)

    edit(root, 3)
    (sb.stubs / "act.fail").write_text("e2e\n")
    session("start", root, sid="s2")
    check(session("stop", root, sid="s2") is None, "a new session starts from the content it finds")
    check((session("stop", root, sid="s1") or {}).get("decision") == "block",
          "the same session is asked again for content it changed after validating")
    r = sb.run(cmd.split(), root)
    check(r.returncode == 1 and "FAIL" in r.stdout and "act:ci.yml:e2e" in r.stdout,
          "4. a failing act job fails auto, named", r.stdout)
    sb.git(root, "commit", "-qam", "broken")
    check(sb.hook(GATE_HOOK, "git push origin feature", root) == "deny", "4. a failed required check blocks the push")
    r = sb.lci(root, "unsupported", "--name", "npm run lint", "--reason", "convenient")
    check(r.returncode == 1 and "required" in r.stderr, "7. a required, runnable check cannot be waived as unsupported",
          r.stderr)

    (sb.stubs / "act.fail").unlink()
    edit(root, 4)  # the fix
    before = len(lines("act.argv"))
    r = sb.run(cmd.split(), root)
    check(r.returncode == 0 and sorted(jobs_run()[before:]) == JOBS,
          "5. the fixed content is revalidated locally, act jobs included", r.stdout)
    edit(root, 5)
    check(not json.loads(sb.lci(root, "status", "--json").stdout)["worktree"]["ok"], "6. an edit after validation is stale")

    (sb.stubs / "npm.fail").write_text("lint\n")
    before = len(lines("act.argv"))
    r = sb.run(cmd.split(), root)
    check(r.returncode == 1 and "deferred" in r.stdout and len(lines("act.argv")) == before,
          "a failing local check defers the act jobs (minutes) until it passes", r.stdout)
    (sb.stubs / "npm.fail").unlink()
    sb.lci(root, "run", "--", "npm run lint")
    st = json.loads(sb.lci(root, "status", "--json").stdout)["worktree"]
    check(not st["ok"] and "npm run lint" in st["passes"] and any("act:ci.yml:e2e" in m for m in st["missing"]),
          "7. every other check passing is not enough: a required act job that never ran still blocks", str(st))

    sb.mode("docker", "down")
    edit(root, 6)
    r = sb.run(cmd.split(), root)
    check(r.returncode == 0 and "Docker daemon is not running" in r.stdout and len(lines("act.argv")) == before,
          "10. Docker down: act jobs reported unsupported, local checks still gate", r.stdout)
    sb.git(root, "commit", "-qam", "no docker")
    out = sb.hook_out(GATE_HOOK, "git push origin feature", root) or {}
    check("permissionDecision" not in out and "act:ci.yml:e2e" in out.get("additionalContext", ""),
          "10. the allowed push still names the jobs that could not run locally", str(out))
    sb.mode("docker", "up")
    (sb.stubs / "act").unlink()
    edit(root, 7)
    r = sb.run(cmd.split(), root)
    check(r.returncode == 0 and "act is not installed" in r.stdout, "10. act missing: reported, never a pass", r.stdout)
    st = json.loads(sb.lci(root, "status", "--json").stdout)["worktree"]
    check(not any(p.startswith("act:") for p in st["passes"]), "10. unsupported act jobs are never counted as passes")

    plain = sb.repo("auto-plain", {"package.json": json.dumps({"scripts": {"test": "node t.js"}}), "a.js": "1\n"})
    session("start", plain)
    (plain / "a.js").write_text("2\n")
    out = session("stop", plain) or {}
    calls = len(lines("act.argv"))
    asked = re.search(r"`([^`]*/local-ci auto)`", out.get("reason", ""))
    r = sb.run((asked.group(1) if asked else "false").split(), plain)
    check(out.get("decision") == "block" and r.returncode == 0 and "act:" not in r.stdout,
          "8. no workflows: the same automatic flow runs the repository's own checks, no act", r.stdout)
    check(len(lines("act.argv")) == calls, "8. act is not needed without workflows")

    shapes = sb.repo("auto-shapes", {".github/workflows/a.yml": "on: [\n  pull_request,\n  push\n]\njobs:\n  aj:\n"
                                     "    runs-on: ubuntu-latest\n    steps:\n      - run: ./x.sh\n",
                                     ".github/workflows/b.yml": "on:\n  push:\n    tags: ['v*']\n  pull_request:\n"
                                     "    paths: ['docs/**']\njobs:\n  bj:\n    runs-on: ubuntu-latest\n"
                                     "    steps:\n      - run: ./x.sh\n", "src/x.js": "1\n"})
    sb.git(shapes, "switch", "-qc", "f")
    (shapes / "src" / "x.js").write_text("2\n")
    wfs = {w["file"]: w for w in json.loads(sb.lci(shapes, "plan", "--json").stdout)["workflows"]}
    check(wfs["a.yml"]["event"] == "pull_request" and wfs["a.yml"]["relevant"],
          "an `on:` list written over several lines is read", str(wfs["a.yml"]["triggers"]))
    check(not wfs["b.yml"]["relevant"], "a tag-only push does not make a code change relevant", wfs["b.yml"]["relevance"])

    # a repository's reviewed declaration: read from the base branch, never from the change itself
    decl = {"checks": ["./scripts/verify.sh --repo-only"],
            "exclude": {"./scripts/verify.sh": "without --repo-only it verifies an installation, not the repository"}}
    dr = sb.repo("auto-declared", {"scripts/verify.sh": '#!/bin/sh\n[ "$1" = --repo-only ]\n', "a.txt": "1\n"})
    (dr / "scripts" / "verify.sh").chmod(0o755)
    sb.git(dr, "add", "-A")
    sb.git(dr, "commit", "-qm", "exec")
    sb.git(dr, "switch", "-qc", "f")
    (dr / ".local-ci.json").write_text(json.dumps(decl))
    plan = json.loads(sb.lci(dr, "plan", "--json").stdout)["validation"]
    check([r["label"] for r in plan["required"]] == ["./scripts/verify.sh"]
          and any(s["name"] == ".local-ci.json" and "once merged" in s["reason"] for s in plan["skipped"]),
          "a declaration added by the change itself does not govern that change", str(plan))
    sb.git(dr, "switch", "-q", "main")
    sb.git(dr, "add", "-A")
    sb.git(dr, "commit", "-qm", "declare")
    sb.git(dr, "switch", "-qc", "g")
    (dr / "a.txt").write_text("2\n")
    r = sb.lci(dr, "auto")
    plan = json.loads(sb.lci(dr, "plan", "--json").stdout)["validation"]
    check(r.returncode == 0 and [x["label"] for x in plan["required"]] == ["./scripts/verify.sh --repo-only"]
          and any(s["name"] == "./scripts/verify.sh" and "installation" in s["reason"] for s in plan["skipped"]),
          "a declaration on the base branch adds its checks and excludes a discovered one, with the reason", r.stdout)
    (dr / ".local-ci.json").write_text(json.dumps({"checks": [], "exclude": {"./scripts/verify.sh --repo-only": "x"}}))
    plan = json.loads(sb.lci(dr, "plan", "--json").stdout)["validation"]
    check([x["label"] for x in plan["required"]] == ["./scripts/verify.sh --repo-only"],
          "editing the declaration in the change cannot drop the checks the base branch declared", str(plan))
    sb.git(dr, "checkout", "-q", ".local-ci.json")
    sb.git(dr, "switch", "-q", "main")
    (dr / ".local-ci.json").write_text('{"exclude": {"./scripts/verify.sh": ""}}')
    sb.git(dr, "commit", "-qam", "bad")
    sb.git(dr, "switch", "-qc", "h")
    (dr / "a.txt").write_text("3\n")
    plan = json.loads(sb.lci(dr, "plan", "--json").stdout)["validation"]
    check([x["label"] for x in plan["required"]] == ["./scripts/verify.sh"]
          and any(s["name"] == ".local-ci.json" and "ignored" in s["reason"] for s in plan["skipped"]),
          "an exclusion without a reason makes the declaration invalid: ignored and reported", str(plan))

    gated = sb.repo("auto-gated", {".github/workflows/ci.yml": "on: [pull_request]\njobs:\n  gated:\n"
                                   "    if: github.ref == 'refs/heads/main'\n    runs-on: ubuntu-latest\n"
                                   "    steps:\n      - run: ./ci.sh\n", "Makefile": "check:\n\ttrue\n"})
    (sb.stubs / "act.skip").write_text("gated\n")
    sb.stub("make", "#!/bin/sh\nexit 0\n")
    sb.stub("act", ACT_AUTO_STUB)
    calls = len(lines("act.argv"))
    r = sb.lci(gated, "auto")
    check(len(lines("act.argv")) == calls + 1, "the gated job was handed to act")
    st = json.loads(sb.lci(gated, "status", "--json").stdout)["worktree"]
    check(r.returncode == 0 and st["ok"] and any(u["name"] == "act:ci.yml:gated" for u in st["unsupported"]),
          "a required job act did not run (its `if:` is false here) is reported unverified, not a permanent block",
          r.stdout + str(st))
    (sb.stubs / "act.skip").unlink()
    (sb.stubs / "make").unlink()

    py = sb.repo("auto-py", {"pyproject.toml": '[project]\nname = "x"\n[tool.ruff]\n', "uv.lock": ""})
    plan = json.loads(sb.lci(py, "plan", "--json").stdout)["validation"]
    check(not plan["required"] and any("uv" in u["reason"] for u in plan["unsupported"]),
          "a check whose tool is not installed is unsupported, not required and never a pass", str(plan))

    session("start", root, sid="s3")
    edit(root, 9)
    off = session("stop", root, sid="s3", extra={"LOCAL_CI_AUTO": "0"})
    check(off is None and (session("stop", root, sid="s3") or {}).get("decision") == "block",
          "LOCAL_CI_AUTO=0 turns the automatic request off (and only it)")
    outside = sb.base / "auto-outside"
    outside.mkdir()
    check(session("stop", outside, sid="s-out") is None, "outside a git repository: nothing")
    r = sb.run(["sh", str(AUTO_HOOK), "stop"], root, stdin="not json")
    check(r.returncode == 0 and not r.stdout.strip(), "unparseable payload: fails open silently")

    # job names: an id ending in -digits, a display name with a slash; then act editing the tree
    names = sb.repo("auto-names", {".github/workflows/ci.yml": NAMES_YML, "scripts/ci-only.sh": "true\n",
                                   "Makefile": "check:\n\ttrue\n"})
    (sb.stubs / "act.label.fmt").write_text("Lint / Format")
    sb.stub("make", "#!/bin/sh\n[ -e \"$(dirname \"$0\")/make.fail\" ] && exit 1\nexit 0\n")
    r = sb.lci(names, "auto")
    st = json.loads(sb.lci(names, "status", "--json").stdout)["worktree"]
    check(r.returncode == 0 and {"act:ci.yml:node-20", "act:ci.yml:fmt"} <= set(st["passes"]),
          "a job id ending in -digits and a job name with a slash are recognised as passing", r.stdout)
    (names / "a.txt").write_text("1\n")
    (sb.stubs / "act.edit").write_text("node-20\n")
    before_fp = json.loads(sb.lci(names, "status", "--json").stdout)["worktree"]["fp"]
    sb.lci(names, "auto")
    (names / "edited-during-act.txt").unlink()
    (sb.stubs / "act.edit").unlink()
    st = json.loads(sb.lci(names, "status", "--json").stdout)["worktree"]
    check(st["fp"] == before_fp and not st["ok"] and "act:ci.yml:node-20" in st["blocking"],
          "a tree changed during an act job: its result is not evidence for the content it started from", str(st))
    (names / ".actrc").write_text("-P ubuntu-latest=-self-hosted\n")
    calls = len(lines("act.argv"))
    r = sb.lci(names, "auto")
    check(len(lines("act.argv")) == calls and "will not start act here" in r.stdout,
          "9. auto refuses act for a repository .actrc too: unsupported, act never started", r.stdout)
    (names / ".actrc").unlink()
    (names / "a.txt").write_text("2\n")
    (sb.stubs / "make.fail").write_text("")
    sb.lci(names, "auto")  # the plan requires both jobs; act is deferred behind the failing check
    (sb.stubs / "make.fail").unlink()
    sb.lci(names, "run", "--", "make check")
    sb.mode("docker", "down")
    sb.lci(names, "act")  # act unavailable now: recorded unsupported, but the plan still requires the jobs
    sb.mode("docker", "up")
    st = json.loads(sb.lci(names, "status", "--json").stdout)["worktree"]
    check(not st["ok"] and any("node-20" in m for m in st["missing"]),
          "an unavailable `local-ci act` does not stand in for a required job the plan says can run", str(st))
    (sb.stubs / "act.label.fmt").unlink()

    # cheapest first across stacks, and a check that rewrites the tree during auto
    order = sb.repo("auto-order", {"package.json": json.dumps({"scripts": {"test": "node t.js"}}),
                                   "Makefile": "lint:\n\ttrue\n", "a.js": "1\n"})
    sb.stub("make", "#!/bin/sh\nprintf 'make %s\\n' \"$*\" >> \"$(dirname \"$0\")/npm.argv\"\nexit 0\n")
    before = len(lines("npm.argv"))
    r = sb.lci(order, "auto", "--plan-only")
    check(len(lines("npm.argv")) == before and not json.loads(sb.lci(order, "status", "--json").stdout)["worktree"]["planned"],
          "auto --plan-only runs and records nothing", r.stdout)
    sb.lci(order, "auto")
    check(lines("npm.argv")[before:] == ["make lint", "run test"], "4. cheapest first across stacks (lint before test)",
          str(lines("npm.argv")[before:]))
    (order / "a.js").write_text("2\n")
    (sb.stubs / "npm.edit").write_text("test\n")
    r = sb.lci(order, "auto")
    check(r.returncode == 1 and "modified the tree" in r.stdout, "a check that rewrites the tree leaves auto NOT VALIDATED",
          r.stdout)
    (sb.stubs / "npm.edit").unlink()
    (sb.stubs / "make").unlink()

    # monorepo: a manifest below the root, only where the change is; never fixtures, vendored code
    mono = sb.repo("auto-mono", {"web/package.json": json.dumps({"scripts": {"test": "x"}}), "web/a.js": "1\n",
                                 "api/package.json": json.dumps({"scripts": {"lint": "x"}}), "api/b.js": "1\n",
                                 "tests/fixtures/package.json": json.dumps({"scripts": {"test": "x"}}),
                                 "vendor/lib/package.json": json.dumps({"scripts": {"test": "x"}})})
    (mono / "web" / "a.js").write_text("2\n")
    (mono / "tests" / "fixtures" / "package.json").write_text(json.dumps({"scripts": {"test": "y"}}))
    (mono / "vendor" / "lib" / "package.json").write_text(json.dumps({"scripts": {"test": "y"}}))
    plan = json.loads(sb.lci(mono, "plan", "--json").stdout)["validation"]
    labels = [r["label"] for r in plan["required"]]
    check(labels == ["npm run test [in web]"], "monorepo: the changed package's own checks are required, in its directory",
          str(labels))
    before = len(lines("npm.where"))
    r = sb.lci(mono, "auto")
    check(r.returncode == 0 and lines("npm.where")[before:] == ["web run test"], "monorepo: auto runs them there", r.stdout)
    r = sb.run(["sh", "-c", f"cd web && {sys.executable} {LOCAL_CI} run -- npm run test && {sys.executable} {LOCAL_CI} "
                            "status --json"], mono)
    check(json.loads(r.stdout[r.stdout.index("{"):])["worktree"]["ok"],
          "a manual `local-ci run -- npm run test` (unquoted) in the package is the plan's check", r.stdout[-300:])
    shutil.rmtree(mono / "api")
    r = sb.lci(mono, "auto")
    check("Traceback" not in r.stderr, "a deleted package directory does not crash auto", r.stderr[-300:])

    # the Stop hook beyond the session's own directory, and loop bounds
    far = sb.repo("auto-far", {"package.json": json.dumps({"scripts": {"test": "x"}}), "a.js": "1\n"})
    lobby = sb.base / "auto-lobby"
    lobby.mkdir()
    session("start", lobby, sid="s5")
    before = len(lines("npm.argv"))
    session("touch", lobby, sid="s5", file=str(far / "a.js"))
    check(len(lines("npm.argv")) == before, "12. the per-edit hook only records a baseline; it runs no check")
    (far / "a.js").write_text("2\n")
    out = session("stop", lobby, sid="s5") or {}
    check(out.get("decision") == "block" and str(far) in out.get("reason", ""),
          "a repository edited from a session started outside it is still asked to validate", str(out))
    moved = sb.repo("auto-moved", {"package.json": json.dumps({"scripts": {"test": "x"}}), "a.js": "1\n"})
    (moved / "a.js").write_text("2\n")
    check(session("stop", moved, sid="s6") is None,
          "a repository the session only visited (the user's own changes in it) is never held")
    sb.git(moved, "commit", "-qam", "published")
    sb.git(sb.base, "init", "-q", "--bare", str(sb.base / "moved-remote.git"))
    sb.git(moved, "remote", "add", "origin", str(sb.base / "moved-remote.git"))
    session("start", moved, sid="s8")
    sb.git(moved, "push", "-q", "origin", "main")
    sb.git(moved, "switch", "-qc", "other")
    (moved / "b.js").write_text("1\n")
    sb.git(moved, "add", "b.js")
    sb.git(moved, "commit", "-qm", "b")
    sb.git(moved, "push", "-q", "origin", "other")
    check(session("stop", moved, sid="s8") is None,
          "content the session only checked out, already on a remote branch, is never held")
    sb.git(moved, "switch", "-q", "main")
    session("start", moved, sid="s7")
    held = []
    for n in range(5):
        (moved / "a.js").write_text(f"churn {n}\n")
        held.append((session("stop", moved, sid="s7", active=n > 0) or {}).get("decision") == "block")
    check(held == [True, True, True, False, False], "content that changes on every run cannot hold stops forever", str(held))
    (moved / "a.js").write_text("fresh\n")
    check((session("stop", moved, sid="s7") or {}).get("decision") == "block",
          "...and a new user turn is asked again")

    settings = json.loads((REPO / "config" / "settings.example.json").read_text())
    hooks = {ev: [h["command"] for e in entries for h in e["hooks"]] for ev, entries in settings["hooks"].items()}
    check(any("local-ci-auto.sh start" in c for c in hooks.get("SessionStart", []))
          and any("local-ci-auto.sh stop" in c for c in hooks.get("Stop", [])),
          "2. the settings wire the automatic trigger: no per-repository setup, no skill to remember")
    wired = sorted((ev, e.get("matcher", ""), h["command"].rsplit("/", 1)[-1]) for ev, entries in settings["hooks"].items()
                   for e in entries for h in e["hooks"] if "local-ci" in h["command"])
    check(wired == [("PreToolUse", "Bash", "local-ci-gate.sh"), ("PreToolUse", "Edit|Write|MultiEdit|NotebookEdit",
                                                                 "local-ci-auto.sh touch"),
                    ("SessionStart", "", "local-ci-auto.sh start"), ("Stop", "", "local-ci-auto.sh stop")],
          "12. local-ci hooks: the push gate, a baseline per edited repository, start and stop - no check per edit",
          str(wired))
    sb.stub("act", ACT_STUB)


# act stub for runner capabilities: a job prints act.out.<job> and exits act.rc.<job> (default 1) when
# that file exists, and otherwise succeeds.
ACT_CAP_STUB = """#!/bin/sh
here=$(dirname "$0")
if [ "$1" = "--version" ]; then echo "act version 0.2.97"; exit 0; fi
if [ "$1" = "--help" ]; then echo "  --container-options-policy string"; exit 0; fi
printf '%s\\n' "$*" >> "$here/act.argv"
job=$(printf '%s\\n' "$*" | sed -n 's/.* -j \\([^ ]*\\) .*/\\1/p')
if [ -f "$here/act.out.$job" ]; then cat "$here/act.out.$job"; exit "$(cat "$here/act.rc.$job" 2>/dev/null || echo 1)"; fi
echo "[CI/$job] 🏁  Job succeeded"
"""
# act's own exec of a JavaScript action's entry point, then the runner cannot find node: the step never ran.
NO_NODE = ("  🐳  docker exec cmd=[node /var/run/act/actions/a/dist/index.js] user= workdir=\n"
           '  | OCI runtime exec failed: exec failed: unable to start container process: exec: "node": executable file '
           "not found in $PATH\n")
NO_DOCKER = ("  | failed to connect to the docker API at unix:///var/run/docker.sock; check if the path is correct and if "
             "the daemon is running: dial unix /var/run/docker.sock: connect: no such file or directory\n"
             "  | make: *** [Makefile:63: db-down] Error 1\n")
NO_DAEMON = "  | Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?\n"
# The step ran and the code's own image lacks node: `docker compose exec app node` inside a run step.
APP_NO_NODE = ("  🐳  docker exec cmd=[bash -e /var/run/act/workflow/3] user= workdir=\n"
               '  | OCI runtime exec failed: exec failed: unable to start container process: exec: "node": executable '
               "file not found in $PATH\n")


def act_log(job: str, *steps: tuple[str, str | None]) -> str:
    """An act log: each (step, output) runs; output None passes, any other text fails the step."""
    out = []
    for step, text in steps:
        out.append(f"[CI/{job}] ⭐ Run {step}\n")
        if text is None:
            out.append(f"[CI/{job}]   ✅  Success - {step} [10ms]\n")
        else:
            out += [f"[CI/{job}]{line}\n" for line in text.splitlines()] + [f"[CI/{job}]   ❌  Failure - {step} [12ms]\n"]
    return "".join(out) + f"[CI/{job}] 🏁  Job failed\n"


CAP_YML = """name: CI
on:
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
      - run: ./ci/lint.sh
  unit:
    runs-on: ubuntu-latest
    steps:
      - run: ./ci/unit.sh
  stack:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
      - run: make test-all
  smoke:
    runs-on: ubuntu-latest
    steps:
      - run: ./dev/smoke.sh
  probe:
    runs-on: ubuntu-latest
    steps:
      - run: ./ci/probe.sh
  after-stack:
    runs-on: ubuntu-latest
    needs: [stack]
    steps:
      - run: ./ci/unit.sh
  boxed:
    runs-on: ubuntu-latest
    container:
      image: alpine:3
    steps:
      - run: ./ci/unit.sh
  db:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
    steps:
      - run: ./ci/unit.sh
"""
CAP_MAKEFILE = ("COMPOSE := docker compose\n\ntest-all: deps ## everything\n\tnpm test\n\n"
                "deps: check-tools\n\ncheck-tools:\n\t@$(COMPOSE) version >/dev/null\n\n"
                "test:\n\t@${DOCKER:-docker} compose -p proj up -d db && pytest\n")


def scenario_capabilities(sb: Sandbox) -> None:
    """Runner capabilities: Docker reached through make or scripts is never run against the developer's
    daemon, missing runner capabilities are unsupported (never a pass, never a failure), genuine
    failures stay failures, and old records are reread only from their own logs."""
    sb.stub("act", ACT_CAP_STUB)
    sb.stub("npm", NPM_STUB)
    sb.stub("docker", DOCKER_STUB)
    sb.mode("docker", "up")
    for f in [*sb.stubs.glob("act.out.*"), *sb.stubs.glob("act.rc.*"), sb.stubs / "act.argv", sb.stubs / "docker.argv",
              sb.stubs / "npm.fail", sb.stubs / "docker.containers", sb.stubs / "docker.volumes"]:
        f.unlink(missing_ok=True)
    make = shutil.which("make")
    if make and not (sb.stubs / "make").exists():
        (sb.stubs / "make").symlink_to(make)  # so `make test` is discovered as a check, never run here

    def jobs_run() -> list[str]:
        p = sb.stubs / "act.argv"
        return [c.split(" -j ")[1].split()[0] for c in (p.read_text().splitlines() if p.exists() else [])]

    def act_out(job: str, text: str | None, rc: int = 1) -> None:
        for name, value in ((f"act.out.{job}", text), (f"act.rc.{job}", None if text is None else str(rc))):
            if value is None:
                (sb.stubs / name).unlink(missing_ok=True)
            else:
                (sb.stubs / name).write_text(value)

    def status() -> dict:
        return json.loads(sb.lci(root, "status", "--json").stdout)["worktree"]

    def unverified() -> dict[str, str]:
        return {u["name"]: u["reason"] for u in status()["unsupported"]}

    script = "#!/bin/sh\ntrue\n"
    root = sb.repo("cap", {".github/workflows/ci.yml": CAP_YML, "Makefile": CAP_MAKEFILE,
                           "ci/lint.sh": script, "ci/unit.sh": script, "ci/probe.sh": script,
                           "dev/smoke.sh": "#!/bin/sh\nexec ./dev/inner.sh\n",
                           "dev/inner.sh": "#!/bin/sh\ndocker volume inspect proj_pgdata\n",
                           "package.json": json.dumps({"scripts": {"test": "node t.js"}}), "src/x.js": "1\n"})
    for s in ("ci/lint.sh", "ci/unit.sh", "ci/probe.sh", "dev/smoke.sh", "dev/inner.sh"):
        (root / s).chmod(0o755)
    sb.git(root, "add", "-A")
    sb.git(root, "commit", "-qm", "exec bits")

    # Plan: Docker reached only through a Makefile target or a script chain is not a runnable job.
    plan = json.loads(sb.lci(root, "plan", "--json").stdout)["validation"]
    why = {x["name"]: x["reason"] for x in plan["unsupported"]}
    req = [r["label"] for r in plan["required"]]
    check("make test-all -> deps -> check-tools" in why.get("act:ci.yml:stack", "")
          and "dev/inner.sh" in why.get("act:ci.yml:smoke", ""),
          "Docker reached through a make target or a script chain: unsupported, the chain named", str(why))
    check("npm run test" in why.get("act:ci.yml:stack", "") and "not for this job on GitHub" in why["act:ci.yml:stack"],
          "an unsupported job's command that also runs directly is named as direct evidence, not as the job",
          why.get("act:ci.yml:stack", ""))
    check({"act:ci.yml:lint", "act:ci.yml:unit", "act:ci.yml:probe", "npm run test"} <= set(req)
          and not {"act:ci.yml:stack", "act:ci.yml:smoke", "act:ci.yml:after-stack", "act:ci.yml:db"} & set(req),
          "jobs without Docker stay required; Docker jobs are not dropped silently but listed unsupported", str(req))
    check("Docker" in why.get("act:ci.yml:after-stack", ""),
          "a job that needs a Docker job (act -j runs both) is unsupported too", why.get("act:ci.yml:after-stack", ""))
    check("isolated network" in why.get("act:ci.yml:db", ""),
          "a job with service containers is unsupported: they need the host network", why.get("act:ci.yml:db", ""))
    check(make is None or ("starts Docker on this machine's daemon" in why.get("make test", "")
                           and "make test" not in req),
          "a discovered local check that starts Docker through its Makefile is not run on the developer's daemon",
          why.get("make test", ""))

    # Run: a normal job passes, Node missing in the runner and Docker missing in a step are unsupported.
    act_out("lint", act_log("lint", ("Main actions/setup-node@v4", NO_NODE), ("Main ./ci/lint.sh", None)))
    act_out("probe", act_log("probe", ("Main ./ci/probe.sh", NO_DAEMON), ("Post Upload artifacts", NO_NODE)))
    r = sb.lci(root, "auto")
    ran = jobs_run()
    check("stack" not in ran and "smoke" not in ran and not any("--docker-socket" in c or "daemon-socket -" not in c
                                                                for c in (sb.stubs / "act.argv").read_text().splitlines()),
          "a Docker-dependent job without isolation is never handed to act; no job gets the socket", str(ran))
    calls = (sb.stubs / "act.argv").read_text().splitlines()
    nets = {c.split("--network ")[1].split()[0] for c in calls if "--network " in c}
    dargv = (sb.stubs / "docker.argv").read_text()
    check(len(nets) == 1 and all("--network local-ci-" in c and "--add-host=host.docker.internal:127.0.0.1" in c
                                 for c in calls)
          and f"network create --driver bridge {next(iter(nets))}" in dargv and f"network rm {next(iter(nets))}" in dargv,
          "act jobs run on a network of their own (created, then removed), host aliases pointed at themselves",
          str(calls[:1]) + dargv)
    st = status()
    check("act:ci.yml:unit" in st["passes"], "a normal runnable act job passes", str(st))
    u = unverified()
    check("`node`" in u.get("act:ci.yml:lint", "") and "missing runner capability" in u["act:ci.yml:lint"]
          and "act:ci.yml:lint" not in st["blocking"] + st["passes"],
          "an act runner missing Node: unsupported with that reason, neither a failure nor a pass", str(u))
    check("Docker engine" in u.get("act:ci.yml:probe", "") and "act:ci.yml:probe" not in st["blocking"],
          "a step that needed Docker the job is not given: unsupported, not an application failure", str(u))
    check(r.returncode == 0 and st["ok"] and "npm run test" in st["passes"],
          "direct checks that ran keep their evidence; runnable required checks passed, so auto passes", r.stdout)
    shown = ("stack", "smoke", "lint", "probe", "after-stack", "db")
    check(all(f"unverified locally: act:ci.yml:{n} - " in r.stdout for n in shown) and "GitHub Actions" in r.stdout,
          "every unsupported job stays visible in the final report, GitHub Actions named as their check", r.stdout)
    sb.git(root, "commit", "-qam", "validated", "--allow-empty")
    out = sb.hook_out(GATE_HOOK, "git push origin HEAD", root) or {}
    ctx = out.get("additionalContext", "")
    check("permissionDecision" not in out and all(f"act:ci.yml:{n} (" in ctx for n in shown)
          and "GitHub Actions is their only verification" in ctx,
          "the push is allowed and names every job only GitHub Actions can verify", str(out))

    # --docker-socket is the user's explicit authorization, and still never the developer's own daemon.
    (sb.stubs / "docker.volumes").write_text("proj_pgdata\nact-toolcache\n")
    (sb.stubs / "docker.containers").write_text("proj-postgres-1\n")
    before = len(jobs_run())
    r = sb.lci(root, "act", "--job", "stack", "--docker-socket")
    check(len(jobs_run()) == before and r.returncode == 3 and "proj_pgdata" in r.stdout and "proj-postgres-1" in r.stdout,
          "--docker-socket on a daemon holding other containers/volumes: refused, they are named", r.stdout)
    r = sb.lci(root, "act", "--job", "unit", "--docker-socket")
    check(len(jobs_run()) == before and r.returncode == 3 and "would give this job the socket too" in r.stdout
          and "proj_pgdata" in r.stdout,
          "--docker-socket is refused for a job not known to use Docker too: the socket would reach it", r.stdout)
    (sb.stubs / "docker.volumes").write_text("act-portal_pgdata\n")
    r = sb.lci(root, "act", "--job", "unit", "--docker-socket")
    check(len(jobs_run()) == before and "act-portal_pgdata" in r.stdout,
          "a developer volume whose name merely starts with act- is not taken for act's own", r.stdout)
    r = sb.lci(root, "act", "--job", "stack")
    check(len(jobs_run()) == before and r.returncode == 3 and "never mounted automatically" in r.stdout,
          "`local-ci act` without --docker-socket does not run a Docker job either", r.stdout)
    (sb.stubs / "docker.psfail").write_text("")
    (sb.stubs / "docker.volumes").write_text("")
    r = sb.lci(root, "act", "--job", "stack", "--docker-socket")
    check(len(jobs_run()) == before and "could not be listed" in r.stdout,
          "a daemon whose containers cannot be listed is not taken for isolated", r.stdout)
    (sb.stubs / "docker.psfail").unlink()
    (sb.stubs / "docker.volumes").write_text("act-toolcache\n")
    (sb.stubs / "docker.containers").write_text("")
    r = sb.lci(root, "act", "--job", "stack", "--docker-socket")
    last = (sb.stubs / "act.argv").read_text().splitlines()[-1]
    check(jobs_run()[-1] == "stack" and "--container-daemon-socket" not in last,
          "--docker-socket on an isolated daemon (only act's own volumes): the job runs with the socket", last)

    # Genuine failures are never hidden behind a capability or an unsupported label.
    edit(root, 2)
    act_out("unit", act_log("unit", ("Main ./ci/unit.sh", "  | AssertionError: 1 failing\n"),
                            ("Main Stop containers", NO_DOCKER)))
    r = sb.lci(root, "auto")
    st = status()
    check(r.returncode == 1 and "act:ci.yml:unit" in st["blocking"],
          "a genuine test failure next to a Docker-less cleanup step is a failure and blocks", r.stdout)
    sb.git(root, "commit", "-qam", "broken")
    check(sb.hook(GATE_HOOK, "git push origin HEAD", root) == "deny", "the failing test blocks publication")
    act_out("unit", act_log("unit", ("Main ./ci/unit.sh", NO_NODE)))
    sb.lci(root, "act", "--job", "unit", "--force")
    check("act:ci.yml:unit" in status()["blocking"],
          "a later run that only lacks a runner capability does not clear a recorded failure")
    r = sb.lci(root, "unsupported", "--name", "act:ci.yml:unit", "--reason", "runner")
    check(r.returncode == 1 and "act:ci.yml:unit" in status()["blocking"],
          "a failed job cannot be relabelled unsupported by hand", r.stderr)
    r = sb.lci(root, "auto")
    check(r.returncode == 1 and "Read again" not in r.stdout,
          "a failure recorded by the current classifier is never reread into unsupported", r.stdout)
    for n, (out, what) in enumerate([
            (act_log("unit", ("Main ./ci/unit.sh", "  | FAILED tests/test_x.py::test_y - AssertionError\n" + NO_DAEMON)),
             "a genuine failure and a Docker-socket line in the same step: a failure"),
            (act_log("unit", ("Main ./ci/unit.sh", APP_NO_NODE)),
             "`node` missing inside the code's own container (the step ran): a failure, not the runner's"),
            (act_log("unit", ("Main ./ci/unit.sh", NO_DAEMON + "  ❗  ::error file=src/x.js,line=1::3 lint problems\n")),
             "an ::error annotation next to a Docker-socket line in the same step: a failure")], start=30):
        edit(root, n)
        act_out("unit", out)
        r = sb.lci(root, "act", "--job", "unit")
        check(r.returncode == 1 and "act:ci.yml:unit" in status()["blocking"], what, r.stdout)

    edit(root, 40)
    act_out("boxed", act_log("boxed", ("Main ./ci/unit.sh", NO_NODE.replace("node", "bash"))))
    (sb.stubs / "docker.netcontainers").write_text("act-CI-boxed-0123456789abcdef0123\n")
    (sb.stubs / "docker.argv").write_text("")
    r = sb.lci(root, "act", "--job", "boxed")
    dargv = (sb.stubs / "docker.argv").read_text()
    check(r.returncode == 1 and "act:ci.yml:boxed" in status()["blocking"],
          "a program missing from the job's own `container:` image is the workflow's failure, as on GitHub", r.stdout)
    check("rm -f act-CI-boxed-0123456789abcdef0123" in dargv
          and dargv.index("rm -f act-CI-boxed") < dargv.index("network rm local-ci-"),
          "a container left on the run's network (act killed at a timeout) is removed, then the network", dargv)
    (sb.stubs / "docker.netcontainers").unlink()
    act_out("boxed", None)

    # Records written before this classifier: reread from their own logs, and only capability-only ones.
    # Both jobs now only lack a runner capability, which on its own never clears a failure.
    edit(root, 3)
    act_out("unit", act_log("unit", ("Main ./ci/unit.sh", NO_NODE)))
    act_out("lint", act_log("lint", ("Main ./ci/lint.sh", NO_NODE)))
    ledger = sb.state / (hashlib.sha256(os.path.realpath(root).encode()).hexdigest()[:16] + ".jsonl")
    fp = status()["fp"]
    logs = sb.base / "legacy-logs"
    logs.mkdir()
    (logs / "cap.log").write_text(act_log("unit", ("Main ./ci/unit.sh", NO_DOCKER), ("Post setup", NO_NODE)))
    (logs / "real.log").write_text(act_log("lint", ("Main ./ci/lint.sh", "  | error: 3 problems\n")))
    with ledger.open("a") as fh:  # probe: by the current classifier; db: a timeout - neither is reread
        for job, log, extra in (("unit", "cap.log", {}), ("lint", "real.log", {}), ("probe", "cap.log", {"classifier": 2}),
                                ("db", "cap.log", {"exit": 124})):
            fh.write(json.dumps({"ts": time.time() - 60, "fp": fp, "name": f"act:ci.yml:{job}", "kind": "act",
                                 "status": "fail", "detail": "old", "exit": 1, "log": str(logs / log),
                                 "cmd": "event=pull_request", **extra}) + "\n")
    r = sb.lci(root, "auto")
    st = status()
    check("Read again" in r.stdout and "act:ci.yml:unit: recorded fail -> unsupported" in r.stdout
          and "act:ci.yml:unit" not in st["blocking"] + st["passes"] and "act:ci.yml:unit" in unverified(),
          "a pre-classifier failure whose log shows only missing capabilities is reread, visibly, to unsupported",
          r.stdout)
    check({"act:ci.yml:probe", "act:ci.yml:db"} <= set(st["blocking"]),
          "a failure recorded by the current classifier, or a timeout, is never reread", str(st["blocking"]))
    check("act:ci.yml:lint" in st["blocking"] and not st["ok"],
          "a pre-classifier failure with a genuine failing step is not reread; a capability-only rerun keeps it",
          str(st))

    # Evidence is for exactly one tree.
    edit(root, 4)
    act_out("lint", None)
    sb.lci(root, "auto")
    check(status()["ok"], "fresh content validated")
    sb.git(root, "add", "-A")
    sb.git(root, "commit", "-qm", "validated")
    sb.git(root, "switch", "-qc", "other")
    edit(root, 5)
    sb.git(root, "commit", "-qam", "other content")
    sb.git(root, "switch", "-q", "-")
    check(sb.ok(root) and not sb.ok(root, "--rev", "other"),
          "the gate does not accept one tree's evidence for another branch's tree")
    check(sb.hook(GATE_HOOK, "git push origin other", root) == "deny",
          "pushing the unvalidated branch is denied while HEAD is validated")
    edit(root, 6)
    check(not status()["ok"], "changed content invalidates the earlier validation")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="local-ci-test-") as tmp:
        sb = Sandbox(pathlib.Path(tmp).resolve())
        sb.stub("gh", GH_STUB)
        for scenario in (scenario_evidence, scenario_act, scenario_stacks, scenario_git_hooks,
                         scenario_gate_table, scenario_installer, scenario_auto, scenario_capabilities):
            if VERBOSE:
                print((scenario.__doc__ or "").splitlines()[0])
            try:
                scenario(sb)
            except Exception as e:  # a crash is a failed scenario, not a skipped one
                check(False, f"{scenario.__name__} raised {type(e).__name__}", str(e))
        # 9: the sandbox can reach nothing remote. Every push target was a local bare repository, git
        # refused non-file protocols, and gh/act/docker resolved only to the stubs.
        path = sb.env["PATH"]
        check(all(str(shutil.which(t, path=path) or "").startswith(str(sb.stubs)) for t in ("gh", "act", "docker")),
              "9. gh, act and docker resolve only to stubs inside the sandbox")
        remotes = [line.split()[1] for d in sb.base.iterdir() if (d / ".git").is_dir()
                   for line in sb.git(d, "remote", "-v").stdout.splitlines()]
        check(bool(remotes) and all(os.path.isabs(u) and os.path.isdir(u) for u in remotes),
              "9. every remote pushed to is a local bare repository", str(remotes))
        check(not (sb.stubs / "gh.argv").exists(), "9. gh was never invoked")
    failed = [r for r in results if not r[0]]
    if failed:
        print(f"{len(failed)} of {len(results)} local-ci checks failed")
        return 1
    print(f"all {len(results)} local-ci checks held")
    return 0


if __name__ == "__main__":
    sys.exit(main())
