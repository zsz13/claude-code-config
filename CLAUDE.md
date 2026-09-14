# Working in this repository

This repository publishes an AI-agent configuration. The files in it are
*inert copies* — editing `hooks/read-budget-advisor.py` here changes nothing on
any machine until someone runs the installer.

## What this repo is

- `rules/`, `skills/`, `agents/`, `hooks/`, `bin/` — the configuration itself,
  copied from a working installation and published as-is.
- `config/`, `examples/` — sanitized templates.
- `docs/`, `workflows/` — the reasoning. These are the point of the repository;
  a change to behavior that does not update them is half a change.
- `scripts/` — installer and verifier.

## Rules for changes here

**Never touch a live installation.** Nothing in this repository may read from or
write to `~/.claude`, `~/.codex`, `~/.config/ponytail`, or any other live
AI-tool configuration. Test the installer against a temporary directory with
`--target`, never against a real config directory:

```bash
./scripts/install.sh --target /tmp/test-home/.claude --apply
./scripts/verify.sh  --target /tmp/test-home/.claude
```

**Run the verifier before committing.**

```bash
./scripts/verify.sh --repo-only
```

It checks that shell scripts parse, Python compiles, JSON and TOML parse, skills
and agents have `name`/`description` frontmatter, every rule declares a `paths:`
glob list, every relative markdown link resolves, no absolute home path or email
address is present, and that every hook command in `settings.example.json`
points at a file this repository actually ships.

**Nothing machine-specific.** No `/Users/...`, no `/home/...`, no usernames, no
email addresses, no private repository names, no hostnames, no tokens. Use
`$HOME`, `~/github`, `YOUR_USERNAME`, `YOUR_REPOSITORY`, `YOUR_API_KEY`. The
verifier enforces this, but it only catches the patterns it knows.

**Every rule needs `paths:` frontmatter.** A rule without it costs exactly what
`CLAUDE.md` costs, with an extra layer of indirection. If it should always load,
it belongs in `examples/CLAUDE.example.md` instead.

**Authorship is the repository owner's.** This configuration is discussed in
terms of the tools it configures — Claude Code, Codex, Ponytail, Superpowers and
the rest — because that is what it is *about*. That is not the same as
attribution. Never add a line, trailer, badge, comment or notice claiming that
an AI system authored, co-authored, generated, wrote or created any part of
this repository, and never list one as an author, contributor, copyright holder
or maintainer. The MIT copyright holder is `zsz13`. `scripts/verify.sh`
enforces this.

**Do not redistribute third-party code.** Plugins, vendored hooks and vendored
skills belong to their projects and keep their own licences — some of which
forbid redistribution here. Reference and configure them; never copy them in.

**Keep the evidence classes honest.** `docs/benchmarks.md` distinguishes
measured, observed, rationale, hypothesis and not-proven. Do not promote a claim
up that ladder without the measurement that justifies it, and do not add a
number that is not reproducible from data a reader can inspect.

## Conventions

- Conventional Commits (`feat:`, `docs:`, `fix:`, `chore:`).
- Shell: POSIX `sh` for the hook wrappers, `bash` for the scripts; classifiers
  and tools in Python 3.11+ with only the standard library.
- Hooks fail open. The only exceptions are the two deny-guards, which fail open
  on a parse error and deny only on a positive match.
- Documentation says *why*, not just *what*. A component without a rationale in
  `docs/` is undocumented no matter how many comments it has.
