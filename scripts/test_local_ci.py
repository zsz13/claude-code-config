#!/usr/bin/env python3
"""Regression scenarios for bin/local-ci, hooks/local-ci-gate.sh and the installer's handling of them.

Every scenario runs in throwaway git repositories under a temporary directory with an isolated HOME,
git config, state directory and PATH. `act`, `docker` and `gh` are stubs that log how they were
called; pushes go only to a local bare repository (GIT_ALLOW_PROTOCOL=file), so nothing here can
reach GitHub or start a real workflow. Run by scripts/verify.sh.

Usage: python3 scripts/test_local_ci.py [-v]
Exit:  0 = every check held, 1 = at least one did not.
"""
import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import tempfile

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
if [ "$(cat "$here/docker.mode" 2>/dev/null)" = up ]; then echo "29.0.0 x86_64"; exit 0; fi
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


def scenario_evidence(sb: Sandbox) -> None:
    """1-3: a pass allows publishing, a failure blocks it, changed content makes evidence stale."""
    root = sb.repo("evidence", {"a.txt": "one\n", "sub/k.txt": "k\n"})
    check(not sb.ok(root), "no evidence: gate refuses")
    counter = sb.base / "unit-runs"
    unit = f"echo run >> {counter}"
    r = sb.lci(root, "run", "--name", "unit", "--", unit)
    check(r.returncode == 0 and "PASS" in r.stdout, "passing check is recorded", r.stdout + r.stderr)
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
    sb.lci(root, "run", "--", "true")
    sb.git(root, "add", "-A")
    sb.git(root, "commit", "-qm", "validated work")
    check(sb.ok(root), "validated uncommitted work, committed whole: valid")

    (root / "a.txt").write_text("four\n")
    (root / "b.txt").write_text("b\n")
    sb.lci(root, "run", "--", "true")
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
    sb.lci(root, "run", "--", "true")
    sb.git(root, "rm", "-q", "new.txt")
    sb.git(root, "commit", "-qm", "rm")
    check(not sb.ok(root), "3. a tracked deletion is a content change")
    (root / "link").symlink_to("a.txt")
    sb.lci(root, "run", "--", "true")
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
    sb.lci(sup, "run", "--", "true")
    check(not sb.ok(sup), "3. uncommitted content inside a submodule is not what HEAD publishes")

    fm = sb.repo("filemode", {"run.sh": "echo 1\n"})
    sb.git(fm, "update-index", "--chmod=+x", "run.sh")
    sb.git(fm, "commit", "-qm", "exec")
    sb.git(fm, "config", "core.fileMode", "false")
    (fm / "run.sh").write_text("echo 2\n")
    sb.lci(fm, "run", "--", "true")
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
    sb.lci(root, "run", "--", "true")
    (root / "a").write_text("2\n")
    sb.git(root, "commit", "-qam", "two")
    r = sb.git(root, "push", "-q", "origin", "main", extra=agent)
    check(r.returncode != 0, "7. evidence for an older commit does not cover a newer one")
    sb.lci(root, "run", "--", "true")
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
    sb.lci(valid, "run", "--", "true")
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

    sb.lci(other, "run", "--", "true")
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
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(target)], REPO)
    check(r.returncode == 0 and "0 to add" in r.stdout, "8. re-running the dry run is idempotent", r.stdout[-200:])

    old = sb.base / "existing" / ".claude"
    old.mkdir(parents=True)
    (old / "settings.json").write_text('{"model": "mine"}\n')
    r = sb.run(["bash", str(REPO / "scripts" / "install.sh"), "--target", str(old), "--apply"], REPO)
    check((old / "settings.json").read_text() == '{"model": "mine"}\n'
          and (old / "settings.claude-code-config-proposed.json").exists(),
          "8. an existing settings.json is never rewritten; a proposal is written beside it", r.stdout[-300:])


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="local-ci-test-") as tmp:
        sb = Sandbox(pathlib.Path(tmp).resolve())
        sb.stub("gh", GH_STUB)
        for scenario in (scenario_evidence, scenario_act, scenario_stacks, scenario_git_hooks,
                         scenario_gate_table, scenario_installer):
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
