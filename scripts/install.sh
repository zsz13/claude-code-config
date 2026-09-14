#!/usr/bin/env bash
# Install this configuration into a Claude Code (and optionally Codex) home.
#
# SAFE BY DEFAULT: does nothing unless you pass --apply. Never overwrites a file
# that differs without --force, and always backs up before it overwrites.
# Never merges into an existing settings.json.
#
# Usage:  scripts/install.sh [--apply] [--components a,b,c] [--force] [--target DIR]
# Run     scripts/install.sh --help   for the full option list.

set -euo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

APPLY=0
FORCE=0
TARGET="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CODEX_TARGET="${CODEX_HOME:-$HOME/.codex}"
BACKUP_DIR=""
ALL_COMPONENTS="hooks bin agents rules skills settings codex"
COMPONENTS="hooks bin agents rules skills settings"

n_install=0; n_skip=0; n_conflict=0; n_backup=0; n_manual=0

c_reset=""; c_red=""; c_grn=""; c_ylw=""; c_dim=""; c_bold=""
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  c_reset=$'\033[0m'; c_red=$'\033[31m'; c_grn=$'\033[32m'
  c_ylw=$'\033[33m'; c_dim=$'\033[2m'; c_bold=$'\033[1m'
fi

usage() {
  cat <<EOF
Install the claude-code-config configuration.

Options:
  --apply                 Actually write files. Without this, nothing is written
                          (dry run) and the plan is printed.
  --dry-run               Explicitly request the default dry-run behavior.
  --components LIST       Comma-separated subset to install.
                          Available: ${ALL_COMPONENTS// /, }
                          Default:   ${COMPONENTS// /, }
  --force                 Overwrite files whose contents differ from this
                          repository. A backup is still taken first.
  --target DIR            Claude config directory.
                          Default: \$CLAUDE_CONFIG_DIR, else \$HOME/.claude
                          (currently: $TARGET)
  --codex-target DIR      Codex config directory.
                          Default: \$CODEX_HOME, else \$HOME/.codex
  --backup-dir DIR        Where to put backups.
                          Default: <target>/backups/claude-code-config-<timestamp>
  --list                  List components and what each installs, then exit.
  -h, --help              This message.

Components:
  hooks     PreToolUse/PostToolUse/Stop guards and advisors -> <target>/hooks/
  bin       run-captured large-output helper                -> <target>/bin/
  agents    reviewer subagent definitions                   -> <target>/agents/
  rules     path-scoped language/stack rules                -> <target>/rules/
  skills    procedure skills                                -> <target>/skills/
  settings  settings.json  (ONLY if absent; otherwise a proposal file is
            written next to it and you merge it yourself)
  codex     Codex reviewer agent definitions                -> <codex-target>/agents/

Exit status: 0 if the plan is clean, 1 if any conflict needs your attention.
EOF
}

log()      { printf '%s\n' "$*"; }
plan_add() { printf '  %sADD%s      %s\n' "$c_grn" "$c_reset" "$1"; n_install=$((n_install+1)); }
plan_same(){ printf '  %sSAME%s     %s\n' "$c_dim" "$c_reset" "$1"; n_skip=$((n_skip+1)); }
plan_conf(){ printf '  %sCONFLICT%s %s\n' "$c_red" "$c_reset" "$1"; n_conflict=$((n_conflict+1)); }
plan_over(){ printf '  %sOVERWRITE%s %s %s(backed up)%s\n' "$c_ylw" "$c_reset" "$1" "$c_dim" "$c_reset"; n_backup=$((n_backup+1)); }
plan_man() { printf '  %sMANUAL%s   %s\n' "$c_ylw" "$c_reset" "$1"; n_manual=$((n_manual+1)); }

# back_up SRC REL — copy an existing target file into the backup tree
back_up() {
  local src="$1" rel="$2" dest
  dest="$BACKUP_DIR/$rel"
  if [ "$APPLY" -eq 1 ]; then
    mkdir -p "$(dirname "$dest")"
    cp -p "$src" "$dest"
  fi
}

# place SRC DEST REL MODE
place() {
  local src="$1" dest="$2" rel="$3" mode="$4"
  if [ ! -e "$dest" ]; then
    plan_add "$rel"
    if [ "$APPLY" -eq 1 ]; then
      mkdir -p "$(dirname "$dest")"
      cp "$src" "$dest"
      chmod "$mode" "$dest"
    fi
    return 0
  fi
  if cmp -s "$src" "$dest"; then
    plan_same "$rel"
    return 0
  fi
  if [ "$FORCE" -eq 1 ]; then
    plan_over "$rel"
    back_up "$dest" "$rel"
    if [ "$APPLY" -eq 1 ]; then
      cp "$src" "$dest"
      chmod "$mode" "$dest"
    fi
    return 0
  fi
  plan_conf "$rel  ${c_dim}(differs; use --force to overwrite, a backup is taken)${c_reset}"
  return 0
}

install_tree() {
  local srcdir="$1" destdir="$2" prefix="$3" mode="$4" pattern="$5"
  local f rel
  while IFS= read -r f; do
    rel="${f#"$srcdir"/}"
    place "$f" "$destdir/$rel" "$prefix/$rel" "$mode"
  done < <(find "$srcdir" -type f -name "$pattern" | sort)
}

# Render $HOME in the settings template to a real absolute path, so the installed
# hooks work regardless of whether the harness expands shell variables.
render_settings() {
  local out="$1"
  python3 - "$REPO/config/settings.example.json" "$TARGET" "$out" <<'PY'
import json, pathlib, sys
src, target, out = sys.argv[1], sys.argv[2], sys.argv[3]
text = pathlib.Path(src).read_text()
text = text.replace("$HOME/.claude", target.rstrip("/"))
json.loads(text)  # fail loudly rather than write invalid JSON
pathlib.Path(out).write_text(text)
PY
}

install_settings() {
  local dest="$TARGET/settings.json"
  local proposal="$TARGET/settings.claude-code-config-proposed.json"
  local tmp; tmp="$(mktemp)"
  render_settings "$tmp"
  if [ ! -e "$dest" ]; then
    plan_add "settings.json  ${c_dim}(rendered with absolute paths)${c_reset}"
    if [ "$APPLY" -eq 1 ]; then mkdir -p "$TARGET"; cp "$tmp" "$dest"; chmod 644 "$dest"; fi
  elif cmp -s "$tmp" "$dest"; then
    plan_same "settings.json"
  else
    plan_man "settings.json already exists and differs."
    printf '           %sWritten instead:%s settings.claude-code-config-proposed.json\n' "$c_dim" "$c_reset"
    printf '           %sMerge it yourself:%s diff settings.json settings.claude-code-config-proposed.json\n' "$c_dim" "$c_reset"
    if [ "$APPLY" -eq 1 ]; then mkdir -p "$TARGET"; cp "$tmp" "$proposal"; chmod 644 "$proposal"; fi
  fi
  rm -f "$tmp"
}

install_codex() {
  if [ ! -d "$REPO/config/codex/agents" ]; then return 0; fi
  install_tree "$REPO/config/codex/agents" "$CODEX_TARGET/agents" "codex:agents" 644 '*.toml'
  local dest="$CODEX_TARGET/config.toml"
  if [ -e "$dest" ]; then
    plan_man "codex:config.toml exists — not touched. Template: config/codex/config.example.toml"
  else
    plan_man "codex:config.toml absent — copy config/codex/config.example.toml yourself and review it first."
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --dry-run) APPLY=0; shift ;;
    --force) FORCE=1; shift ;;
    --components) COMPONENTS="$(printf '%s' "${2:?--components needs a value}" | tr ',' ' ')"; shift 2 ;;
    --components=*) COMPONENTS="$(printf '%s' "${1#*=}" | tr ',' ' ')"; shift ;;
    --target) TARGET="${2:?--target needs a value}"; shift 2 ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    --codex-target) CODEX_TARGET="${2:?--codex-target needs a value}"; shift 2 ;;
    --codex-target=*) CODEX_TARGET="${1#*=}"; shift ;;
    --backup-dir) BACKUP_DIR="${2:?--backup-dir needs a value}"; shift 2 ;;
    --backup-dir=*) BACKUP_DIR="${1#*=}"; shift ;;
    --list) printf '%s\n' $ALL_COMPONENTS; exit 0 ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'install.sh: unknown option %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

: "${BACKUP_DIR:=$TARGET/backups/claude-code-config-$(date +%Y%m%d-%H%M%S)}"

for c in $COMPONENTS; do
  case " $ALL_COMPONENTS " in
    *" $c "*) ;;
    *) printf 'install.sh: unknown component "%s" (available: %s)\n' "$c" "$ALL_COMPONENTS" >&2; exit 2 ;;
  esac
done

log ""
log "${c_bold}claude-code-config installer${c_reset}"
log "  source:       $REPO"
log "  claude target: $TARGET"
case " $COMPONENTS " in *" codex "*) log "  codex target:  $CODEX_TARGET" ;; esac
log "  components:   $COMPONENTS"
if [ "$APPLY" -eq 1 ]; then
  log "  mode:         ${c_ylw}APPLY — files will be written${c_reset}"
else
  log "  mode:         ${c_grn}DRY RUN — nothing will be written${c_reset} (pass --apply to install)"
fi
log ""
log "Plan:"

for c in $COMPONENTS; do
  case "$c" in
    hooks)
      install_tree "$REPO/hooks" "$TARGET/hooks" "hooks" 755 '*.sh'
      install_tree "$REPO/hooks" "$TARGET/hooks" "hooks" 755 '*.py'
      ;;
    bin)      install_tree "$REPO/bin"    "$TARGET/bin"    "bin"    755 '*' ;;
    agents)   install_tree "$REPO/agents" "$TARGET/agents" "agents" 644 '*.md' ;;
    rules)    install_tree "$REPO/rules"  "$TARGET/rules"  "rules"  644 '*.md' ;;
    skills)   install_tree "$REPO/skills" "$TARGET/skills" "skills" 644 '*.md' ;;
    settings) install_settings ;;
    codex)    install_codex ;;
  esac
done

log ""
log "Summary: ${c_grn}$n_install to add${c_reset}, $n_skip already identical, ${c_ylw}$n_backup to overwrite${c_reset}, ${c_red}$n_conflict conflicting${c_reset}, ${c_ylw}$n_manual needing manual action${c_reset}"

if [ "$n_backup" -gt 0 ] && [ "$APPLY" -eq 1 ]; then
  log "Backups: $BACKUP_DIR"
fi

if [ "$n_conflict" -gt 0 ]; then
  log ""
  log "${c_red}Conflicts found.${c_reset} Nothing was overwritten. Review the differences, then either"
  log "re-run with --force (each overwritten file is backed up first) or install a"
  log "narrower --components set."
  exit 1
fi

if [ "$APPLY" -eq 0 ]; then
  log ""
  log "Dry run complete. Re-run with ${c_bold}--apply${c_reset} to install."
else
  log ""
  log "Done. Verify with: scripts/verify.sh --target \"$TARGET\""
fi
exit 0
