#!/usr/bin/env python3
"""PreToolUse(Grep|Glob|Bash): lazy, adaptive Graphify bootstrap. FAILS OPEN.

Fires only when Claude is about to do a broad, repository-wide search. Then:
  - not a git repo / graphify missing / HOME as root  -> allow silently
  - graphify-out/graph.json exists                     -> nudge once per session to query it
  - no graph: count tracked source files (+LOC if small); if the repo is large
    enough, build once (code-only, offline, no viz), install graphify's
    incremental git hooks, keep tracked files untouched, exclude graphify-out/
    locally. Decisions are cached so the common path costs a few milliseconds.
Any error, timeout, or parse failure -> exit 0 with no output. Never blocks.
Recursion guards: GRAPHIFY_HOOK_ACTIVE=1, commands mentioning graphify, a lock file.
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

MIN_FILES = 50            # tracked source files
MIN_LOC = 10_000          # tracked source lines (only counted when files < MIN_FILES)
MAX_AUTO_FILES = int(os.environ.get("GRAPHIFY_HOOK_MAX_AUTO_FILES", "6000"))
TOTAL_BUDGET = 150        # seconds; registered hook timeout is 180
BUILD_TIMEOUT = 90        # `graphify extract`
STEP_TIMEOUT = 25         # cluster / hook install
SMALL_TTL = 6 * 3600      # re-count a "too small" repo after this (or when HEAD changes)
FAIL_TTL = 24 * 3600      # do not retry a failed build for this long
LOCK_STALE = 600          # a lock older than this is considered abandoned
STATE_DIR = Path.home() / ".cache" / "claude-hooks" / "graphify"
T0 = time.monotonic()

SRC_EXT = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts",
    ".go", ".rs", ".java", ".kt", ".kts", ".c", ".cc", ".cpp", ".cxx", ".h", ".hh",
    ".hpp", ".cs", ".rb", ".php", ".swift", ".scala",
}
EXCLUDE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "dist", "build", "target", "coverage",
    ".coverage", "htmlcov", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__",
    ".cache", ".next", ".nuxt", ".turbo", ".parcel-cache", "vendor", "graphify-out",
    ".gitnexus", "site-packages", ".tox", ".idea", ".vscode",
}
LLM_ENV_KEYS = (
    "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY",
    "MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT",
    "OLLAMA_BASE_URL", "OLLAMA_HOST", "AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION",
    "GRAPHIFY_API_KEY",
)
SEARCH_VERBS = {"rg", "grep", "egrep", "fgrep", "find", "fd", "fdfind", "tree", "ls"}
# split a shell command into segments; remember whether a segment consumes a pipe
SEG_SPLIT = re.compile(r"(\|\||&&|\||;|\n|\(|\)|\$\()")


def remaining() -> float:
    return TOTAL_BUDGET - (time.monotonic() - T0)


def emit(msg: str) -> None:
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}
    }))
    sys.stdout.flush()


def run(cmd, cwd=None, timeout=10, env=None):
    """Run with a hard timeout; kill the whole process group on expiry."""
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, start_new_session=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except Exception:
            p.kill()
        try:
            p.communicate(timeout=5)
        except Exception:
            pass
        raise
    return subprocess.CompletedProcess(cmd, p.returncode, out, err)


def git_root(cwd: str):
    try:
        r = run(["git", "-C", cwd, "rev-parse", "--show-toplevel"], timeout=5)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    root = r.stdout.strip()
    return Path(root) if root else None


def git_head(root: Path) -> str:
    try:
        r = run(["git", "-C", str(root), "rev-parse", "HEAD"], timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


# ---------------------------------------------------------------- classifier
def _is_root_target(target, cwd: str, root: Path) -> bool:
    """True when `target` (None, '.', or a path) denotes the repository root."""
    if target in (None, "", ".", "./"):
        try:
            return Path(cwd).resolve() == root.resolve()
        except Exception:
            return False
    try:
        p = Path(os.path.expanduser(target))
        if not p.is_absolute():
            p = Path(cwd) / p
        return p.resolve() == root.resolve()
    except Exception:
        return False


def _bash_segment_is_broad(seg: str, cwd: str, root: Path) -> bool:
    try:
        toks = shlex.split(seg, posix=True)
    except ValueError:
        toks = seg.split()
    # strip env assignments and wrappers
    while toks and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in ("sudo", "command", "time", "nice")):
        toks = toks[1:]
    if not toks:
        return False
    verb = os.path.basename(toks[0])
    args = toks[1:]
    if verb == "git":
        # git [-C dir] grep ...
        i = 0
        while i < len(args) and args[i].startswith("-"):
            i += 2 if args[i] in ("-C", "-c") else 1
        if i >= len(args) or args[i] != "grep":
            return False
        verb, args = "git-grep", args[i + 1:]
    if verb not in SEARCH_VERBS and verb != "git-grep":
        return False
    if verb == "grep" and not any(re.match(r"^-[a-zA-Z]*[rR]", a) or a in ("--recursive", "--dereference-recursive") for a in args):
        return False
    if verb == "ls" and not any(re.match(r"^-[a-zA-Z]*R", a) for a in args):
        return False
    # positional arguments (very rough: drop options; for grep-likes drop the pattern)
    positional = []
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "--":
            continue
        if a.startswith("-") and a != "-":
            if a in ("-e", "-f", "-g", "--glob", "-t", "--type", "-E", "--extension", "-name", "-iname",
                     "-path", "-type", "-maxdepth", "-mindepth", "-L", "-I", "-P", "--pattern"):
                skip = True
            continue
        positional.append(a)
    if verb in ("rg", "grep", "egrep", "fgrep", "git-grep", "fd", "fdfind"):
        has_pattern_flag = any(a in ("-e", "--regexp") or a.startswith(("-e", "--regexp=")) for a in args)
        if not has_pattern_flag and positional:
            positional = positional[1:]      # first positional is the pattern
    if verb == "find":
        # find [paths...] [expression]; expression starts at the first token beginning with '-' or '(' or '!'
        positional = []
        for a in args:
            if a.startswith(("-", "(", "!")):
                break
            positional.append(a)
    if not positional:
        return _is_root_target(None, cwd, root)
    return any(_is_root_target(p, cwd, root) for p in positional)


def is_broad(tool: str, ti: dict, cwd: str, root: Path) -> bool:
    if tool == "Grep":
        return _is_root_target(ti.get("path"), cwd, root)
    if tool == "Glob":
        pat = str(ti.get("pattern") or "")
        return "**" in pat and _is_root_target(ti.get("path"), cwd, root)
    if tool == "Bash":
        cmd = str(ti.get("command") or "")
        if "graphify" in cmd or "gitnexus" in cmd:
            return False
        parts = SEG_SPLIT.split(cmd)
        prev_op = None
        for part in parts:
            if part in ("||", "&&", "|", ";", "\n", "(", ")", "$("):
                prev_op = part
                continue
            seg = part.strip()
            if not seg:
                continue
            if prev_op == "|":          # consumer of a pipe: bounded by its input
                prev_op = None
                continue
            prev_op = None
            if _bash_segment_is_broad(seg, cwd, root):
                return True
        return False
    return False


# ---------------------------------------------------------------- counting
def tracked_source_files(root: Path):
    r = run(["git", "-C", str(root), "ls-files", "-z", "--cached"], timeout=15)
    if r.returncode != 0:
        return []
    files = []
    for rel in r.stdout.split("\0"):
        if not rel:
            continue
        p = Path(rel)
        if p.suffix.lower() not in SRC_EXT:
            continue
        if p.name.endswith((".min.js", ".min.css", ".d.ts", ".pb.go", "_pb2.py")):
            continue
        if EXCLUDE_DIRS.intersection(p.parts[:-1]):
            continue
        files.append(root / p)
    return files


def count_loc(files, cap: int) -> int:
    total = 0
    for f in files:
        try:
            if f.stat().st_size > 2_000_000:
                continue
            with open(f, "rb") as fh:
                total += fh.read().count(b"\n")
        except Exception:
            continue
        if total >= cap:
            break
    return total


# ---------------------------------------------------------------- state
def state_key(root: Path) -> str:
    return hashlib.sha1(str(root).encode()).hexdigest()[:16]


def load_decision(key: str):
    try:
        return json.loads((STATE_DIR / f"{key}.json").read_text())
    except Exception:
        return None


def save_decision(key: str, **data) -> None:
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        data["ts"] = time.time()
        (STATE_DIR / f"{key}.json").write_text(json.dumps(data))
    except Exception:
        pass


def acquire_lock(key: str) -> bool:
    lock = STATE_DIR / f"{key}.lock"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if lock.exists() and time.time() - lock.stat().st_mtime > LOCK_STALE:
            lock.unlink()
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        return True  # cannot lock at all: proceed rather than silently disabling


def release_lock(key: str) -> None:
    try:
        (STATE_DIR / f"{key}.lock").unlink(missing_ok=True)
    except Exception:
        pass


def nudge_once(session: str, key: str, msg: str) -> None:
    marker = STATE_DIR / f"nudge-{session}-{key}"
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if marker.exists():
            return
        marker.touch()
        cutoff = time.time() - 7 * 86400
        for p in STATE_DIR.glob("nudge-*"):
            try:
                if p.stat().st_mtime < cutoff:
                    p.unlink()
            except Exception:
                pass
    except Exception:
        pass
    emit(msg)


def clean_env():
    env = os.environ.copy()
    env["GRAPHIFY_HOOK_ACTIVE"] = "1"
    for k in LLM_ENV_KEYS:
        env.pop(k, None)
    return env


# ---------------------------------------------------------------- repo side effects
def _git_path(root: Path, rel: str) -> Path:
    p = run(["git", "-C", str(root), "rev-parse", "--git-path", rel], timeout=5)
    path = Path(p.stdout.strip())
    return path if path.is_absolute() else root / path


def install_git_hooks(root: Path, graphify: str, env) -> bool:
    """Install graphify's post-commit/post-checkout hooks without touching tracked files.

    `graphify hook install` appends a merge-driver line to .gitattributes (tracked).
    Whatever happens, .gitattributes is restored; the line goes to .git/info/attributes.
    """
    ga = root / ".gitattributes"
    before = ga.read_text() if ga.exists() else None
    ok = False
    try:
        r = run([graphify, "hook", "install"], cwd=str(root), timeout=min(STEP_TIMEOUT, max(5, remaining() - 5)), env=env)
        ok = r.returncode == 0
    except Exception:
        ok = False
    finally:
        try:
            after = ga.read_text() if ga.exists() else None
            if after != before:
                old_lines = set((before or "").splitlines())
                added = [ln for ln in (after or "").splitlines() if ln and ln not in old_lines]
                if before is None:
                    ga.unlink(missing_ok=True)
                else:
                    ga.write_text(before)
                if added:
                    attr = _git_path(root, "info/attributes")
                    attr.parent.mkdir(parents=True, exist_ok=True)
                    existing = attr.read_text() if attr.exists() else ""
                    new = [ln for ln in added if ln not in existing.splitlines()]
                    if new:
                        with open(attr, "a") as fh:
                            if existing and not existing.endswith("\n"):
                                fh.write("\n")
                            fh.write("\n".join(new) + "\n")
        except Exception:
            pass
    return ok


def exclude_locally(root: Path) -> None:
    try:
        r = run(["git", "-C", str(root), "check-ignore", "-q", "graphify-out"], timeout=5)
        if r.returncode == 0:
            return
        ex = _git_path(root, "info/exclude")
        ex.parent.mkdir(parents=True, exist_ok=True)
        existing = ex.read_text() if ex.exists() else ""
        if "graphify-out" not in existing:
            with open(ex, "a") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write("graphify-out/\n")
    except Exception:
        pass


def build(root: Path, graphify: str):
    env = clean_env()
    r = run([graphify, "extract", str(root), "--code-only", "--no-viz"],
            cwd=str(root), timeout=BUILD_TIMEOUT, env=env)
    if r.returncode != 0 or not (root / "graphify-out" / "graph.json").exists():
        raise RuntimeError((r.stderr or r.stdout or "extract failed")[-400:])
    stats = re.search(r"(\d+) nodes, (\d+) edges", r.stdout or "")
    if remaining() > STEP_TIMEOUT + 15:
        try:
            run([graphify, "cluster-only", str(root), "--no-label", "--no-viz"],
                cwd=str(root), timeout=STEP_TIMEOUT, env=env)
        except Exception:
            pass  # graph.json is already usable without the report
    return stats.group(0) if stats else "graph built"


QUERY_HINT = ("`graphify query \"<focused question>\"`, `graphify explain \"<Symbol>\"`, "
              "`graphify affected \"<Symbol>\"`, `graphify path \"<A>\" \"<B>\"` (run from the repo root)")


# ---------------------------------------------------------------- main
def main() -> None:
    if os.environ.get("GRAPHIFY_HOOK_ACTIVE") == "1":
        return
    data = json.loads(sys.stdin.read() or "{}")
    tool = data.get("tool_name") or ""
    if tool not in ("Grep", "Glob", "Bash"):
        return
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    session = re.sub(r"[^A-Za-z0-9_-]", "", str(data.get("session_id") or "nosession"))[:40]

    root = git_root(cwd)
    if root is None or root == Path.home() or str(root) == "/":
        return
    if not is_broad(tool, ti, cwd, root):
        return
    graphify = shutil.which("graphify")
    if not graphify:
        return

    key = state_key(root)
    graph = root / "graphify-out" / "graph.json"
    dec = load_decision(key) or {}
    now = time.time()

    if graph.exists():
        # requirement 8/9: make sure incremental hooks exist, but attempt at most once a day
        if dec.get("decision") == "built" and not dec.get("hooks_ok") and now - float(dec.get("hooks_ts", 0)) > FAIL_TTL:
            if acquire_lock(key):
                try:
                    ok = install_git_hooks(root, graphify, clean_env())
                    exclude_locally(root)
                    dec.update(hooks_ok=ok, hooks_ts=now)
                    save_decision(key, **{k: v for k, v in dec.items() if k != "ts"})
                finally:
                    release_lock(key)
        nudge_once(session, key,
            f"Graphify graph exists for this repository ({root.name}/graphify-out/graph.json). "
            "For architecture, dependency, call-flow, data-flow, or impact questions, query it before broad search "
            f"and then read only the files it points to: {QUERY_HINT}. "
            "Targeted searches for a known string are fine without it.")
        return

    head = git_head(root)
    if dec:
        age = now - float(dec.get("ts", 0))
        d = dec.get("decision")
        if d == "failed" and age < FAIL_TTL:
            return
        if d == "small" and age < SMALL_TTL and dec.get("head") == head:
            return
        if d == "too_large" and age < FAIL_TTL and dec.get("head") == head:
            return

    files = tracked_source_files(root)
    n = len(files)
    justified = n >= MIN_FILES
    loc = None
    if not justified and n > 0:
        loc = count_loc(files, MIN_LOC)
        justified = loc >= MIN_LOC
    if not justified:
        save_decision(key, decision="small", head=head, files=n, loc=loc)
        return
    if n > MAX_AUTO_FILES:
        save_decision(key, decision="too_large", head=head, files=n)
        nudge_once(session, key,
            f"This repository has {n} tracked source files and no Graphify graph; it is too large to build inside a hook. "
            "If the task needs architecture, dependency, or impact reasoning, build once in the background: "
            "`graphify extract . --code-only --no-viz && graphify cluster-only . --no-label --no-viz && graphify hook install` "
            f"(offline, tree-sitter only), then use {QUERY_HINT}.")
        return

    if not acquire_lock(key):
        return  # another hook invocation is already building this repo
    out_dir = root / "graphify-out"
    created_out = not out_dir.exists()
    try:
        try:
            stats = build(root, graphify)
        except Exception as e:
            timed_out = isinstance(e, subprocess.TimeoutExpired)
            if created_out and not graph.exists():
                shutil.rmtree(out_dir, ignore_errors=True)   # leave no untracked litter behind
            save_decision(key, decision="failed", head=head, files=n,
                          error="timeout" if timed_out else str(e)[:300])
            if timed_out:
                nudge_once(session, key,
                    f"Graphify build for {root.name} exceeded {BUILD_TIMEOUT}s and was cancelled (no graph). Continue normally; "
                    "to build manually in the background: `graphify extract . --code-only --no-viz`.")
            return

        exclude_locally(root)
        hooks_ok = install_git_hooks(root, graphify, clean_env()) if remaining() > 10 else False
        save_decision(key, decision="built", head=head, files=n, hooks_ok=hooks_ok, hooks_ts=now)
    finally:
        release_lock(key)

    hooks_msg = ("Incremental git hooks installed (post-commit/post-checkout, background, code-only)."
                 if hooks_ok else "Incremental git hooks not installed yet (will retry later; or run `graphify hook install`).")
    emit(
        f"Graphify graph initialized for {root.name} ({n} tracked source files; {stats}; code-only, offline, "
        f"output in graphify-out/, excluded locally via .git/info/exclude). {hooks_msg} "
        f"Use it to narrow scope before reading source: {QUERY_HINT}, `graphify god-nodes`. "
        "Then read only the files it points to. Do not read GRAPH_REPORT.md wholesale."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open, always
    sys.exit(0)
