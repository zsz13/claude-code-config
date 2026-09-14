#!/usr/bin/env python3
"""Source-read budget advisor. Advisory only: never blocks, never rewrites.
Fails open on any error.

Modes (argument):
  (none)    PreToolUse(Read|Bash): emit a hint, record nothing about the read
            itself (a denied or failed read must not count as a read).
  --record  PostToolUse(Read|Bash): record the completed read (range, mtime, size).

Hints, both short:
  1. Re-read: the same file (a covering range) was already read in this context
     and is unchanged on disk (mtime+size) -> suggest reusing what is already in
     context. Fires on each repeat. State is keyed by session AND agent id, so a
     subagent's reads never count for the parent or vice versa; the
     SessionStart(compact|clear) hook clears the state so post-compaction reads
     are never flagged.
  2. Large file: a whole-file read of a big file with no offset/limit ->
     suggest locating the target (LSP, grep -n) and reading a range, once per
     file per context. Whole-file reads stay legitimate when structure matters.

The Read tool returns at most READ_CAP lines per call, so a Read without limit is
recorded as lines 1..READ_CAP, never as "the whole file". Bash is covered only for
unpiped `cat|bat|less|more FILE` (whole file), `sed -n 'A,Bp' FILE`, `head -n N FILE`.
"""
import json, os, re, sys, time
from pathlib import Path

LARGE_LINES = 400
LARGE_BYTES = 16 * 1024  # ~4k tokens
READ_CAP = 2000          # Read tool default/maximum lines per call
STATE_DIR = Path.home() / ".cache" / "claude-hooks" / "read-budget"
MAX_TRACKED = 400


def target(d):
    """Return (path, range) for the read this payload describes, or (None, None).
    range: None = whole file; (start, end) 1-based inclusive."""
    tool = d.get("tool_name")
    ti = d.get("tool_input") or {}
    if tool == "Read":
        path = ti.get("file_path")
        off, lim = ti.get("offset"), ti.get("limit")
        start = int(off or 1)
        end = start + (int(lim) if lim else READ_CAP) - 1
        return path, (start, end)
    if tool == "Bash":
        cmd = str(ti.get("command") or "").strip()
        if not cmd or "|" in cmd or ">" in cmd or "&&" in cmd or ";" in cmd:
            return None, None
        f = r"([^\s'\"]+|'[^']+'|\"[^\"]+\")"
        m = re.match(r"^(?:cat|bat|less|more)(?:\s+-[A-Za-z]+)*\s+" + f + r"\s*$", cmd)
        if m:
            return m.group(1).strip("'\""), None
        m = re.match(r"^sed\s+-n\s+['\"]?(\d+),(\d+)p['\"]?\s+" + f + r"\s*$", cmd)
        if m:
            return m.group(3).strip("'\""), (int(m.group(1)), int(m.group(2)))
        m = re.match(r"^head\s+-n\s*(\d+)\s+" + f + r"\s*$", cmd)
        if m:
            return m.group(2).strip("'\""), (1, int(m.group(1)))
    return None, None


def covers(prev, want):
    if prev is None:
        return True
    if want is None:
        return False
    return prev[0] <= want[0] and prev[1] >= want[1]


def count_lines(p: Path) -> int:
    """Newline count; negative means 'at least this many' (stopped after 8 MB)."""
    lines = 0
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            lines += chunk.count(b"\n")
            if fh.tell() > 8 << 20:
                return -lines
    return lines


def main(record: bool) -> None:
    d = json.load(sys.stdin)
    path, rng = target(d)
    if not path:
        return
    cwd = d.get("cwd") or os.getcwd()
    p = Path(os.path.expanduser(path))
    if not p.is_absolute():
        p = Path(cwd) / p
    try:
        st = p.stat()
    except OSError:
        return
    if not p.is_file():
        return
    ident = str(d.get("session_id") or "nosession")
    if d.get("agent_id"):
        ident += "-" + str(d.get("agent_id"))
    sid = re.sub(r"[^A-Za-z0-9_-]", "", ident)[:80]
    key = str(p.resolve())
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    sf = STATE_DIR / f"{sid}.json"
    try:
        state = json.loads(sf.read_text()) if sf.exists() else {}
    except Exception:
        state = {}
    entry = state.get(key) or {}
    unchanged = entry.get("mtime") == st.st_mtime and entry.get("size") == st.st_size
    dirty = False
    msg = None

    if record:
        reads = entry.get("reads", []) if unchanged else []
        reads.append(list(rng) if rng else None)
        entry.update({"mtime": st.st_mtime, "size": st.st_size, "reads": reads[-12:], "t": time.time()})
        dirty = True
    else:
        try:
            rel = os.path.relpath(key, cwd) if key.startswith(str(Path(cwd).resolve())) else key
        except ValueError:
            rel = key
        prev_reads = [tuple(r) if r else None for r in entry.get("reads", [])]
        if unchanged and any(covers(r, rng) for r in prev_reads):
            how = "whole file" if rng is None else f"lines {rng[0]}-{rng[1]}"
            msg = (f"Re-read hint: {rel} was already read in this context (a covering range; now requested {how}) and is "
                   f"unchanged on disk. Reuse the content already in context. Read it only if that content is genuinely not "
                   f"in your context (compaction, a denied or failed read) or you need a different range; after an edit, "
                   f"inspect the changed region or the diff, not the whole file.")
        elif (rng is None or (rng[0] == 1 and rng[1] >= READ_CAP)) and not entry.get("hinted") and st.st_size >= LARGE_BYTES:
            try:
                lines = count_lines(p)
            except OSError:
                lines = 0
            if lines >= LARGE_LINES or lines < 0:
                approx = f"~{max(1, st.st_size // 4 // 1000)}k tokens"
                n = f"{abs(lines)}{'+' if lines < 0 else ''} lines"
                narrow = ("`grep -n <symbol|key> <file>` then `sed -n 'A,Bp' <file>`" if d.get("tool_name") == "Bash"
                          else "LSP definition/references or `grep -n`, then Read with offset/limit")
                cap = f" (a single Read returns at most {READ_CAP} lines)" if abs(lines) > READ_CAP else ""
                msg = (f"Read budget hint: {rel} is {n} ({approx}){cap}. If one function, class, section, or key is the subject, "
                       f"locate it first ({narrow}) and read that range with enough surrounding context (imports, enclosing scope, "
                       f"control flow); widen if it proves insufficient. Read the whole file when it is small or its structure, "
                       f"cross-section interactions, or a wide refactor need it.")
                entry["hinted"] = True
                entry.setdefault("t", time.time())
                dirty = True
    if dirty:
        state[key] = entry
        if len(state) > MAX_TRACKED:
            for k in sorted(state, key=lambda k: state[k].get("t", 0))[: len(state) - MAX_TRACKED]:
                state.pop(k, None)
        try:
            sf.write_text(json.dumps(state))
            cutoff = time.time() - 7 * 86400
            for old in STATE_DIR.iterdir():
                if old.suffix == ".json" and old.stat().st_mtime < cutoff:
                    old.unlink()
        except Exception:
            pass
    if msg:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}}))


if __name__ == "__main__":
    try:
        main("--record" in sys.argv[1:])
    except Exception:
        pass
    sys.exit(0)
