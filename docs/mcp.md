# design-scope MCP server

Local MCP server exposing the **204-card design library** as tools any MCP client
(Claude Code, Cursor, another agent) can call. Read-only for the library;
`capture` adds cards; **never edits project source**.

## Run

```bash
# stdio (Claude Code / Cursor / Hermes)
python library/mcp_server.py

# HTTP (streamable)
cd library && uvicorn mcp_server:app --host 127.0.0.1 --port 8232
```

Startup validation fails loudly if `index.json` or `style-index.json` are
missing, with the exact fix command. It runs at import, so it covers the HTTP
transport too — `uvicorn mcp_server:app` refuses to boot rather than serving a
library that isn't there.

## Register with clients

**Claude Code**
```bash
claude mcp add design-scope -- python "<path-to-repo>/library/mcp_server.py"
```

**Cursor** — `.mcp.json`:
```json
{"mcpServers": {"design-scope": {"command": "python",
  "args": ["<path-to-repo>\\library\\mcp_server.py"]}}}
```

**Hermes** — add the server to your MCP config; the stdio command above is the
server entry.

## Tools

| tool | args | returns |
|---|---|---|
| `ping` | — | health: ok + card count, or startup problems |
| `style_search` | `query`, `top_n` | ranked cards — natural language: `"funky"`, `"editorial but not brutalist"`, `"warm minimal"` |
| `style_filter` | vector fields, `archetype`, `max_results` | structured filter (hue/brightness/saturation/corners/flatness/type_mood) |
| `card_get` | `slug` | full card: fingerprint + semantic + **annotation** + behaviors + absolute asset paths |
| `card_compare` | `slug`, `project_dir` | borrow candidates vs the project's fingerprint |
| `theme_borrow` | `slug`, `target_dir` | token remap + contrast-guarded CSS (WCAG AA) |
| `get_page_structure` | `brief`, `direction` | the band contract: declared bands + mechanism budget |
| `get_section_blueprint` | `section_type` | the contracted recipe for one band type |
| `capture` | `url`, `name`, `category`, `slug`, `fast`, `why` | **job_id** (async, never blocks) |
| `capture_status` | `job_id` | queued / running / done / failed |
| `recommend_history` | `project_dir` | the design-scope iteration chain (manifest.json) |

`card_compare` and `theme_borrow` import `compare.py`/`theme.py`. Those scripts
ship with this repo in `scripts/`, so both tools work out of the box.
Resolution order at runtime: `DESIGN_SCOPE_SKILL_SCRIPTS` env, then an
installed design-scope skill, then the repo's `scripts/`.

### capture notes

- `fast=True` (default): screenshots + tokens + semantic, **skips** motion +
  behavior (~60s). `fast=False`: the full 4-layer pass (~4min).
- `why` (optional, ≤300 chars) becomes the card's rationale — shown on the
  gallery and used by search fallback.
- Duplicate slug → job fails with a hint (different slug or `capture.py --redo`).
- Bot-walled sites (403/429) → job fails with the underlying error; retry later.
- A successful capture rebuilds `style-index.json` automatically — the new
  card is searchable immediately.

## Error convention

MCP has no error types — every failure returns structured JSON:
```json
{"error": "card 'nope' not found", "hint": "see style_search for valid slugs"}
```

## Env

- `DESIGN_SCOPE_LIBRARY` — override the library path (default: this repo's
  `library/`). Honored by every module: the server, capture, backfill,
  gallery, style_index, style_search, annotate, regenerate_media.
- `DESIGN_SCOPE_SKILL_SCRIPTS` — where `compare.py`/`theme.py` live (default:
  the Hermes-profile design-scope skill scripts). `card_compare`/`theme_borrow`
  return a structured error when the directory is absent.
- Port: `uvicorn ... --port 8232` (change freely).

## Smoke test

```bash
python tests/client_smoke.py            # real stdio transport, all tools + error paths
python tests/client_smoke.py --queue    # in-process queue mock (no network)
python tests/test_style_search.py       # search layer unit tests
python tests/test_semantic_pass.py      # classifier vocabulary guard
python tests/test_style_index.py        # vector/hue boundaries (temp fixture)
python tests/test_behavior_pass.py      # hover-diff regression guard
python tests/test_vocabulary_consistency.py  # producers ⊆ search vocabulary
```

## Files

- `library/mcp_server.py` — the server (FastMCP, stdio + HTTP)
- `tests/client_smoke.py` — smoke test
- `library/style-index.json` — the style index the search tools read
  (rebuild: `python library/style_index.py`)
