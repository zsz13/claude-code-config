#!/usr/bin/env python3
"""Classifier for block-git-no-verify.sh. Reads the PreToolUse payload on stdin.

Denies git commands that bypass repository hooks:
  git [global opts] commit ... --no-verify | -n | -<bundle containing n>
  git [global opts] push|merge|rebase ... --no-verify
  git -c core.hooksPath=... <anything>
  git config [flags] core.hooksPath <value>     (setting it; --get/--unset are allowed)
Tokens are parsed with shlex per shell segment, so "-n" inside a quoted message
is not a flag. Anything unparseable or unrelated -> exit 0 (allow). Fails open.
"""
import json
import re
import shlex
import sys

SEG = re.compile(r"\|\||&&|\||;|\n|\(|\)|\$\(")
HOOKED = {"commit", "push", "merge", "rebase", "am", "cherry-pick", "revert"}
GLOBAL_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--config-env"}


def bypasses(seg: str) -> bool:
    try:
        toks = shlex.split(seg, posix=True)
    except ValueError:
        toks = seg.split()
    while toks and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in ("sudo", "command", "env", "time", "nice")):
        toks = toks[1:]
    if not toks or toks[0].rsplit("/", 1)[-1] != "git":
        return False
    i = 1
    # global options
    while i < len(toks) and toks[i].startswith("-"):
        t = toks[i]
        if t.startswith("-c") and "core.hookspath" in t.lower():
            return True
        if t in GLOBAL_WITH_ARG and i + 1 < len(toks):
            if t == "-c" and "core.hookspath" in toks[i + 1].lower():
                return True
            i += 2
            continue
        if t.startswith("--git-dir=") or t.startswith("--work-tree=") or t.startswith("-C"):
            i += 1
            continue
        i += 1
    if i >= len(toks):
        return False
    sub, rest = toks[i], toks[i + 1:]
    if sub == "config":
        flags = [r for r in rest if r.startswith("-")]
        if any(f.startswith(("--get", "--unset", "-l", "--list", "--show", "-e", "--edit")) for f in flags):
            return False
        return any(r.lower() == "core.hookspath" for r in rest)
    if sub not in HOOKED:
        return False
    for r in rest:
        if r == "--":
            break
        if r == "--no-verify":
            return True
        if sub == "commit" and re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", r) and not r.startswith("--"):
            return True
    return False


def main() -> None:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    if d.get("tool_name") != "Bash":
        return
    cmd = str((d.get("tool_input") or {}).get("command") or "")
    if "git" not in cmd:
        return
    for seg in SEG.split(cmd):
        if seg and bypasses(seg.strip()):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Blocked: this git command bypasses the repository's hooks (--no-verify / -n / core.hooksPath). "
                    "Quality gates are not skipped to get past a failing check: read the hook output, fix the cause "
                    "(or stage the files a fixer changed and rerun), then commit or push normally. If the hook itself is "
                    "broken or the user explicitly asked to bypass it, report why and ask the user to run the bypass "
                    "command themselves.")}}))
            sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        pass
    sys.exit(0)
