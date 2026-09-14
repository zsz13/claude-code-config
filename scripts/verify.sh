#!/usr/bin/env bash
# Verify an installation (or this repository itself).
#
# Read-only: this script never writes, moves, or deletes anything.
#
# Usage: scripts/verify.sh [--target DIR] [--components a,b,c] [--repo-only]
# Exit:  0 = all checks passed, 1 = at least one failure.

set -uo pipefail

REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
COMPONENTS="hooks bin agents rules skills settings"
REPO_ONLY=0
pass=0; fail=0; warn=0

c_reset=""; c_red=""; c_grn=""; c_ylw=""; c_bold=""
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  c_reset=$'\033[0m'; c_red=$'\033[31m'; c_grn=$'\033[32m'; c_ylw=$'\033[33m'; c_bold=$'\033[1m'
fi

ok()   { printf '  %sPASS%s  %s\n' "$c_grn" "$c_reset" "$1"; pass=$((pass+1)); }
bad()  { printf '  %sFAIL%s  %s\n' "$c_red" "$c_reset" "$1"; fail=$((fail+1)); }
note() { printf '  %sWARN%s  %s\n' "$c_ylw" "$c_reset" "$1"; warn=$((warn+1)); }

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:?--target needs a value}"; shift 2 ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    --components) COMPONENTS="$(printf '%s' "${2:?}" | tr ',' ' ')"; shift 2 ;;
    --components=*) COMPONENTS="$(printf '%s' "${1#*=}" | tr ',' ' ')"; shift ;;
    --repo-only) REPO_ONLY=1; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) printf 'verify.sh: unknown option %s\n' "$1" >&2; exit 2 ;;
  esac
done

printf '\n%sVerifying repository: %s%s\n\n' "$c_bold" "$REPO" "$c_reset"

# ---------- repository-side checks ----------

printf 'Shell scripts parse:\n'
while IFS= read -r f; do
  if bash -n "$f" 2>/dev/null; then ok "${f#"$REPO"/}"; else bad "${f#"$REPO"/} — bash -n failed"; fi
done < <(find "$REPO" -name '*.sh' -not -path '*/.git/*' | sort)

printf '\nPython scripts compile:\n'
while IFS= read -r f; do
  # compile() rather than py_compile: writes no __pycache__ into the tree
  if python3 -c 'import sys; compile(open(sys.argv[1]).read(), sys.argv[1], "exec")' "$f" 2>/dev/null; then
    ok "${f#"$REPO"/}"
  else
    bad "${f#"$REPO"/} — does not compile"
  fi
done < <( { find "$REPO" -name '*.py' -not -path '*/.git/*'; printf '%s\n' "$REPO/bin/run-captured"; } | sort -u)

printf '\nJSON examples parse:\n'
while IFS= read -r f; do
  if python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f" 2>/dev/null; then ok "${f#"$REPO"/}"; else bad "${f#"$REPO"/} — invalid JSON"; fi
done < <(find "$REPO" -name '*.json' -not -path '*/.git/*' | sort)

printf '\nTOML examples parse:\n'
while IFS= read -r f; do
  if python3 -c 'import tomllib,sys; tomllib.load(open(sys.argv[1],"rb"))' "$f" 2>/dev/null; then ok "${f#"$REPO"/}"; else bad "${f#"$REPO"/} — invalid TOML"; fi
done < <(find "$REPO" -name '*.toml' -not -path '*/.git/*' | sort)

printf '\nSkills and agents have YAML frontmatter with name + description:\n'
while IFS= read -r f; do
  if head -1 "$f" | grep -q '^---$' && sed -n '2,12p' "$f" | grep -q '^name:' && sed -n '2,12p' "$f" | grep -q '^description:'; then
    ok "${f#"$REPO"/}"
  else
    bad "${f#"$REPO"/} — missing frontmatter name/description"
  fi
done < <( { find "$REPO/skills" -name 'SKILL.md'; find "$REPO/agents" -name '*.md'; } 2>/dev/null | sort)

printf '\nPath-scoped rules declare a paths: glob list:\n'
while IFS= read -r f; do
  if head -1 "$f" | grep -q '^---$' && sed -n '2,40p' "$f" | grep -q '^paths:'; then
    ok "${f#"$REPO"/}"
  else
    bad "${f#"$REPO"/} — a rule without paths: costs as much as CLAUDE.md"
  fi
done < <(find "$REPO/rules" -name '*.md' 2>/dev/null | sort)

printf '\nNo personal filesystem paths or identifiers:\n'
# A path or address that names a real machine or person must never ship. The
# documented placeholders (/Users/<name>, /Users/... inside a prose rule) are
# the only tolerated forms, so match a real lowercase login rather than the
# placeholder, and exclude this script's own pattern definitions.
leak=$(grep -rIn -E '/Users/[a-z]|/home/[a-z]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' \
        "$REPO" --exclude-dir=.git --exclude-dir=__pycache__ 2>/dev/null \
        | grep -vE '^[^:]*/(verify|install)\.sh:|/Users/(<name>|\.\.\.)' || true)
if [ -z "$leak" ]; then ok "no absolute home paths or email addresses"; else
  bad "found machine-specific strings:"; printf '%s\n' "$leak" | sed 's/^/        /'
fi

printf '\nNo AI authorship or generation attribution:\n'
# This repository is authored by its owner. Tooling is discussed on its merits;
# nothing here may claim an AI wrote, generated, or co-authored it.
attrib=$(grep -rIn -E 'Co-[Aa]uthored-[Bb]y|Claude-Session|[Gg]enerated (with|by) (Claude|AI|Codex|GPT)|[Mm]ade (with|by) (Claude|AI)|[Ww]ritten by (Claude|AI)|[Cc]reated by (Claude|AI)|AI-generated' \
        "$REPO" --exclude-dir=.git --exclude-dir=__pycache__ 2>/dev/null \
        | grep -vE '^[^:]*/verify\.sh:' || true)
if [ -z "$attrib" ]; then ok "no AI authorship or generation attribution"; else
  bad "found authorship attribution:"; printf '%s\n' "$attrib" | sed 's/^/        /'
fi

printf '\nEvery documentation link resolves:\n'
broken=0
while IFS= read -r f; do
  d="$(dirname "$f")"
  while IFS= read -r link; do
    [ -z "$link" ] && continue
    case "$link" in http*|'#'*|mailto:*) continue ;; esac
    t="${link%%#*}"; [ -z "$t" ] && continue
    if [ ! -e "$d/$t" ]; then bad "${f#"$REPO"/} -> $t"; broken=$((broken+1)); fi
  done < <(grep -oE '\]\([^)]+\)' "$f" | sed 's/^](//; s/)$//')
done < <(find "$REPO" -name '*.md' -not -path '*/.git/*' | sort)
[ "$broken" -eq 0 ] && ok "all relative markdown links resolve"

printf '\nSettings example is self-consistent:\n'
python3 - "$REPO" <<'PY'
import json, pathlib, re, sys
repo = pathlib.Path(sys.argv[1])
s = json.loads((repo / "config/settings.example.json").read_text())
missing, checked = [], 0
for event, entries in s.get("hooks", {}).items():
    for entry in entries:
        for h in entry.get("hooks", []):
            cmd = h.get("command", "")
            m = re.search(r"\$HOME/\.claude/([^\s']+)", cmd)
            if not m:
                continue
            checked += 1
            if not (repo / m.group(1)).exists():
                missing.append(f"{event}: {m.group(1)}")
if missing:
    print("  \033[31mFAIL\033[0m  settings.example.json references files this repo does not ship:")
    for m in missing:
        print("        " + m)
    sys.exit(1)
print(f"  \033[32mPASS\033[0m  all {checked} hook commands resolve to shipped files")
PY
if [ $? -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi

# ---------- installed-target checks ----------

if [ "$REPO_ONLY" -eq 0 ]; then
  printf '\n%sVerifying installation: %s%s\n\n' "$c_bold" "$TARGET" "$c_reset"
  if [ ! -d "$TARGET" ]; then
    note "target directory does not exist — nothing installed yet"
  else
    for c in $COMPONENTS; do
      case "$c" in
        hooks|bin|agents|rules|skills)
          src="$REPO/$c"
          [ -d "$src" ] || continue
          n_ok=0; n_missing=0; n_diff=0
          while IFS= read -r f; do
            rel="${f#"$src"/}"; dest="$TARGET/$c/$rel"
            if [ ! -e "$dest" ]; then n_missing=$((n_missing+1))
            elif cmp -s "$f" "$dest"; then n_ok=$((n_ok+1))
            else n_diff=$((n_diff+1)); fi
          done < <(find "$src" -type f -not -name '*.pyc' -not -name 'README.md' | sort)
          if [ "$n_missing" -eq 0 ] && [ "$n_diff" -eq 0 ]; then
            ok "$c — $n_ok/$n_ok files installed and identical"
          elif [ "$n_ok" -eq 0 ] && [ "$n_diff" -eq 0 ]; then
            note "$c — not installed ($n_missing files)"
          else
            bad "$c — $n_ok identical, $n_diff differ, $n_missing missing"
          fi
          if [ "$c" = "hooks" ] || [ "$c" = "bin" ]; then
            noexec=""
            while IFS= read -r f; do
              [ -e "$f" ] && [ ! -x "$f" ] && noexec="$noexec $(basename "$f")"
            done < <(find "$TARGET/$c" -type f -not -name 'README.md' 2>/dev/null | sort)
            if [ -n "$noexec" ]; then bad "$c — not executable:$noexec"; else ok "$c — all installed files are executable"; fi
          fi
          ;;
        settings)
          if [ ! -e "$TARGET/settings.json" ]; then
            note "settings.json — not present"
          elif python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$TARGET/settings.json" 2>/dev/null; then
            ok "settings.json — valid JSON"
            bads=$(python3 - "$TARGET" <<'PY'
import json, os, re, sys
t = sys.argv[1]
s = json.load(open(os.path.join(t, "settings.json")))
missing = []
for event, entries in s.get("hooks", {}).items():
    for entry in entries:
        for h in entry.get("hooks", []):
            for p in re.findall(r"(?:'([^']+)'|(\S*/\.?claude/hooks/\S+))", h.get("command", "")):
                path = p[0] or p[1]
                if "/hooks/" in path and not os.path.exists(os.path.expandvars(path)):
                    missing.append(path)
print("\n".join(sorted(set(missing))))
PY
)
            if [ -n "$bads" ]; then bad "settings.json — hook paths that do not exist:"; printf '%s\n' "$bads" | sed 's/^/        /'
            else ok "settings.json — every hook command resolves to an existing file"; fi
          else
            bad "settings.json — invalid JSON"
          fi
          if [ -e "$TARGET/settings.claude-code-config-proposed.json" ]; then
            note "a settings proposal file is waiting to be merged: $TARGET/settings.claude-code-config-proposed.json"
          fi
          ;;
      esac
    done
  fi
fi

printf '\n%sResult:%s %s%d passed%s, %s%d failed%s, %s%d warnings%s\n\n' \
  "$c_bold" "$c_reset" "$c_grn" "$pass" "$c_reset" "$c_red" "$fail" "$c_reset" "$c_ylw" "$warn" "$c_reset"
[ "$fail" -eq 0 ] || exit 1
exit 0
