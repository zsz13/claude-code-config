#!/usr/bin/env python3
"""Classifier for skill-install-guard.sh. Reads the PreToolUse payload on stdin.

Asks the user (permissionDecision "ask") before a persistent skill or plugin change:
  skills add|update|remove|experimental_install|experimental_sync   (bare, or via npx/bunx/pnpm dlx/npm exec)
  add-skill <source>
  claude plugin install|update|uninstall|enable|disable|init|prune, claude plugin marketplace add|remove|update
  Write/Edit/MultiEdit/NotebookEdit of a file in a skill or plugin directory, or of a Claude Code settings
  file when the new text sets enabledPlugins or extraKnownMarketplaces
  a shell command that writes into a skill or plugin directory: cp/mv/ln/rsync/install/ditto/scp/degit
  (destination, or destination plus the source's name), mkdir/rm/rmdir/touch/tee/unzip/patch/curl/wget,
  tar -x, git clone/pull/checkout/..., gh repo clone, sed -i/perl -i, find -delete/-exec, redirection, or
  any of those run after a `cd` into one; relative paths are resolved against earlier `cd`s
Skill and plugin directories, at any depth and in any letter case: .claude/skills, .agents/skills,
.codex/skills, .claude/commands, .claude/plugins. Never asked about: skills find|use|list|init,
skills add --list, reading those directories.
Code is separated from data first, as the shell does: here-doc bodies (a PR body, a commit message, a
document) and comments are data, so the commands they mention are not commands; a here-doc fed to a shell
(`bash <<EOF`, `ssh host <<EOF`) is a script, and $(...) or `...` outside single quotes, including in
double quotes and unquoted here-docs, runs. The code is then tokenized quote-aware (shlex with shell
punctuation, line continuations joined), so a quoted mention is not a command. Shell keywords, wrappers
(sudo, env, timeout, xargs, ...), package runners and `sh -c` strings are looked through. Anything
unparseable or unrelated -> exit 0 with no decision. Fails open.
"""
import json
import os
import re
import shlex
import sys

SEG = re.compile(r"\|\||&&|\||;|\n|\(|\)|\$\(|`")
REDIRECT = re.compile(r">>?\|?\s*([^\s;&|<>()]+)")
HEREDOC = re.compile(r"<<(-?)[ \t]*(?:'([^'\n]*)'|\"([^\"\n]*)\"|(\\?)([^\s;&|<>()'\"]+))")
SKILL_DIR = re.compile(r"(?:^|[/=])\.(?:(?:claude|agents|codex)/skills|claude/(?:commands|plugins))(?:/|$)", re.I)
SETTINGS_FILE = re.compile(r"(?:^|/)\.claude/settings(?:\.local)?\.json$", re.I)
PLUGIN_KEYS = re.compile(r"enabledPlugins|extraKnownMarketplaces")
SHELL_C = re.compile(r"-[A-Za-z]*c[A-Za-z]*")
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{"}
PREFIXES = {  # wrapper -> its flags that take a value
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-U", "-r", "-t"}, "env": {"-u", "-C", "-S"},
    "xargs": {"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a", "-J", "-R"}, "nice": {"-n"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"}, "command": set(), "time": set(), "exec": set(),
    "nohup": set(), "stdbuf": set(),
}
RUNNERS = {"npx", "bunx", "pnpx"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish"}
SKILLS_WRITE = {"add", "a", "update", "upgrade", "remove", "rm", "experimental_install", "experimental_sync"}
SKILLS_VALUE_FLAGS = {"-a", "--agent", "-s", "--skill", "--metadata", "--subagent", "--include", "--exclude"}
PLUGIN_WRITE = {"install", "i", "update", "uninstall", "remove", "enable", "disable", "init", "new", "prune", "autoremove"}
MARKETPLACE_WRITE = {"add", "remove", "rm", "update"}
COPIES = {"cp", "mv", "ln", "rsync", "install", "ditto", "scp", "degit", "tiged"}
WRITES_ANY_ARG = {"mkdir", "rm", "rmdir", "touch", "tee", "unzip", "patch", "curl", "wget"}
GIT_WRITE = {"clone", "pull", "checkout", "switch", "reset", "restore", "merge", "rebase", "am", "apply",
             "submodule", "init", "mv", "rm", "clean", "stash", "worktree"}


def in_skill_dir(path: str) -> bool:
    return "://" not in path and bool(SKILL_DIR.search(os.path.normpath(path)))


def resolve(cwd: str, path: str) -> str:
    return path if not cwd or path.startswith(("/", "~", "$")) or "://" in path else os.path.join(cwd, path)


def substitution(text: str, i: int) -> tuple[str | None, str, int]:
    """For the `...` or $(...) at text[i]: the command it runs (None for $((arithmetic))), its text
    with here-doc bodies and comments removed, and the index just past it."""
    if text[i] == "`":
        j = i + 1
        while j < len(text) and text[j] != "`":
            j += 2 if text[j] == "\\" else 1
        j = min(j + 1, len(text))
        return text[i + 1:j - 1], text[i:j], j
    inner, _, j = scan(text, i + 2, nested=True)
    return (None if text.startswith("$((", i) else text[i + 2:j - 1]), "$(" + inner + ")", j


def body_substitutions(body: str) -> list[str]:
    """Command substitutions in an unquoted here-doc body, where quotes are literal text."""
    out, i = [], 0
    while i < len(body):
        if body[i] == "\\":
            i += 2
        elif body[i] == "`" or body.startswith("$(", i):
            sub, _, i = substitution(body, i)
            out += [sub] if sub is not None else []
        else:
            i += 1
    return out


def feeds_shell(prefix: str) -> bool:
    """Whether the here-doc read by this command is a script that runs (bash <<EOF, ssh host <<EOF)."""
    try:
        argv = effective_argv(shlex.split(prefix, posix=True))
    except ValueError:
        return True
    names = [os.path.basename(a) for a in argv]
    return bool(names) and (names[0] in ("ssh", "source", ".") or (
        any(a in SHELLS for a in names) and not any(SHELL_C.fullmatch(a) for a in argv)))


def scan(cmd: str, i: int = 0, nested: bool = False) -> tuple[str, list[str], int]:
    """(code, scripts, end). The code is the command without here-doc bodies, comments and line
    continuations. The scripts are what the shell also runs: $(...) and `...` outside single quotes,
    substitutions in unquoted here-docs, and here-doc bodies fed to a shell (or never closed, so the
    text after them is not lost). Any other here-doc body is data, so a command it mentions is not run.
    With nested, scanning starts inside a $( and stops just past the ) that closes it."""
    code, scripts, pending = "", [], []
    n, quote, start, depth = len(cmd), "", 0, 0
    while i < n:
        c = cmd[i]
        if quote == "'":
            quote = "" if c == "'" else quote
            code, i = code + c, i + 1
        elif c == "\\":
            code, i = (code, i + 2) if cmd.startswith("\\\n", i) else (code + cmd[i:i + 2], i + 2)
        elif c == "`" or cmd.startswith("$(", i):
            sub, text, i = substitution(cmd, i)
            scripts += [sub] if sub is not None else []
            code += text
        elif quote == '"':
            quote = "" if c == '"' else quote
            code, i = code + c, i + 1
        elif c in "'\"":
            quote, code, i = c, code + c, i + 1
        elif c == "#" and (not code or code[-1] in " \t\n;&|()"):
            j = cmd.find("\n", i)
            i = n if j < 0 else j
        elif cmd.startswith("<<", i) and not cmd.startswith("<<<", i) and (m := HEREDOC.match(cmd, i)):
            delim = next(g for g in (m.group(2), m.group(3), m.group(5)) if g is not None)
            literal = m.group(5) is None or m.group(4) == "\\"
            pending.append((delim, literal, m.group(1) == "-", code[start:]))
            code, i = code + m.group(0), m.end()
        elif c == "\n" and pending:
            code, i = code + c, i + 1
            for delim, literal, tabs, prefix in pending:
                lines, closed = [], False
                while i < n and not closed:
                    j = cmd.find("\n", i)
                    line, i = cmd[i:n if j < 0 else j], n if j < 0 else j + 1
                    closed = (line.lstrip("\t") if tabs else line) == delim
                    lines += [] if closed else [line]
                body = "\n".join(lines)
                if not closed or feeds_shell(prefix):
                    scripts.append(body)
                elif not literal:
                    scripts += body_substitutions(body)
            pending, start = [], len(code)
        else:
            if nested and c in "()":
                depth += 1 if c == "(" else -1
                if depth < 0:
                    return code, scripts, i + 1
            if c in ";&|()\n":
                start = len(code) + 1
            code, i = code + c, i + 1
    return code, scripts, n


def segments(cmd: str) -> list[tuple[list[str], list[str]]]:
    """(argv, redirect targets) per shell segment. Quote-aware; falls back to a plain split."""
    try:
        lex = shlex.shlex(cmd, posix=True, punctuation_chars=";&|()<>\n")
        lex.whitespace = " \t\r"
        lex.whitespace_split = True
        lex.commenters = ""
        toks = list(lex)
    except ValueError:
        out = []
        for seg in SEG.split(cmd):
            try:
                argv = shlex.split(seg, posix=True)
            except ValueError:
                argv = seg.split()
            out.append((argv, REDIRECT.findall(seg)))
        return out
    out, argv, targets, i = [], [], [], 0
    while i < len(toks):
        t = toks[i]
        if t and all(c in ";&|()<>\n" for c in t):
            if ">" in t or "<" in t:
                if ">" in t and i + 1 < len(toks):
                    targets.append(toks[i + 1])
                i += 2
                continue
            out.append((argv, targets))
            argv, targets = [], []
        else:
            argv.append(t)
        i += 1
    out.append((argv, targets))
    return out


def effective_argv(toks: list[str]) -> list[str]:
    """Drop env assignments, shell keywords, wrappers (sudo, timeout, xargs, ...) and package runners."""
    while toks:
        head = os.path.basename(toks[0])
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]) or toks[0] in KEYWORDS:
            toks = toks[1:]
            continue
        if head in PREFIXES:
            toks, takes_value = toks[1:], PREFIXES[head]
        elif head in RUNNERS:
            toks, takes_value = toks[1:], {"-p", "--package"}
        elif head in ("npm", "pnpm", "yarn", "bun") and len(toks) > 1 and toks[1] in ("exec", "dlx", "x"):
            toks, takes_value = toks[2:], {"-p", "--package"}
        else:
            return toks
        while toks and toks[0].startswith("-"):
            flag, toks = toks[0], toks[1:]
            if flag in takes_value and toks:
                toks = toks[1:]
        if head == "timeout":
            toks = toks[1:]  # the duration
    return toks


def skills_reason(args: list[str]) -> str | None:
    flags, pos, named, i = set(), [], [], 0
    while i < len(args):
        a = args[i]
        if a in SKILLS_VALUE_FLAGS and i + 1 < len(args):
            if a in ("-s", "--skill"):
                named.append(args[i + 1])
            i += 2
            continue
        if a.startswith("--skill="):
            named.append(a.split("=", 1)[1])
        elif a.startswith("-"):
            flags.add(a)
        else:
            pos.append(a)
        i += 1
    if not pos or pos[0] not in SKILLS_WRITE:
        return None
    sub, rest = pos[0], pos[1:]
    if sub in ("add", "a") and flags & {"-l", "--list"}:
        return None
    is_global = "--global" in flags or any(re.fullmatch(r"-[a-z]*g[a-z]*", f) for f in flags)
    which = ", ".join(named) or ("all skills" if "--all" in flags else "")
    if sub in ("add", "a"):
        where = ("globally: ~/.agents/skills, linked into every detected agent's skill directory including "
                 "~/.claude/skills" if is_global else "into this project: .agents/skills, linked into .claude/skills")
        return f"`skills add` installs {which or 'skills'} from {rest[0] if rest else '(no source given)'} {where}."
    scope = "global" if is_global else "project" if flags & {"-p", "--project"} else "project or global"
    return f"`skills {sub}` changes installed skills ({', '.join(rest) or which or 'all'}; {scope} scope)."


def plugin_reason(args: list[str]) -> str | None:
    pos, scope, i = [], "user", 0
    while i < len(args):
        a = args[i]
        if a in ("-s", "--scope") and i + 1 < len(args):
            scope, i = args[i + 1], i + 2
            continue
        if a.startswith("--scope="):
            scope = a.split("=", 1)[1]
        elif not a.startswith("-"):
            pos.append(a)
        i += 1
    if pos[:1] == ["marketplace"] and len(pos) > 1 and pos[1] in MARKETPLACE_WRITE:
        return f"`claude plugin marketplace {pos[1]}` {' '.join(pos[2:3])} changes your plugin marketplaces."
    if pos and pos[0] in PLUGIN_WRITE:
        return f"`claude plugin {pos[0]}` {' '.join(pos[1:2])} changes installed plugins (scope: {scope})."
    return None


def git_subcommand(args: list[str]) -> str:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    return args[i] if i < len(args) else ""


def written_paths(head: str, args: list[str]) -> list[str] | None:
    """The paths a writing command writes to, or None when the command does not write."""
    pos = [a for a in args if not a.startswith("-") and "://" not in a]
    if head in COPIES:
        dest = [args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-t", "--target-directory")]
        dest += [a.split("=", 1)[1] for a in args if a.startswith("--target-directory=")]
        dest = dest or pos[-1:]
        sources = [a for a in pos if a not in dest]
        landed = [os.path.join(d, os.path.basename(s.rstrip("/"))) for d in dest for s in sources]
        return dest + landed + (sources if head == "mv" else [])
    if head == "tar":
        mode = args[:1] + [a for a in args if a.startswith("-")]
        return pos if any(a == "--extract" or re.fullmatch(r"-?[A-Za-z]*x[A-Za-z]*", a) for a in mode) else None
    if head == "git":
        return pos if git_subcommand(args) in GIT_WRITE else None
    if head == "gh":
        return pos if args[:2] == ["repo", "clone"] else None
    if head in ("sed", "perl"):
        return pos if any(a == "--in-place" or re.fullmatch(r"-[A-Za-z]*i\S*", a) for a in args) else None
    return pos if head in WRITES_ANY_ARG else None


def argv_reason(argv: list[str], redirects: list[str], cwd: str, depth: int) -> str | None:
    head, args = os.path.basename(argv[0]), argv[1:]
    name = head.split("@", 1)[0]
    if name == "skills":
        return skills_reason(args)
    if name == "add-skill":
        src = next((a for a in args if not a.startswith("-")), "(no source given)")
        return f"`add-skill` installs skills from {src} into agent skill directories."
    if head in ("claude", "claude-code"):
        rest = [a for a in args if not a.startswith("-")]
        return plugin_reason(args[args.index(rest[0]) + 1:]) if rest[:1] in (["plugin"], ["plugins"]) else None
    if head in SHELLS and depth < 3:
        i = next((i for i, a in enumerate(args[:-1]) if SHELL_C.fullmatch(a)), None)
        if i is not None:
            return command_reason(args[i + 1], depth + 1)
    if head == "find":
        roots = []
        for a in args:
            if a.startswith(("-", "(", "!")):
                break
            roots.append(resolve(cwd, a))
        if "-delete" in args:
            hit = next((r for r in roots if in_skill_dir(r)), None)
            return f"`find -delete` removes files in a skill directory: {hit}" if hit else None
        flag = next((f for f in ("-exec", "-execdir", "-ok", "-okdir") if f in args), None)
        sub = [roots[0] if a == "{}" and roots else a for a in args[args.index(flag) + 1:]] if flag else []
        return argv_reason(sub, [], cwd, depth + 1) if sub and depth < 3 else None
    hit = next((t for t in (resolve(cwd, r) for r in redirects) if in_skill_dir(t)), None)
    if hit:
        return f"a redirection writes into a skill directory: {hit}"
    paths = written_paths(head, args)
    if paths is None:
        return None
    if cwd and in_skill_dir(cwd):
        return f"`{head}` writes inside a skill directory: {cwd}"
    hit = next((p for p in (resolve(cwd, a) for a in paths) if in_skill_dir(p)), None)
    return f"`{head}` writes into a skill directory: {hit}" if hit else None


def command_reason(cmd: str, depth: int = 0) -> str | None:
    code, scripts, _ = scan(cmd)
    for script in scripts if depth < 3 else []:
        reason = command_reason(script, depth + 1)
        if reason:
            return reason
    cwd = ""
    for argv, redirects in segments(code):
        argv = effective_argv(argv)
        if not argv:
            continue
        if os.path.basename(argv[0]) in ("cd", "pushd"):
            cwd = resolve(cwd, next((a for a in argv[1:] if not a.startswith("-")), "~"))
            continue
        reason = argv_reason(argv, redirects, cwd, depth)
        if reason:
            return reason
    return None


def file_reason(tool: str, inp: dict) -> str | None:
    path = str(inp.get("file_path") or inp.get("notebook_path") or "")
    if not path:
        return None
    if in_skill_dir(path):
        return f"{tool} {path} writes into a skill or plugin directory."
    if SETTINGS_FILE.search(os.path.normpath(path)):
        edits = inp.get("edits")
        edits = edits if isinstance(edits, list) else []
        text = " ".join(str(e.get("new_string", "")) for e in edits if isinstance(e, dict))
        if PLUGIN_KEYS.search(f"{inp.get('content') or ''} {inp.get('new_string') or ''} {text}"):
            return f"{tool} {path} changes enabled plugins or plugin marketplaces."
    return None


def main() -> None:
    try:
        d = json.load(sys.stdin)
    except Exception:
        return
    tool, inp = d.get("tool_name"), d.get("tool_input") or {}
    if tool == "Bash":
        reason = command_reason(str(inp.get("command") or ""))
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        reason = file_reason(tool, inp)
    else:
        return
    if reason:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": (
                f"Persistent skill/plugin change: {reason} Approve only if you decided to keep it; "
                "`npx skills use <owner/repo>@<skill>` runs a skill once without installing it. "
                "(skill-install-guard; remove it from ~/.claude/settings.json to disable.)")}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
