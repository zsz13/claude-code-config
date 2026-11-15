#!/usr/bin/env python3
"""Classifier for local-ci-gate.sh. Reads the PreToolUse payload on stdin.

Denies a command that publishes work or starts remote CI while the content it publishes has no
passing local validation recorded by `local-ci` (~/.claude/bin/local-ci):
  git [global opts] push ...            (not --dry-run/-n, not a deletion-only push)
  gh pr create | pr ready | pr update-branch | workflow run | run rerun | release create
  gh api <...>/dispatches|update-branch|rerun|rerun-failed-jobs
`push --all|--mirror|--tags` and the matching refspec `:` check every branch or tag they send.
The commits checked are the push's source refs (default HEAD); `local-ci gate` compares their tree
content with the recorded evidence, so evidence for older content never counts.

Shell text is read with skill-install-guard.py's scanner: here-doc bodies and comments are data,
quoted mentions are not commands, wrappers (sudo, env, timeout, xargs, ...), `sh -c` strings,
$(...) and `cd`/`pushd`/`git -C`/`--git-dir` directories are looked through. It is not a sandbox: a
script file or a command built at run time is not read. The opt-in git pre-push hook (`local-ci hook
install`) also sees a push started from a script, while CLAUDECODE is set in the agent's environment.

Allowed with no decision: everything else, a command outside a git work tree, and any error
(missing local-ci or scanner, timeout) - fails open, with a one-line note when it could not decide.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_CI = os.environ.get("LOCAL_CI_BIN") or os.path.join(os.path.dirname(HERE), "bin", "local-ci")
GIT_GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}
PUSH_WITH_ARG = {"-o", "--push-option", "--receive-pack", "--exec", "--repo"}
GH_GLOBAL_WITH_ARG = {"-R", "--repo", "--hostname"}
API_PUBLISH = ("/dispatches", "/update-branch", "/rerun", "/rerun-failed-jobs")
GH_PUBLISH = {("pr", "create"), ("pr", "ready"), ("pr", "update-branch"), ("workflow", "run"),
              ("run", "rerun"), ("release", "create")}


def load_scanner():
    spec = importlib.util.spec_from_file_location("skill_install_guard", os.path.join(HERE, "skill-install-guard.py"))
    if spec is None or spec.loader is None:
        raise ImportError("skill-install-guard.py not found beside this hook")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_push(args: list[str], cwd: str, sg) -> tuple[str, list[str]] | None:
    """(directory, revs) for a `git push`; "refs/heads/" or "refs/tags/" stands for every ref under it."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        a = args[i]
        flag, eq, val = a.partition("=")
        if not eq and flag in GIT_GLOBAL_WITH_ARG and i + 1 < len(args):
            val = args[i + 1]
        if flag == "-C" and val:
            cwd = sg.resolve(cwd, val)
        elif flag == "--git-dir" and val:  # --work-tree alone does not change which repository is pushed
            gd = sg.resolve(cwd, val).rstrip("/")
            cwd = os.path.dirname(gd) if os.path.basename(gd) == ".git" else gd
        if not eq and flag in GIT_GLOBAL_WITH_ARG:
            i += 2
            continue
        i += 1
    if i >= len(args) or args[i] != "push":
        return None
    rest, pos, j = args[i + 1:], [], 0
    while j < len(rest):
        a = rest[j]
        if a == "--":
            pos += rest[j + 1:]
            break
        if a in ("-n", "--dry-run", "-d", "--delete") or (a.startswith("-") and not a.startswith("--") and "n" in a[1:]):
            return None
        if a in PUSH_WITH_ARG:
            j += 2
            continue
        if not a.startswith("-"):
            pos.append(a)
        j += 1
    refspecs, revs = pos[1:], []
    for spec in refspecs:
        spec = spec.lstrip("+")
        if spec == ":":
            revs.append("refs/heads/")  # "matching": every branch the remote also has
        elif spec.split(":", 1)[0]:
            revs.append(spec.split(":", 1)[0])
    if {"--all", "--mirror", "--branches"} & set(rest):
        revs.append("refs/heads/")
    if {"--tags", "--mirror"} & set(rest):
        revs.append("refs/tags/")
    if refspecs and not revs:
        return None  # deletions only (":branch")
    return cwd, revs or ["HEAD"]


def gh_publish(args: list[str]) -> str | None:
    pos, i = [], 0
    while i < len(args):
        a = args[i]
        if a in GH_GLOBAL_WITH_ARG:
            i += 2
            continue
        if not a.startswith("-"):
            pos.append(a)
        i += 1
    if tuple(pos[:2]) in GH_PUBLISH and not (pos[:2] == ["pr", "ready"] and "--undo" in args):
        return f"gh {pos[0]} {pos[1]}"
    hit = next((e for e in API_PUBLISH for a in args if a.rstrip("/").endswith(e)), None) if pos[:1] == ["api"] else None
    if hit:
        return f"gh api ...{hit}"
    return None


def targets(cmd: str, sg, depth: int = 0) -> list[tuple[str, str, list[str]]]:
    """(label, directory, revs) for every publishing command in a shell command line."""
    code, scripts, _ = sg.scan(cmd)
    # The scanner keeps a redirect's file descriptor (`2>&1`, `1>out`) as an argument, where it would
    # read as a refspec; a number attached to `<`/`>` at the start of a word is never one.
    code = re.sub(r"(?<![^\s;&|()])\d+(?=[<>])", "", code)
    out = []
    for script in scripts if depth < 3 else []:
        out += targets(script, sg, depth + 1)
    # A `cd` inside ( ... ) or undone by `popd` does not outlast it, but segments() flattens both; when
    # either is present the session's own directory is checked as well, so a push cannot hide behind one.
    cwd, stack = "", []
    nested = "(" in code or "popd" in code
    for argv, _ in sg.segments(code):
        argv = sg.effective_argv(argv)
        if not argv:
            continue
        head, args = os.path.basename(argv[0]), argv[1:]
        if head == "popd":
            cwd = stack.pop() if stack else ""
        elif head in ("cd", "pushd"):
            if head == "pushd":
                stack.append(cwd)
            cwd = sg.resolve(cwd, next((a for a in args if not a.startswith("-")), "~"))
        elif head in sg.SHELLS and depth < 3:
            k = next((k for k, a in enumerate(args[:-1]) if sg.SHELL_C.fullmatch(a)), None)
            if k is not None:
                out += [(lbl, d if os.path.isabs(os.path.expanduser(d)) else os.path.join(cwd, d), revs)
                        for lbl, d, revs in targets(args[k + 1], sg, depth + 1)]
        elif head == "git":
            hit = git_push(args, cwd, sg)
            if hit:
                out.append(("git push", hit[0], hit[1]))
                if nested and hit[0]:
                    out.append(("git push", "", hit[1]))
        elif head == "gh":
            label = gh_publish(args)
            if label:
                out.append((label, cwd, ["HEAD"]))
                if nested and cwd:
                    out.append((label, "", ["HEAD"]))
    return out


def gate(directory: str, revs: list[str]) -> dict | None:
    cmd = [sys.executable, LOCAL_CI, "gate", "--json"]
    for r in revs:
        cmd += ["--rev", r]
    r = subprocess.run(cmd, cwd=directory, capture_output=True, text=True, timeout=50)
    if r.returncode == 2 and not r.stdout.strip():
        return None  # not a git work tree: nothing local to validate
    return json.loads(r.stdout)


def emit(**out) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **out}}))


def main() -> None:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    if d.get("tool_name") != "Bash":
        return
    cmd = str((d.get("tool_input") or {}).get("command") or "")
    base = str(d.get("cwd") or os.getcwd())
    try:
        sg = load_scanner()
    except Exception:
        if any(w in cmd for w in ("push", "gh ")):
            emit(additionalContext="local-ci-gate could not load skill-install-guard.py's shell scanner, so this "
                                   "command was not checked for local validation evidence. Validate locally before "
                                   "publishing; reinstall the hooks component to restore the gate.")
        return
    try:
        found = targets(cmd, sg)
    except Exception:
        return
    notes = []
    for label, rel, revs in found:
        directory = os.path.normpath(os.path.join(base, os.path.expanduser(rel)))
        if not os.path.isfile(LOCAL_CI):
            emit(additionalContext=f"local-ci-gate: {LOCAL_CI} is not installed, so `{label}` was not checked "
                                   "for local validation evidence. Validate locally before publishing.")
            return
        try:
            res = gate(directory if os.path.isdir(directory) else base, revs)
        except Exception as e:
            emit(additionalContext=f"local-ci-gate could not decide for `{label}` ({type(e).__name__}); "
                                   "confirm local validation passed before publishing.")
            return
        if res is None:
            continue
        if not res.get("ok"):
            lines = []
            for r in res.get("revs", []):
                lines.append(f"{r['rev']} (tree {r['fp'][:12]}): {r['why']}")
            emit(permissionDecision="deny", permissionDecisionReason=(
                f"Blocked: `{label}` publishes work or starts remote CI, and local validation has not passed "
                f"for the content it would publish - {'; '.join(lines)}. Remote CI is final verification, not "
                f"a debugger. Run `{LOCAL_CI} auto` in that repository: it derives the validation plan (the "
                "repository's own checks, then the affected GitHub Actions jobs under act) and runs every required "
                "check that has not passed for this content. Fix failures and rerun it until it exits 0, commit "
                "exactly what was validated, then retry once. If the user explicitly wants to publish without local "
                "validation, they run the command themselves. (local-ci-gate)"))
            return
        for r in res.get("revs", []):
            for u in r.get("unsupported", []):
                notes.append(f"{u['name']} ({u['reason']})")
    if notes:
        emit(additionalContext="local-ci: validated locally, but these checks did not run here, so GitHub Actions is "
                               "their only verification - report them as unverified and confirm they pass remotely "
                               "before merging: " + "; ".join(dict.fromkeys(notes)))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
