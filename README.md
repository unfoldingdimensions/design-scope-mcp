# design-scope

A curated **201-card design reference library** with natural-language style
search, capture tooling, and a local MCP server. Free, local, private — no
subscription, no cloud, no analytics.

Every card is a real site's design captured as a 4-layer profile:
**fingerprint** (measured tokens: colors, type, spacing, radii) · **semantic**
(named tokens, design intent, z-index, responsive rules) · **annotation**
(LLM design intelligence: vibe, what works, search terms) · **behavior**
(hover diffs, scroll triggers, interaction model).

```bash
# search the library in plain English
python library/style_search.py "warm minimal serif"

# or through the MCP server, from any agent
# → mcp__design_scope__style_search(query="editorial but not brutalist")
```

## Why

Reference libraries like mobbin are paid and closed. design-scope is the
open alternative: capture any site you like, search the curated 201-card
library by *design qualities* instead of by brand, and let any agent borrow
concrete palettes and patterns — all on your own machine.

## What's in the box

| Layer | Ships in repo | Regenerates locally |
|---|---|---|
| `library/cards/` — 201 cards: card.md, fingerprint, semantic, annotation, behaviors | ✅ ~9 MB intelligence layer | — |
| `library/index.json` + `style-index.json` | ✅ | `python library/style_index.py` |
| `docs/design-tests/` + `docs/dogfood-app/` — demo artifacts | ✅ | — |

The library works with media missing: search, filter, compare, and theme
borrowing all function from the intelligence layer alone.

## Install

```bash
git clone git@github.com:unfoldingdimensions/design-scope-mcp.git
cd design-scope-mcp
pip install -r requirements.txt
playwright install chromium
```

Python 3.11+. Tested on Windows and Linux (CI runs both).

**Capture also needs Node.js.** `capture.py` shells out to `npx -y dembrandt`
for design-token extraction. Searching, filtering, comparing and theme borrowing
need no Node — only capturing new cards or regenerating media does. Without it a
capture still produces screenshots, but `fingerprint.json` will be empty.

## Quickstart

**Search the library** (CLI or via any MCP client):

```bash
python library/style_search.py "funky"
python library/style_search.py "editorial but not brutalist"
python library/style_search.py --json "dark minimal serif"
```

**Capture a new card:**

```bash
python library/capture.py --url https://stripe.com --name Stripe --category fintech
# batch from a seed file:
python library/capture.py seed-batch-1.json --limit 5
```

**Rebuild media for cards that lost it (e.g. fresh clone):**

```bash
python library/regenerate_media.py            # cards missing media only
python library/regenerate_media.py --fast     # skip motion/behavior passes
```

**Annotate cards with the LLM intelligence pass** (optional, needs
`NVIDIA_API_KEY`):

```bash
python library/annotate.py
```

## MCP server

Run the server locally and use its 9 tools from Claude Code, Cursor, Hermes,
or any MCP client:

```bash
# stdio (recommended)
python library/mcp_server.py

# or HTTP (streamable)
cd library && uvicorn mcp_server:app --host 127.0.0.1 --port 8232
```

Register with Claude Code: `claude mcp add design-scope -- python "<path-to-repo>/library/mcp_server.py"`
(see `docs/mcp.md` for Cursor `.mcp.json` and Hermes config).

| tool | args | returns |
|---|---|---|
| `ping` | — | health: ok + card count, or startup problems |
| `style_search` | `query`, `top_n` | ranked cards — natural language: `"funky"`, `"editorial but not brutalist"`, `"warm minimal"` |
| `style_filter` | vector fields, `archetype`, `max_results` | structured filter (hue/brightness/saturation/corners/flatness/type_mood) |
| `card_get` | `slug` | full card: fingerprint + semantic + annotation + behaviors + absolute asset paths |
| `card_compare` ⚠️ | `slug`, `project_dir` | borrow candidates vs the project's fingerprint |
| `theme_borrow` ⚠️ | `slug`, `target_dir` | token remap + contrast-guarded CSS (WCAG AA) |
| `capture` | `url`, `name`, `category`, `slug`, `fast`, `why` | **job_id** (async, never blocks) |
| `capture_status` | `job_id` | queued / running / done / failed |
| `recommend_history` | `project_dir` | the design-scope iteration chain (manifest.json) |

`card_compare` and `theme_borrow` work out of the box: they import `compare.py` /
`theme.py`, which ship with this repo in `scripts/` (mirrored from the
design-scope skill). Point `DESIGN_SCOPE_SKILL_SCRIPTS` at your own copies to
override. See [docs/OSS.md](docs/OSS.md).

Errors are returned as structured JSON (`{"error": ..., "hint": ...}`) — MCP
has no error types.

### Environment variables

| var | meaning |
|---|---|
| `DESIGN_SCOPE_LIBRARY` | override the library root (default: the repo's `library/`). Honored by every module. |
| `DESIGN_SCOPE_SKILL_SCRIPTS` | override for where `compare.py`/`theme.py` live. Default resolution: env → installed design-scope skill → the repo's own `scripts/` (ships both files). |
| `NVIDIA_API_KEY` | key for the LLM annotation pass (`annotate.py`). |
| `HERMES_ENV` | optional path to a `.env` file to read `NVIDIA_API_KEY` from. |

## Showcase + verdict

`showcase/index.html` is the project's sheet one-pager — built and graded with
itself. Every figure on it is counted from the library at build time, and the
page is graded by the same scored rubric your agent gets:

```bash
python scripts/build_showcase.py      # inject fresh stats + latest verdict + ledger
python scripts/verdict.py showcase/index.html --label "R1" \
    --ledger showcase/verdicts.json --json showcase/verdict.json
python scripts/build_showcase.py      # rebuild: rubric + ledger rows real
```

`verdict.py` measures the rendered DOM against six checks (band allocation,
mechanism budget, palette conformance, fabric floor, reduced motion, living
artefacts) and appends PASS/UNDER rows to a ledger that is never edited after
it lands — the ledger keeps its failures. Exit code = number of UNDER rows.

## Repository layout

```
library/
├── mcp_server.py        # the MCP server (stdio + HTTP)
├── capture.py           # capture pipeline (screenshots, tokens, motion)
├── annotate.py          # LLM design-intelligence pass
├── semantic_pass.py     # named tokens, design intent, z-index, responsive
├── behavior_pass.py     # hover diffs, scroll triggers, interaction model
├── style_index.py       # rebuild style-index.json from cards
├── style_search.py      # natural-language search CLI
├── regenerate_media.py  # rebuild gitignored media locally
├── gallery.py           # HTML gallery generator
├── backfill.py          # motion/behavior/semantic backfill for old cards
├── index.json           # card registry (204 cards)
├── style-index.json     # searchable style vectors + archetypes + tags
└── cards/<slug>/        # per-card intelligence layer
scripts/
├── verdict.py           # scored 6-check rubric reviewer (PASS/UNDER + ledger)
├── stats.py             # corpus numbers counted fresh from the library
├── build_showcase.py    # inject stats + verdict + ledger into showcase/index.html
├── compare.py           # borrow candidates (card fingerprint vs project)
└── theme.py             # token remap + contrast-guarded CSS
showcase/
├── index.template.html  # the sheet one-pager (both themes, self-contained)
├── index.html           # built artifact — open this
└── verdicts.json        # the ledger: every verdict, never edited after it lands
docs/
├── mcp.md               # MCP server reference
└── OSS.md               # packaging + regeneration documentation
tests/                   # smoke test + unit suites (no framework needed)
```

## Tests

```bash
python tests/client_smoke.py                  # real stdio MCP transport + error paths
python tests/client_smoke.py --queue          # in-process capture queue mock (no network)
python tests/test_style_search.py             # search layer unit tests
python tests/test_semantic_pass.py            # classifier + vocabulary guard
python tests/test_style_index.py              # vectors/hue boundaries (temp fixture)
python tests/test_behavior_pass.py            # hover-diff regression guard
python tests/test_vocabulary_consistency.py   # producers ⊆ search vocabulary
```

The unit suites and the queue mock run in CI on every push, on both
ubuntu-latest and windows-latest. Shared plumbing lives in `tests/_harness.py`.

## Data provenance

Cards describe the *design* of third-party sites — factual metadata
(color tokens, typography, layout measurements, interaction behavior) plus
LLM annotations that deliberately avoid brand commentary. design-scope has no
affiliation with any captured site; screenshots and motion media are
regenerated locally and never shipped in the repo. If you capture a site,
respect its terms of use.

## Contributing

Issues and PRs welcome. Good first contributions: capturing a missing
category, improving the search vocabulary, or adding a test. Keep changes
additive and non-destructive — the library is data, not a build artifact.

## License

MIT — see [LICENSE](LICENSE).
