#!/usr/bin/env python3
"""design-scope stats — real corpus numbers for the showcase sheet.

Reads library/index.json, library/style-index.json, and the card
directories, and emits one JSON document of measured facts. Every figure
printed here is counted from disk on every run — nothing is hard-coded.

Usage:
  python scripts/stats.py [--json]        # pretty JSON to stdout
  python scripts/stats.py --out path.json # write JSON to a file

RUN WITH THE LIBRARY ENV'S PYTHON (same venv as capture.py).
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()

# The MCP server surface — kept static here because tool names come from
# decorators at import time; the showcase sheet lists them as a contract.
MCP_TOOLS = [
    ("ping", "health check — library stats or startup problems"),
    ("style_search", "natural-language style search over the library"),
    ("style_filter", "structured filter over the style index"),
    ("card_get", "one card: fingerprint + semantic + behaviors + absolute tokens"),
    ("card_compare", "borrow candidates: card fingerprint vs a project"),
    ("theme_borrow", "a card's palette: token remap + contrast-guarded CSS"),
    ("get_page_structure", "the band contract for a one-shot page: declared bands + mechanism budget"),
    ("get_section_blueprint", "the contracted recipe for one band type: contents + mechanism + measured backing"),
    ("capture", "capture a website as a library card"),
    ("capture_status", "poll a capture job"),
    ("recommend_history", "the iteration chain for a project"),
]


def _count(cards_dir: Path, pred) -> int:
    return sum(1 for d in cards_dir.iterdir() if d.is_dir() and pred(d))


def compute(library: Path) -> dict:
    cards_dir = library / "cards"
    if not cards_dir.is_dir():
        print(f"no cards dir under {library}", file=sys.stderr)
        sys.exit(2)

    index = json.loads((library / "index.json").read_text(encoding="utf-8"))
    index_cards = index.get("cards", {})
    index_stats = index.get("stats", {})

    captured = sum(1 for d in cards_dir.iterdir() if d.is_dir())
    annotated = _count(cards_dir, lambda d: (d / "annotation.json").exists())
    motion = _count(cards_dir, lambda d: (d / "motion").is_dir())
    behaviors = _count(cards_dir, lambda d: (d / "motion" / "behaviors.json").exists())
    semantic = _count(cards_dir, lambda d: (d / "semantic.json").exists())
    dark_themed = _count(cards_dir, lambda d: _has_dark(d))
    with_why = _count(cards_dir, lambda d: _annotated_why(d))

    style_index = json.loads((library / "style-index.json").read_text(encoding="utf-8"))
    si_cards = style_index.get("cards", style_index) if isinstance(style_index, dict) else style_index
    if isinstance(si_cards, dict):
        si_cards = list(si_cards.values())
    style_indexed = len(si_cards)

    archetypes = {}
    hues = {}
    for c in si_cards:
        for a in (c.get("archetypes") or []):
            archetypes[a] = archetypes.get(a, 0) + 1
        h = (c.get("vector") or {}).get("hue_family")
        if h:
            hues[h] = hues.get(h, 0) + 1

    top_archetypes = sorted(archetypes.items(), key=lambda kv: -kv[1])
    top_hues = sorted(hues.items(), key=lambda kv: -kv[1])

    return {
        "generated": _now(),
        "corpus": {
            "captured": captured,
            "indexed": len(index_cards),
            "annotated": annotated,
            "annotated_why": with_why,
            "motion": motion,
            "behaviors": behaviors,
            "semantic": semantic,
            "dark_themed": dark_themed,
            "style_indexed": style_indexed,
            "index_stats": index_stats,
            "bands_scanned": _band_stat("scanned", library),
            "bands_measured": _band_stat("bands", library),
        },
        "styles": {
            "top_archetypes": top_archetypes,
            "top_hues": top_hues,
            "archetype_total_tags": sum(archetypes.values()),
        },
        "mcp": {
            "name": "design-scope",
            "tools": MCP_TOOLS,
            "transports": ["stdio", "streamable-http"],
        },
    }


def _has_dark(card_dir: Path) -> bool:
    try:
        s = json.loads((card_dir / "semantic.json").read_text(encoding="utf-8"))
        nt = s.get("named_tokens") or {}
        return bool(nt.get("dark"))
    except Exception:
        return False


def _annotated_why(card_dir: Path) -> bool:
    md = card_dir / "card.md"
    if not md.exists():
        return False
    return "annotation pending" not in md.read_text(encoding="utf-8", errors="ignore")


def _band_stat(key: str, library: Path):
    """Band-index stats (section_scan.py) — 0 until the corpus is scanned.
    Uses the passed library, not the module global — fixture-based calls must
    not report the real repo's band counts."""
    idx = library / "band-index.json"
    if not idx.exists():
        return 0
    try:
        return json.loads(idx.read_text(encoding="utf-8")).get("stats", {}).get(key, 0)
    except Exception:
        return 0


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="pretty JSON to stdout")
    ap.add_argument("--out", default=None, help="write JSON to a file")
    args = ap.parse_args()

    data = compute(LIBRARY)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"stats -> {args.out}")
    else:
        print(text if args.json else " ".join(
            f"{k}={v}" for k, v in data["corpus"].items()))


if __name__ == "__main__":
    main()
