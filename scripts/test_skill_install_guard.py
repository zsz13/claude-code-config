#!/usr/bin/env python3
"""Decision table for hooks/skill-install-guard.sh.

Feeds PreToolUse payloads to the hook as Claude Code would and compares the
decision it returns: "ask", or none (the hook stays silent and the normal
permission flow applies). Each row is a form that was tried; the table says how
many forms were tried, not that no others exist. Run by scripts/verify.sh.

The sample commands are data in this file, handed to the hook on stdin. Edit
this table with a file editor, never through a shell command that spells the
samples out: a live guard reads that command, and its samples look like installs.

Usage: python3 scripts/test_skill_install_guard.py [HOOK] [-v]
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
# The command the guard once asked about by mistake: a PR body, written by a quoted here-doc,
# mentioned `skills add`. Only the scratchpad and repository paths are made generic.
PR_COMMAND = r'''S=/tmp/claude-scratchpad
cat > "$S/pr-body.md" <<'EOF'
## What

Skills can be searched for and used on demand. Installing, updating or removing one is always the user's decision.

- **Policy:** a new "Skills on demand" section in `examples/CLAUDE.example.md`. It says:
  - search with `npx skills find` only when a specialised task would materially benefit;
  - run a skill once with `npx skills use`;
  - prefer official or well-known sources, and read a skill before following it;
  - avoid duplicate or conflicting skills;
  - propose a permanent install only after repeated use, never for popularity;
  - never recreate a declined install by hand.
- **Guard:** `hooks/skill-install-guard.{sh,py}`, a PreToolUse hook on `Bash|Write|Edit|MultiEdit|NotebookEdit`. It returns `permissionDecision: "ask"` before:
  - `skills add`/`update`/`remove`, also when run through `npx`, `bunx`, `pnpm dlx` or `npm exec`;
  - `claude plugin install`/`update`/`enable`/… and `claude plugin marketplace add`;
  - settings edits that set `enabledPlugins` or `extraKnownMarketplaces`;
  - any write into `.claude/skills`, `.agents/skills`, `.codex/skills`, `.claude/commands` or `.claude/plugins`, whether made with the file tools or with shell commands.

  The prompt says what would be installed and where. The guard never denies and fails open. It never prompts for `skills find`, `skills use`, reads, or ordinary edits.
- **Settings:** `config/settings.example.json` registers the guard and allows `Bash(npx skills find:*)` and `Bash(npx skills use:*)`.
- **Regression table:** `scripts/test-skill-install-guard.py` holds 104 cases, including the 23 an adversarial review found the first version missed. `scripts/verify.sh` now runs it.
- **Docs:**
  - the rationale is in `docs/why-this-setup.md`;
  - the limits are in `docs/security.md` and `hooks/README.md`;
  - the measurements are in `docs/benchmarks.md` §10.

## Verification

- `scripts/verify.sh --repo-only` on a clean copy of this commit: 62 passed, 0 failed. That includes `104/104 cases decided as expected`.
- **Red–green:** run against a hook that never asks, the table reports 40/104 and fails.
- **Headless sessions with only this hook configured:** these cover auto and default modes, with and without the guard (table in benchmarks §10).
- **Live configuration**, with the guard installed beside the other hooks and plugins, in a throwaway folder:
  - `skills find` ran, both headless (`acceptEdits`) and interactive (auto mode);
  - `skills use` ran in both;
  - the edit to `src/app.ts` was applied in both;
  - `skills add` was refused in the headless run, with `decision_reason_type: "hook"`;
  - interactively, Claude Code showed "Hook PreToolUse:Bash requires confirmation for this command:", the guard's reason, then "Do you want to proceed?". It was declined.
  - No skill was installed: nothing changed in the folder, `~/.claude/skills` or `~/.agents/skills`.

## Limits

- **Not a sandbox.** It reads command text, so it misses:
  - a path built at run time;
  - a script file;
  - `python -c` or `node -e`;
  - `jq` rewriting `settings.json`;
  - a download tool it doesn't know.
- An approved prompt counts as an approval. `bypassPermissions` mode and an approved install going through were not tested.
- Each `npx skills` run fetches the latest `skills` package; the two allow rules let that happen without a prompt.
- Whether the policy text changes when sessions search is a hypothesis (benchmarks §9).
EOF
cd ~/github/claude-code-config && gh pr create --base main --head feat/skill-install-guard --title "feat(hooks): ask before persistent skill or plugin installs" --body-file "$S/pr-body.md"'''
DOCS = [  # a command mentioned as text is data; a command the shell runs is not
    (NONE, PR_COMMAND),
    (NONE, 'gh pr create --title "docs: skills" --body "Asks before \\`npx skills add\\` and \\`claude plugin install\\`; it\'s a guard."'),
    (NONE, "gh issue create --title 'Install flow' --body 'Steps: npx skills update -g, then claude plugin install foo@bar.'"),
    (NONE, "git commit -q -F - <<'EOF'\nfeat(hooks): guard\n\n- asks before `skills add`/`update`/`remove` and `claude plugin install`\n- it's quoted, so nothing here runs\nEOF"),
    (NONE, "cat > docs/install.md <<'EOF'\n# Installing\nRun `npx skills add owner/repo -g`; don't run `claude plugin install x@y` blindly.\nEOF"),
    (NONE, "cat >> notes.md <<EOF\nInstall later with npx skills add owner/repo (it's optional)\nEOF"),
    (NONE, "gh pr comment 3 --body-file - <<'EOF'\nUse `npx skills use o/r@s` instead of `npx skills add`.\nEOF"),
    (NONE, "cat <<'EOF' | gh pr edit 3 --body-file -\nupdated: `skills add` now asks | see docs\nEOF"),
    (NONE, 'echo "To install: npx skills add o/r; to update: npx skills update -g"'),
    (NONE, "printf '%s\\n' 'npx skills remove foo' 'claude plugin install bar@m'"),
    (NONE, "git commit -m 'docs: explain `skills update` and `claude plugin install`'"),
    (NONE, "# don't run npx skills add here\nls -la"),
    (NONE, "python3 - <<'PY'\ncases = [('ask', \"npx skills add o/r -g\"), ('ask', \"bash <<'EOF'\")]\nPY"),
    (NONE, "git commit -m \"$(cat <<'EOF'\nfeat: guard\n\n1) asks before `skills add`\n2) not before `skills use`\nEOF\n)\""),
    (NONE, "gh pr create --body $(cat <<'EOF'\nmentions npx skills add o/r\nEOF\n)"),
    (ASK, "bash <<'EOF'\nnpx skills add o/r -g\nEOF"),
    (ASK, "sh -s <<'EOF'\nclaude plugin install foo@bar\nEOF"),
    (ASK, "ssh localhost <<'EOF'\nnpx skills update -g\nEOF"),
    (ASK, "cat > /tmp/notes.md <<EOF\nresult: $(npx skills add o/r -g)\nEOF"),
    (ASK, 'echo "$(npx skills add o/r -g)"'),
    (ASK, 'git commit -m "docs: `npx skills add o/r`"'),
    (ASK, "cat <<'EOF' > .agents/skills/x/SKILL.md\nit's a skill\nEOF"),
    (ASK, "# don't skip this\nnpx skills add o/r"),
    (ASK, "cat > notes.md <<'EOF'\nnpx skills add a/b\nEOF\nnpx skills add o/r -g"),
    (ASK, "gh pr create --body-file - <<'EOF' && cp -r x ~/.claude/skills/\nbody it's\nEOF"),
    (ASK, "x=$(cat <<'EOF'\nnotes (1\nEOF\n); npx skills add o/r"),
    (ASK, "(( n = 1 << 2 ))\nnpx skills add o/r -g"),
    (ASK, "ksh <<'EOF'\nclaude plugin update foo\nEOF"),
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


rows = [(e, bash(c), c if len(c) < 160 else c[:150] + " [...]") for e, c in BASH + REVIEW + DOCS]
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
