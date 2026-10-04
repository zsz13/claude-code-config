# Visual energy and reference-led probe

Evidence for [benchmarks §8](../../benchmarks.md#visual-energy-and-reference-led-probes-2026-10-01).
Run 2026-10-01 on Claude Code 2.1.286. Per-run data and every redesign reply are
in [visual-energy-probes.json](visual-energy-probes.json).

## What it checks

For a major redesign, with the direction gate in `frontend-quality` and steps 4
and 5 of `design-brief`:

1. The reply proposes three directions, each with all four scores (visual
   energy, density, motion, reference fidelity).
2. No two directions share an energy level.
3. At least one direction is reference-led: built on one or two references,
   fidelity high.
4. That direction's adaptation list covers all six aspects: composition,
   hierarchy, spacing rhythm, interaction model, motion, visual treatment.
5. No product file is written before the user chooses.

For a trivial fix: no frontend skill loads, and the run makes the one edit asked
for.

Two cells were added after a blind review of the first results, with these
criteria fixed before they ran:

- **After the choice (P).** A fresh redesign run, resumed twice as forks of
  that session. One fork says "Go with the reference-led direction", the other
  "Go with the most restrained of the three directions". Both go on: "Write the
  plan, and stop before changing any files: I'll approve the plan before you
  build." A fork passes when its plan meets each of these that applies:
  - answers the pre-build questions, 1 to 5 and the visual-energy questions 6
    to 11;
  - for the reference-led choice, keeps each aspect its Adapts list took, or
    names a reason other than "simpler to build";
  - for the restrained choice, keeps the direction's energy rather than
    revising it upward.
  No product file may be written.
- **Established system (E).** The fixture plus a `DESIGN-BRIEF.md` naming a
  "lending ledger" direction, with matching tokens in `src/App.css`, and the
  prompt "Add a Borrowers page that lists each borrower and how many packets
  they currently have out." The run passes when the gate does not fire (no
  three directions, no scores) and the page is built in the brief's style.

Criteria 1 to 5 come from the request that asked for the change, and were
written before any run. The skill text was revised three times after seeing
runs; [benchmarks §8](../../benchmarks.md#visual-energy-and-reference-led-probes-2026-10-01)
says what each revision changed and why. Criteria 1 to 4 were scored by one
person (the one who made the change) from the reply text. Criterion 5 and the
trivial-fix checks come from the transcripts and from `git status` in each
run's fixture copy.

## Fixture

Seedkeep, a three-file React app with no design system. The configuration under
test goes in its project `.claude/`: this repository's `skills/`, `agents/` and
`rules/`, copied as they stand.

`README.md`:

```
# Seedkeep

Lending tracker for a neighbourhood seed library. Volunteers record which seed
packets are on loan, to whom, and whether the borrower returned saved seed at
the end of the season. Run with `npm run dev`.
```

`package.json`:

```json
{ "name": "seedkeep", "private": true, "type": "module",
  "scripts": { "dev": "vite", "build": "vite build" },
  "dependencies": { "react": "^19.0.0", "react-dom": "^19.0.0" },
  "devDependencies": { "vite": "^7.0.0", "@vitejs/plugin-react": "^5.0.0" } }
```

`index.html`:

```html
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Seedkeep</title></head>
<body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>
```

`src/main.jsx`:

```jsx
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./App.css";
createRoot(document.getElementById("root")).render(<App />);
```

`src/App.jsx`:

```jsx
import { useState } from "react";

const INITIAL = [
  { id: 1, variety: "Cherokee Purple tomato", borrower: "R. Okafor", out: "2026-03-14", returned: false },
  { id: 2, variety: "Dragon tongue bean", borrower: "M. Lindqvist", out: "2026-04-02", returned: true },
  { id: 3, variety: "Lemon cucumber", borrower: "A. Haddad", out: "2026-04-20", returned: false },
];

export default function App() {
  const [loans, setLoans] = useState(INITIAL);
  const [query, setQuery] = useState("");
  const shown = loans.filter((l) => l.variety.toLowerCase().includes(query.toLowerCase()));
  const markReturned = (id) => setLoans(loans.map((l) => (l.id === id ? { ...l, returned: true } : l)));
  return (
    <div className="app">
      <header className="header"><h1>Seedkeep</h1></header>
      <main className="container">
        <input className="search" placeholder="Search varieties" value={query} onChange={(e) => setQuery(e.target.value)} />
        <div className="grid">
          {shown.map((l) => (
            <div className="card" key={l.id}>
              <h2>{l.variety}</h2>
              <p>{l.borrower} · since {l.out}</p>
              <span className={l.returned ? "pill ok" : "pill"}>{l.returned ? "Returned" : "On loan"}</span>
              {!l.returned && <button onClick={() => markReturned(l.id)}>Return</button>}
            </div>
          ))}
        </div>
      </main>
      <footer className="footer"><small>© 2026 Seedkeep volunteers</small></footer>
    </div>
  );
}
```

`src/App.css`:

```css
body { margin: 0; font-family: system-ui, sans-serif; background: #f3f4f6; color: #111827; }
.header { background: #fff; padding: 16px 24px; border-bottom: 1px solid #e5e7eb; }
.container { max-width: 960px; margin: 0 auto; padding: 24px; }
.search { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; margin-bottom: 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.card { background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.pill { display: inline-block; padding: 2px 10px; border-radius: 999px; background: #fef3c7; font-size: 12px; }
.pill.ok { background: #d1fae5; }
button { margin-left: 8px; background: #4f46e5; color: #fff; border: 0; border-radius: 8px; padding: 6px 12px; }
.footer { text-align: center; padding: 24px; }
.footer small { font-size: 11px; color: #6b7280; }
```

The established-system cell (E) adds two things to this fixture.
`src/App.jsx` is unchanged, and still uses the card markup the brief rules out.

`DESIGN-BRIEF.md`:

```
# Seedkeep design brief

# Product            Lending tracker for a neighbourhood seed library.
# Visual direction   "Lending ledger": ruled rows on off-white paper, no cards, hairline rules.
# Typography roles   Serif (Georgia stack) for variety names; tabular monospace for dates and counts; system sans for labels.
# Color roles        --paper #faf7f0, --ink #1f2a24, --rule #d8d2c4, --stamp #b4432b (returned stamp only).
# Signature element  A "RETURNED" rubber stamp on returned rows.
# Anti-goals         Card grids, pills, gradients, purple.
```

`src/App.css`, in place of the one above:

```css
:root { --paper:#faf7f0; --ink:#1f2a24; --rule:#d8d2c4; --stamp:#b4432b; --serif: Georgia, "Times New Roman", serif; --mono: ui-monospace, Menlo, monospace; }
body { margin:0; background:var(--paper); color:var(--ink); font-family: system-ui, sans-serif; }
.ledger { max-width: 980px; margin: 0 auto; padding: 32px 20px; }
.ledger h1 { font-family: var(--serif); font-weight: 400; font-size: 32px; border-bottom: 2px solid var(--ink); padding-bottom: 8px; }
.row { display:grid; grid-template-columns: 2fr 1.2fr 1fr auto; gap: 16px; padding: 12px 0; border-bottom: 1px solid var(--rule); align-items: baseline; }
.row .variety { font-family: var(--serif); font-size: 18px; }
.row .date { font-family: var(--mono); font-variant-numeric: tabular-nums; }
.stamp { font-family: var(--mono); color: var(--stamp); border: 2px solid var(--stamp); padding: 0 6px; transform: rotate(-4deg); display:inline-block; }
```

## Harness

Each run gets a fresh copy of the fixture as a git repository in a writable
temporary directory, so a write shows in `git status`. `--setting-sources
project,local` keeps user-level skills, rules, hooks, plugins and user-scope MCP
servers out, so only the copied configuration loads. That also leaves every
research server out, so a reference-led direction can only take the no-tool
form. Connecting one would need a `--mcp-config` file with its credentials;
these runs had none.

```bash
# run.sh CONFIG_DIR NAME PROMPT
# CONFIG_DIR holds skills/ agents/ rules/; FIXTURE holds the files above.
D="$PROBE_ROOT/$2"; mkdir -p "$D"
cp -R "$FIXTURE"/. "$D"/
mkdir -p "$D/.claude"; cp -R "$1/skills" "$1/agents" "$1/rules" "$D/.claude/"
( cd "$D" && git init -q && git add -A && git commit -qm fixture )
cd "$D" && claude -p "$3" --setting-sources project,local \
  --permission-mode acceptEdits --max-turns 40 --output-format stream-json --verbose \
  --disallowedTools mcp__21st__get_component mcp__gitnexus \
  > "$LOGS/$2.jsonl" 2> "$LOGS/$2.err"
# P cell only: fork the session once per choice, in the same directory.
SID=$(jq -r 'select(.type=="result") | .session_id' "$LOGS/$2.jsonl")
claude -p "$CHOICE_PROMPT" --resume "$SID" --fork-session <same flags as above> \
  > "$LOGS/$2-$CHOICE.jsonl"
```

## Prompts

| Kind | Prompt |
|---|---|
| Redesign 1 | Completely rethink Seedkeep's frontend visual design and UX while preserving its existing functionality. |
| Redesign 2 | Seedkeep needs a major redesign: a whole new look and layout for the app. Go ahead and build it. |
| Trivial 1 | The footer copyright text is too small to read. Bump it to 14px. |
| Trivial 2 | The button on each loan says 'Return'. Change its label to 'Mark returned'. |
| P, reference-led choice (resumed) | Go with the reference-led direction. Write the plan, and stop before changing any files: I'll approve the plan before you build. |
| P, restrained choice (resumed) | Go with the most restrained of the three directions. Write the plan, and stop before changing any files: I'll approve the plan before you build. |
| E | Add a Borrowers page that lists each borrower and how many packets they currently have out. |

Redesign 2 says "build it" on purpose: the gate's text says that asks for the
result, not for skipping the choice.

## Result

| Text | Redesign proposals | Criteria 1 to 5 all met | Trivial runs as expected |
|---|---|---|---|
| Baseline (the gate before this change) | 4 | 0/4: no scores, no reference-led direction; no writes | not run |
| Text 1 | 4 | 0/4: criteria 1, 2, 3 and 5 met in all four; criterion 4 in none (three or four of the six aspects) | 2/2 |
| Text 2 | 2 | 0/2: one had no fidelity scores and no adaptation list; the other gave fidelity in words, and its reference-led direction had three sources | not run |
| Text 3 | 4 | 4/4 | 2/2 |
| Final (published) | 4 | 3/4: one left fidelity off its two other directions | 2/2 |

On the final text, the P cell's four plans passed 4/4 and the E cell passed
2/2. Three sentences in the step after the choice were added after every run;
[benchmarks §8](../../benchmarks.md#visual-energy-and-reference-led-probes-2026-10-01)
names them. Per-run detail, including how each run reached `design-brief`, is in
[visual-energy-probes.json](visual-energy-probes.json).

What the probe does not cover is in
[benchmarks §8](../../benchmarks.md#visual-energy-and-reference-led-probes-2026-10-01).
