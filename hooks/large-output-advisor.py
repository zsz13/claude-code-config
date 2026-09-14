#!/usr/bin/env python3
"""Classifier for large-output-advisor.sh. Reads the PreToolUse payload on stdin.
Advisory only: prints a one-line additionalContext hint at most once per session per
command class, never blocks or rewrites. Fails open.

Hints point at ~/.claude/bin/run-captured (full output kept on disk, compact
summary + exit status in context) for commands whose raw output is large, and at
progressive narrowing for searches. They never suggest blind `| head` truncation
of search results."""
import json, re, sys, time
from pathlib import Path
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if d.get("tool_name") != "Bash":
    sys.exit(0)
cmd = str((d.get("tool_input") or {}).get("command") or "")
if not cmd:
    sys.exit(0)
if "run-captured" in cmd:
    sys.exit(0)  # already routed through the capture helper
piped = bool(re.search(r"\|(?!\|)", cmd)) or bool(re.search(r"(?<![0-9&<])>>?\s*[^&\s]", cmd))  # filtered or redirected to a file (2>&1 does not count)

V = r"(?:^|[;&|(]\s*|\$\(\s*)"  # a command verb: start of a segment, never mid-argument
RC = "~/.claude/bin/run-captured"

def has(*pats):
    return any(re.search(p, cmd, re.M) for p in pats)

cls = msg = None
if has(V + r"git\s+(diff|show)\b") and not piped and not has(r"--(stat|name-only|name-status|shortstat|numstat|dirstat)\b", r"\bgit\s+(diff|show)\b[^|]*\s--\s"):
    # a git diff/show with no explicit path after `--` and no summary flag
    if not re.search(r"\bgit\s+(diff|show)\b\S*(\s+-\S+)*\s+[^-\s][^\s]*[./][^\s]*", cmd):
        cls, msg = "git-diff", ("Large-output hint: `git status --short` / `git diff --stat` first, then `git diff -- <path>` for the files that matter. "
                                "Load the complete diff only for cross-file review; if it is too large, split it by file/subsystem (never drop a changed file).")
elif has(V + r"git\s+log\b") and not piped and not has(r"\s-n\s*\d+", r"\s-\d+\b", r"--max-count", r"--oneline", r"\s-[0-9]"):
    cls, msg = "git-log", "Large-output hint: bound history reads: `git log --oneline -n 20 [-- <path>] [--grep=<text>]`; `git show <sha>` only for the commits that matter."
elif has(V + r"(python3?\s+-m\s+)?pytest\b", V + r"uv\s+run\s+pytest\b") and not piped and not has(r"\s-q\b", r"--tb=", r"\s-x\b", r"::"):
    cls, msg = "pytest", (f"Large-output hint: `{RC} -- <pytest cmd> -q -ra --tb=short` keeps the exit status, every failing test name, and the full log on disk "
                          "while only the summary enters context. On failure rerun just the failing tests with `--lf --tb=long` (or `-x`).")
elif has(V + r"(npm|pnpm|yarn|bun)\s+(run\s+)?test\b", V + r"(npx\s+)?(jest|vitest)\b", V + r"go\s+test\b", V + r"cargo\s+test\b", V + r"(mvn|gradle|\./gradlew)\s+test\b") and not piped:
    cls, msg = "tests", (f"Large-output hint: verbose test runners can emit thousands of lines. Run `{RC} -- <test cmd>` (full log kept on disk, exit status "
                         "and failures summarised) with the runner's quiet reporter; rerun only failing specs verbosely when diagnosing.")
elif has(V + r"docker(\s+compose)?\s+logs\b") and not has(r"--tail", r"--since", r"\s-n\s*\d+") and not piped:
    cls, msg = "docker-logs", ("Large-output hint: `docker logs --since 10m <c> 2>&1 | grep -nE 'error|warn|<request-id>'` or `--tail 200`; expand around matching "
                               "lines. Do not rely on `tail` alone when the failure may be earlier in the log.")
elif has(V + r"(terraform|tofu)\s+plan\b") and not piped and not has(r"-out="):
    cls, msg = "tf-plan", (f"Large-output hint: `{RC} --match 'Plan:|No changes|^  # ' -- terraform plan -no-color` keeps terraform's exit status and the whole "
                           "plan on disk while surfacing the summary and resource headers; open specific resources from that file. Never paste state or secrets into context.")
elif has(V + r"pip3?\s+(list|freeze)\b", V + r"npm\s+(ls|list)\b", V + r"pnpm\s+(ls|list)\b", V + r"yarn\s+list\b", V + r"cargo\s+tree\b", V + r"go\s+list\s+\./\.\.\.") and not piped:
    cls, msg = "deps", "Large-output hint: filter dependency listings to the package in question (`| grep -i <pkg>`, `npm ls <pkg>`, `uv tree --package <pkg>`) instead of loading the whole tree."
elif has(V + r"ls\s+-[a-zA-Z]*R\b", V + r"tree\b", V + r"find\s+\.?\s*$", V + r"find\s+\.\s+-type\s+[fd]\s*$") and not piped and not has(r"\s-L\s*\d"):
    cls, msg = "recursive-ls", ("Large-output hint: prefer `git ls-files [<dir>]`, Glob, or `tree -L 2 -I 'node_modules|.venv|dist|build|.git'` over a recursive listing; "
                                "Graphify/LSP locate code faster than a directory dump.")
elif has(V + r"(rg|grep\s+-[a-zA-Z]*[rR])\s") and not piped and not has(r"\s-(l|c|L)\b", r"--(files-with-matches|count|files|json)\b", r"\s--\s") \
        and not re.search(r"\s(-[a-zA-Z]+\s+)*(['\"][^'\"]+['\"]|\S+)\s+[^\s-][^\s]*[/.][^\s]*\s*$", cmd):
    # pattern search whose target is the whole tree (no path after the pattern)
    cls, msg = "broad-search", ("Search hint: when a pattern may match widely, get the shape first: `rg -c <pat>` (per-file counts) or `rg -l <pat>`, then `rg -n <pat> <files>` "
                                "for the relevant files, scoping by type/path (`-t py`, `-g '!**/tests/**'`). Never `| head` a search (it hides matches). "
                                "For a known symbol use LSP references; for a subsystem question use `graphify query`.")
elif has(V + r"docker\s+(build|compose\s+build)\b", V + r"(npm|pnpm|yarn|bun)\s+(run\s+)?build\b", V + r"(npx\s+)?vite\s+build\b", V + r"cargo\s+build\b", V + r"(mvn|gradle|\./gradlew)\s+(build|package|assemble)\b") and not piped:
    cls, msg = "build", f"Large-output hint: `{RC} -- <build cmd>` keeps the complete build log on disk and puts only exit status, errors/warnings, and the summary in context."
elif has(V + r"pip3?\s+install\b", V + r"(npm|pnpm|yarn|bun)\s+(install|ci|add)\b") and not piped and not has(r"\s-q\b", r"--quiet", r"--silent"):
    cls, msg = "pkg-install", f"Large-output hint: package installs are verbose; add the manager's quiet flag or run `{RC} -- <install cmd>` so only errors/warnings and the result enter context."

if not cls:
    sys.exit(0)
sid = re.sub(r"[^A-Za-z0-9_-]", "", str(d.get("session_id") or "nosession"))[:40]
state = Path.home() / ".cache" / "claude-hooks" / "large-output"
try:
    state.mkdir(parents=True, exist_ok=True)
    marker = state / f"{sid}-{cls}"
    if marker.exists():
        sys.exit(0)
    marker.touch()
    cutoff = time.time() - 7 * 86400
    for p in state.iterdir():
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink()
        except Exception:
            pass
except Exception:
    pass
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}}))
