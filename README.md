# design-scope

A curated **204-card design reference library** with a natural-language style
search, site capture tooling, and a local MCP server. Free, local, and
private: no subscription, no cloud, no analytics.

Every card is a real site's design captured as a four-layer profile:

- **fingerprint**: measured tokens (colors, typography, spacing, radii)
- **semantic**: named tokens, design intent, z-index layers, responsive rules
- **annotation**: LLM design intelligence (vibe, what works, search terms)
- **behavior**: hover diffs, scroll triggers, interaction model

```bash
# search the library in plain English
python library/style_search.py "warm minimal serif"

# or through the MCP server, from any agent
# style_search(query="editorial but not brutalist")
```

## Why

Reference libraries like Mobbin are paid and closed. design-scope is the open
alternative: capture any site you like, search the curated 204-card library
by design qualities instead of by brand, and let any agent borrow concrete
palettes and patterns. Everything runs on your own machine.

## What ships in the repo

| Layer | Ships in repo | Regenerates locally |
|---|---|---|
| `library/cards/` with 204 cards: card.md, fingerprint, semantic, annotation, behaviors | yes, about 9 MB of intelligence data | no |
| `library/index.json` and `style-index.json` | yes | `python library/style_index.py` |
| `docs/design-tests/` and `docs/dogfood-app/` demo artifacts | yes | no |

The library works with media missing. Search, filter, compare, and theme
borrowing all function from the intelligence layer alone. Screenshots and
motion media are gitignored and can be rebuilt locally at any time.

## Install

```bash
git clone git@github.com:unfoldingdimensions/design-scope-mcp.git
cd design-scope-mcp
pip install -r requirements.txt
playwright install chromium
```

Python 3.11 or newer. Tested on Windows and Linux; CI runs both.

**Capturing new cards also needs Node.js.** The capture pipeline shells out
to `npx -y dembrandt` for design-token extraction. Searching, filtering,
comparing, and theme borrowing need no Node. Without it, a capture still
produces screenshots, but the token extraction step is skipped.

## Quickstart

**Search the library** (CLI, no server needed):

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

**Rebuild media for cards that lost it (for example after a fresh clone):**

```bash
python library/regenerate_media.py            # cards missing media only
python library/regenerate_media.py --fast     # skip motion and behavior passes
```

**Annotate cards with the LLM intelligence pass** (optional, needs
`NVIDIA_API_KEY`):

```bash
python library/annotate.py
```

## Using the MCP server from an agent

The server speaks the Model Context Protocol (MCP) over stdio and over
streamable HTTP, so any MCP client can use it. It exposes 11 tools for
searching the library, borrowing design decisions, capturing new sites, and
grading pages. The server is read-only for your projects: it never edits
project source.

### Start the server

```bash
# stdio (recommended for agent harnesses)
python library/mcp_server.py

# or HTTP (streamable)
cd library && uvicorn mcp_server:app --host 127.0.0.1 --port 8232
```

Startup validation runs at import on both transports. If `index.json` or
`style-index.json` are missing, the server refuses to boot and prints the
exact fix command instead of failing per request later.

### Hermes

Add the server to your Hermes MCP config as a stdio server. The server entry
is the stdio command above. In the JSON shape most harnesses use:

```json
{
  "mcpServers": {
    "design-scope": {
      "command": "python",
      "args": ["<path-to-repo>/library/mcp_server.py"]
    }
  }
}
```

If the design-scope skill is installed in a Hermes profile, the server
automatically finds that skill's copies of `compare.py` and `theme.py`, so
`card_compare` and `theme_borrow` use the skill's versions. No configuration
is needed for that to happen.

### Claude Code

```bash
claude mcp add design-scope -- python "<path-to-repo>/library/mcp_server.py"
```

### Cursor

Add to `.mcp.json` in the project root:

```json
{"mcpServers": {"design-scope": {"command": "python",
  "args": ["<path-to-repo>/library/mcp_server.py"]}}}
```

### Any other harness

Any MCP client works. Use the stdio JSON snippet from the Hermes section
above with your client's config format, or point a streamable-HTTP client at
the uvicorn server on port 8232. The tool reference below is the full tool
surface; point your agent at it and let it call tools directly.

### A typical agent session

An agent building or restyling a page with design-scope usually runs this
loop:

1. `style_search` with a direction ("dark minimal serif") to rank candidate
   cards and pick one.
2. `card_get` on the chosen slug for the full four-layer profile, including
   absolute paths to screenshots and motion media.
3. `theme_borrow` to get a token remap and contrast-guarded CSS it can apply
   to the project.
4. `get_page_structure` and `get_section_blueprint` for the page's band
   contract when composing a page from scratch.
5. `verdict.py` (repo script) to grade the result, or `capture` to add the
   site that inspired the work back into the library.

## Tool reference

| tool | arguments | returns |
|---|---|---|
| `ping` | none | health check: ok plus card count, or startup problems |
| `style_search` | `query`, `top_n` | ranked cards for a natural-language query such as "funky" or "editorial but not brutalist" |
| `style_filter` | vector fields, `archetype`, `max_results` | structured filter over hue, brightness, saturation, corners, flatness, type_mood |
| `card_get` | `slug` | full card: fingerprint, semantic, annotation, behaviors, absolute asset paths |
| `card_compare` | `slug`, `project_dir` | borrow candidates for a project, based on its fingerprint |
| `theme_borrow` | `slug`, `target_dir` | token remap plus contrast-guarded CSS (WCAG AA) |
| `get_page_structure` | `brief`, `direction` | the band contract for a one-shot page: declared bands and mechanism budget |
| `get_section_blueprint` | `section_type` | the contracted recipe for one band type: contents, mechanism, measured backing |
| `capture` | `url`, `name`, `category`, `slug`, `fast`, `why` | a job id; the capture runs asynchronously and never blocks |
| `capture_status` | `job_id` | queued, running, done, or failed |
| `recommend_history` | `project_dir` | the design-scope iteration chain (manifest.json) |

`card_compare` and `theme_borrow` work out of the box: they import
`compare.py` and `theme.py`, which ship in this repo's `scripts/` directory.
At runtime the server resolves those scripts in this order: the
`DESIGN_SCOPE_SKILL_SCRIPTS` environment variable, an installed design-scope
skill, then the repo's own `scripts/`. Point the env var at your own copies
to override. See `docs/OSS.md` for details.

### Capture notes

- `fast=True` (default): screenshots, tokens, and semantic pass in about 60
  seconds; motion and behavior are skipped. `fast=False` runs the full
  four-layer pass in about 4 minutes.
- `why` (optional, up to 300 characters) becomes the card's rationale and is
  shown in the gallery and used by search fallback.
- A duplicate slug fails the job with a hint (use a different slug or
  `capture.py --redo`).
- Bot-walled sites (HTTP 403 or 429) fail the job with the underlying error;
  retry later.
- A successful capture rebuilds `style-index.json` automatically, so the new
  card is searchable immediately.

### Error convention

MCP has no error types, so every failure returns structured JSON:

```json
{"error": "card 'nope' not found", "hint": "see style_search for valid slugs"}
```

### Environment variables

| variable | meaning |
|---|---|
| `DESIGN_SCOPE_LIBRARY` | override the library root (default: the repo's `library/`). Honored by every module. |
| `DESIGN_SCOPE_SKILL_SCRIPTS` | override for where `compare.py` and `theme.py` live. Default resolution: env, then installed design-scope skill, then the repo's `scripts/`. |
| `NVIDIA_API_KEY` | key for the LLM annotation pass (`annotate.py`). |
| `HERMES_ENV` | optional path to a `.env` file to read `NVIDIA_API_KEY` from. |

## Showcase and verdict

`showcase/index.html` is the project's one-page sheet, built and graded with
the library itself. Every figure on it is counted from the library at build
time, and the page is graded by the same scored rubric an agent gets:

```bash
python scripts/build_showcase.py      # inject fresh stats, verdict, ledger
python scripts/verdict.py showcase/index.html --label "R1" \
    --ledger showcase/verdicts.json --json showcase/verdict.json
python scripts/build_showcase.py      # rebuild so rubric and ledger rows are real
```

`verdict.py` measures the rendered DOM against six checks (band allocation,
mechanism budget, palette conformance, fabric floor, reduced motion, living
artefacts) and appends PASS or UNDER rows to a ledger that is never edited
after it lands. The ledger keeps its failures. The exit code equals the
number of UNDER rows.

## One-shot pipeline

`showcase/one-shot/index.html` is the sheet whose decisions were made by the
server: the palette was borrowed (style_search then theme_borrow, with a
usability gate that rejects collapsed or low-contrast borrows and records the
rejects), the structure was measured (section_scan over the corpus, then
get_page_structure), and the page prints its own machine-written build
receipt.

```bash
python scripts/section_scan.py --all              # corpus band inventory
python scripts/one_shot.py scaffold --brief "blueprint sheet" --direction "measured technical"
# fill scripts/sheet_content.py; rendering is the agent's job
python scripts/one_shot.py grade --label "R1 one-shot"   # verdict, ledger, rebuild
```

The band skeleton is rendered by `scripts/blueprint.py` from the structure:
`data-band` and `data-band-type` and `data-mechanism` attributes per band, a
`<meta>` contract matching the structure, scroll-reveal scaffolding, and a
content layer (`sheet_content.py`) that survives re-scaffolds. Structure is
corpus-measured when `band-index.json` exists; the curated v1 plan is the
fallback on a fresh checkout.

## Repository layout

```
library/
  mcp_server.py        the MCP server (stdio and HTTP)
  capture.py           capture pipeline (screenshots, tokens, motion)
  annotate.py          LLM design-intelligence pass
  semantic_pass.py     named tokens, design intent, z-index, responsive
  behavior_pass.py     hover diffs, scroll triggers, interaction model
  style_index.py       rebuild style-index.json from cards
  style_search.py      natural-language search CLI
  regenerate_media.py  rebuild gitignored media locally
  gallery.py           HTML gallery generator
  backfill.py          motion, behavior, and semantic backfill for old cards
  index.json           card registry (204 cards)
  style-index.json     searchable style vectors, archetypes, tags
  cards/<slug>/        per-card intelligence layer
scripts/
  verdict.py           scored six-check rubric reviewer (PASS/UNDER plus ledger)
  stats.py             corpus numbers counted fresh from the library
  build_showcase.py    inject stats, verdict, ledger into a sheet
  one_shot.py          the pipeline: prepare, scaffold, grade
  page_structure.py    the band contract, corpus-measured with curated fallback
  section_scan.py      corpus band inventory
  section_blueprint.py the contracted recipe for one band type
  blueprint.py         renders the band skeleton from a structure
  sheet_content.py     the agent's fill layer, stable across re-scaffolds
  compare.py           borrow candidates (card fingerprint vs project)
  theme.py             token remap plus contrast-guarded CSS
showcase/
  index.template.html  the hand-built sheet (both themes, self-contained)
  index.html           built artifact; open this one
  verdicts.json        the ledger; every verdict, never edited after it lands
  one-shot/            the one-shotted sheet, its register, and its ledger
docs/
  mcp.md               MCP server reference
  OSS.md               packaging and regeneration documentation
tests/                 smoke and unit suites (no framework needed)
```

## Tests

```bash
python tests/client_smoke.py                  # real stdio MCP transport and error paths
python tests/client_smoke.py --queue          # in-process capture queue mock (no network)
python tests/test_style_search.py             # search layer unit tests
python tests/test_semantic_pass.py            # classifier and vocabulary guard
python tests/test_style_index.py              # vectors and hue boundaries (temp fixture)
python tests/test_behavior_pass.py            # hover-diff regression guard
python tests/test_vocabulary_consistency.py   # producers are a subset of search vocabulary
```

The unit suites and the queue mock run in CI on every push, on both
ubuntu-latest and windows-latest. Shared test plumbing lives in
`tests/_harness.py`.

## Data provenance

Cards describe the design of third-party sites: factual metadata such as
color tokens, typography, layout measurements, and interaction behavior,
plus LLM annotations that deliberately avoid brand commentary. design-scope
has no affiliation with any captured site. Screenshots and motion media are
regenerated locally and never shipped in the repo. If you capture a site,
respect its terms of use.

## Contributing

Issues and pull requests are welcome. Good first contributions: capturing a
missing category, improving the search vocabulary, or adding a test. Keep
changes additive and non-destructive; the library is data, not a build
artifact.

## License

MIT. See `LICENSE`.
