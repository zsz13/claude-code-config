#!/usr/bin/env python3
"""Decision table for hooks/skill-install-guard.sh.

Feeds PreToolUse payloads to the hook as Claude Code would and compares the
decision it returns: "ask", or none (the hook stays silent and the normal
permission flow applies). Each row is a form that was tried; the table says how
many forms were tried, not that no others exist. Run by scripts/verify.sh.

Usage: scripts/test-skill-install-guard.py [HOOK] [-v]
  HOOK  path to skill-install-guard.sh (default: this repository's copy)
  -v    print every case and the reason shown for each "ask"
Exit:  0 = every case decided as expected, 1 = at least one did not.
"""
import json
import os
import pathlib
import subprocess
import sys

args = [a for a in sys.argv[1:] if a != "-v"]
VERBOSE = "-v" in sys.argv[1:]
HOOK = args[0] if args else str(pathlib.Path(__file__).resolve().parent.parent / "hooks/skill-install-guard.sh")
H = os.path.expanduser("~")
ASK, NONE = "ask", None

BASH = [
    (ASK, "npx skills add vercel-labs/agent-skills --skill web-design-guidelines -g -y"),
    (ASK, "npx -y skills@latest add owner/repo"),
    (ASK, "npx --package skills skills add owner/repo"),
    (ASK, "bunx skills a owner/repo"),
    (ASK, "pnpm dlx skills update"),
    (ASK, "npm exec -- skills add owner/repo"),
    (ASK, "skills upgrade -g"),
    (ASK, "npx skills remove foo -y"),
    (ASK, "npx skills experimental_install"),
    (ASK, "npx add-skill owner/repo"),
    (ASK, "cd /tmp && npx skills add owner/repo"),
    (ASK, "FOO=1 sudo npx skills add owner/repo"),
    (ASK, 'bash -lc "npx skills add owner/repo -y; echo done"'),
    (ASK, "claude plugin install foo@bar --scope project"),
    (ASK, "claude plugin i foo@bar"),
    (ASK, "claude plugin marketplace add owner/repo"),
    (ASK, "claude plugins update foo"),
    (ASK, "claude plugin enable foo@bar"),
    (ASK, "mkdir -p .claude/skills/x"),
    (ASK, "cp -r /tmp/x ~/.claude/skills/"),
    (ASK, "cp -t ~/.claude/skills /tmp/x"),
    (ASK, 'ln -s "$PWD/.agents/skills/x" .claude/skills/x'),
    (ASK, "mv ~/.claude/skills/x /tmp/x"),
    (ASK, "git clone https://github.com/o/r ~/.claude/skills/r"),
    (ASK, "git -C ~/.claude/skills/r pull"),
    (ASK, "cat > .claude/skills/x/SKILL.md <<'EOF'\n---\nname: x\n---\nit's a test\nEOF"),
    (ASK, "printf 'x' >> ~/.agents/skills/x/SKILL.md"),
    (ASK, "curl -fsSL https://example.com/SKILL.md -o ~/.agents/skills/x/SKILL.md"),
    (ASK, "rm -rf ~/.claude/skills/x"),
    (ASK, "sed -i '' 's/a/b/' .claude/skills/x/SKILL.md"),
    (ASK, "tee .codex/skills/x/SKILL.md < /tmp/s"),
    (ASK, "tar -xzf /tmp/s.tgz -C ~/.claude/skills"),
    (ASK, "unzip /tmp/s.zip -d .claude/skills/x"),
    (ASK, "touch .claude/commands/deploy.md"),
    (NONE, "npx skills find react performance"),
    (NONE, "npx skills use vercel-labs/agent-skills@web-design-guidelines"),
    (NONE, "npx skills use vercel-labs/agent-skills --skill web-design-guidelines"),
    (NONE, "npx skills add vercel-labs/agent-skills --list"),
    (NONE, "npx skills list -g"),
    (NONE, "npx skills --help"),
    (NONE, "ls -la ~/.claude/skills"),
    (NONE, "cat ~/.claude/skills/x/SKILL.md"),
    (NONE, "sed -n 1,40p .claude/skills/x/SKILL.md"),
    (NONE, "cp ~/.claude/skills/x/SKILL.md /tmp/review.md"),
    (NONE, "tar -czf /tmp/backup.tgz ~/.claude/skills"),
    (NONE, "git -C ~/.claude/skills/r log --oneline -n 5"),
    (NONE, 'rg -n "npx skills add" docs/'),
    (NONE, 'git commit -m "docs: explain npx skills add and claude plugin install"'),
    (NONE, "grep -rn skills src/ 2>/dev/null"),
    (NONE, "ls ~/.claude/skills 2>/dev/null"),
    (NONE, "curl -s https://raw.githubusercontent.com/o/r/main/.claude/skills/x/SKILL.md"),
    (NONE, "claude plugin list"),
    (NONE, "claude plugin details superpowers"),
    (NONE, "mkdir -p skills/new-skill && cp /tmp/s skills/new-skill/SKILL.md"),
    (NONE, "npm install && npm test"),
    (NONE, "echo 'unterminated"),
]
REVIEW = [  # forms an adversarial review found the first version missed
    (ASK, "cp -r /tmp/frontend-design \\\n  ~/.claude/skills/"),
    (ASK, "npx skills \\\n  add o/r -g"),
    (ASK, "echo step#1 && mkdir -p ~/.claude/skills/x"),
    (ASK, "cd /tmp/src  # fetched\ncp -r foo ~/.claude/skills/"),
    (ASK, "for s in a b; do cp -r /tmp/$s ~/.claude/skills/; done"),
    (ASK, "if true; then mkdir .claude/skills/x; fi"),
    (ASK, "ls | xargs -I{} cp -r {} ~/.claude/skills/"),
    (ASK, "find ~/.claude/skills -mindepth 1 -delete"),
    (ASK, "find /tmp/s -name SKILL.md -exec cp {} ~/.claude/skills/x/ \\;"),
    (ASK, "timeout 60 npx skills add o/r -g"),
    (ASK, "sudo -E npx skills add o/r -g"),
    (ASK, "cd ~/.claude/skills && git clone https://github.com/o/r"),
    (ASK, "cd ~/.claude/skills/foo && git pull"),
    (ASK, "cd .claude && cp -r ~/dl/foo skills/"),
    (ASK, "cp -r skills ~/.claude/"),
    (ASK, "mv skills ~/.claude"),
    (ASK, "gh repo clone o/r ~/.claude/skills/r"),
    (ASK, "npx degit o/r ~/.claude/skills/r"),
    (ASK, "scp host:x ~/.claude/skills/"),
    (ASK, "claude --debug plugin install x"),
    (NONE, "find ~/.claude/skills -name SKILL.md"),
    (NONE, "find ~/.claude/skills -name SKILL.md -exec cat {} \\;"),
    (NONE, "cd ~/.claude/skills && ls -la"),
    (NONE, "cd ~/.claude/skills/x && git log --oneline -n 3"),
    (NONE, "cd src && cp a.ts b.ts"),
    (NONE, "for f in src/*.ts; do cp $f /tmp/; done"),
    (NONE, "timeout 60 npm test"),
    (NONE, "# just a comment mentioning npx skills find"),
]
FILES = [  # (expect, tool, file_path)
    (ASK, "Write", f"{H}/proj/.claude/skills/x/SKILL.md"),
    (ASK, "Edit", f"{H}/.claude/skills/frontend-quality/SKILL.md"),
    (ASK, "MultiEdit", f"{H}/proj/.agents/skills/x/SKILL.md"),
    (ASK, "Write", f"{H}/.claude/plugins/cache/x/y.md"),
    (ASK, "Write", f"{H}/proj/.claude/commands/x.md"),
    (ASK, "Write", f"{H}/.codex/skills/x/SKILL.md"),
    (ASK, "Write", ".claude/skills/x/SKILL.md"),
    (ASK, "Write", f"{H}/.claude/Skills/foo/SKILL.md"),
    (NONE, "Write", f"{H}/github/claude-code-config/skills/design-brief/SKILL.md"),
    (NONE, "Edit", f"{H}/proj/src/app.ts"),
    (NONE, "Write", f"{H}/proj/docs/skills/guide.md"),
    (NONE, "Write", f"{H}/proj/.claude/settings.json"),
    (NONE, "Write", f"{H}/proj/.claude/skills-notes.md"),
    (NONE, "Write", f"{H}/proj/src/commands/deploy.ts"),
]
SETTINGS = [  # (expect, tool, file_path, extra tool_input)
    (ASK, "Edit", f"{H}/.claude/settings.json", {"old_string": "{", "new_string": '{"enabledPlugins": {"x@m": true},'}),
    (ASK, "Write", f"{H}/proj/.claude/settings.local.json", {"content": '{"extraKnownMarketplaces": {}}'}),
    (NONE, "Edit", f"{H}/.claude/settings.json", {"old_string": '"model": "a"', "new_string": '"model": "b"'}),
    (NONE, "Edit", f"{H}/proj/package.json", {"old_string": "{", "new_string": '{"enabledPlugins": 1,'}),
]


def decide(payload: str) -> tuple[str | None, str]:
    out = subprocess.run(["sh", HOOK], input=payload, capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        return f"exit {out.returncode}", out.stderr.strip()
    if not out.stdout.strip():
        return None, ""
    h = json.loads(out.stdout)["hookSpecificOutput"]
    return h["permissionDecision"], h["permissionDecisionReason"]


def bash(c: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": c}})


def tool(t: str, p: str, extra: dict | None = None) -> str:
    return json.dumps({"tool_name": t, "tool_input": {"file_path": p, **(extra or {"content": "x"})}})


rows = [(e, bash(c), c) for e, c in BASH + REVIEW]
rows += [(e, tool(t, p), f"{t} {p}") for e, t, p in FILES]
rows += [(e, tool(t, p, x), f"{t} {p} {x}") for e, t, p, x in SETTINGS]
rows += [(NONE, json.dumps({"tool_name": "Read", "tool_input": {"file_path": f"{H}/.claude/skills/x/SKILL.md"}}), "Read a skill file")]
rows += [(NONE, "not json {", "malformed payload (fails open)")]

fails = 0
for expect, payload, label in rows:
    got, reason = decide(payload)
    ok = got == expect
    fails += not ok
    if VERBOSE or not ok:
        print(f"{'PASS' if ok else 'FAIL'}  {str(expect):4} <- {label!r}" + ("" if ok else f"  [got {got}] {reason}"))
        if ok and got == ASK:
            print(f"        {reason}")
print(f"{len(rows) - fails}/{len(rows)} cases decided as expected")
sys.exit(1 if fails else 0)
