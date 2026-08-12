# design-scope OSS packaging — what ships, what regenerates

**Decision (2026-08):** the public repo ships the **intelligence layer only**.
No media (screenshots, motion videos ≈ 3GB local) is packaged. Users rebuild
media locally with one command.

## What ships in the repo (~9MB tracked)

```
library/
├── index.json              # 201 cards: slug, url, name, category + fingerprint summaries
├── style-index.json        # style vectors + archetypes + LLM tags (searchable)
├── style-summary.md        # human-readable landscape
├── seed-batch-1..4.json    # the original 4×50 site lists (capture recipes)
├── cards/<slug>/
│   ├── card.md             # capture metadata
│   ├── fingerprint.json    # Dembrandt tokens (colors/type/spacing/radii/motion)
│   ├── semantic.json       # named tokens, design intent, z-index, responsive rules
│   ├── annotation.json     # LLM design intelligence (vibe, what_works, search_terms)
│   └── motion/             # behaviors.json (classified model + signals) + hover-inventory.json
├── capture.py              # the capture pipeline
├── annotate.py             # LLM annotation pass (needs NVIDIA_API_KEY)
├── style_index.py          # rebuild style-index.json from cards
├── style_search.py         # natural-language search CLI
├── regenerate_media.py     # ← THE REBUILD COMMAND
├── backfill.py             # motion/behavior/semantic backfill
└── mcp_server.py           # optional MCP server (stdio + HTTP)
```

## What regenerates locally

```bash
# rebuild ALL media (screenshots + motion + semantic) for cards missing it
python library/regenerate_media.py            # full passes, ~4-6 min/card
python library/regenerate_media.py --fast     # skip motion/behavior, ~60s/card
python library/regenerate_media.py --all      # redo everything

# or per-batch with the original seed lists
python library/capture.py seed-batch-1.json

# or one card
python library/capture.py --url https://stripe.com --name Stripe --category fintech

# or the HTML gallery (generated artifact — not tracked)
python library/gallery.py
```

Estimated full rebuild of 201 cards: **~14-20h background** (full passes) or
**~3-4h** (`--fast`, screenshots + tokens + semantic only — motion/behavior
omitted).

## Capture pipeline

One card = **3 page loads**: a single desktop context shared by the semantic
probe, the reference screenshot, and the merged interaction probe (scroll
sweep, scroll triggers, hover before/after diffs, click); one mobile context
(separate iPhone UA — kept separate by design); and the dembrandt CLI. The
motion video is recorded across the whole desktop session, so the video and
`behaviors.json` describe the same browsing session. `behaviors.json` carries
the classified `interaction_model` (`"scroll-driven"` / `"click-driven"` /
`"static"`) plus the raw probe counters in `interaction_signals`.

## Regenerated files that stay out of git

`.gitignore` excludes: `screenshot-*.png`, `motion/card-motion.webm`,
`motion/hover-*.png`, `motion/video/`, `tmp/`, `gallery.html`. The library
works with media missing — search, style-filter, and annotation (text
fallback) all function from the intelligence layer alone.

**One caveat:** the MCP server's `card_compare` and `theme_borrow` tools
import `compare.py`/`theme.py`, which ship with the design-scope skill, not
with this repo. Point the server at them with `DESIGN_SCOPE_SKILL_SCRIPTS`
(or install the skill); without it the tools return a clear error instead of
a traceback.

## Annotation

`python library/annotate.py` — needs `NVIDIA_API_KEY` in the environment
(NVIDIA NIM, vision-capable, 40 RPM). Skips cards with an existing
`annotation.json` (resumable). Without a key, cards stay unannotated —
search falls back to deterministic tags (graceful).

## MCP server (optional)

```bash
python library/mcp_server.py                    # stdio (Claude Code, Cursor, Hermes)
cd library && uvicorn mcp_server:app --port 8232  # HTTP
```

See `docs/mcp.md` for registration + tool reference.
