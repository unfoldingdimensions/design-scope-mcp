#!/usr/bin/env python3
"""design-scope page structure — the band contract for a one-shot build.

v1 CURATED: returns the band skeleton (types, order, mechanism budget) the
agent renders against. v2 (corpus-measured) is a separate project — a band
inventory pass over captured cards; when it lands, this module becomes the
consumer of that data.

The contract is enforced by the page: <meta name="bands"> and
<meta name="mechanisms"> must equal what this planner declares, and the
verdict rubric measures the rendered document against them.

Usage:
  python scripts/page_structure.py --brief "blueprint sheet" [--direction "measured technical"]
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# the sheet taxonomy — band types with their interaction contract
BAND_TYPES = {
    "nav":               {"mechanism": True,  "note": "theme toggle + anchor state"},
    "hero":              {"mechanism": True,  "note": "hover-lift CTAs, entrance choreography"},
    "features-grid":     {"mechanism": False, "note": "corpus numbers, equal-height cards"},
    "how-it-works":      {"mechanism": False, "note": "connection / pipeline explanation"},
    "feature-spotlight": {"mechanism": False, "note": "self-grade rubric table"},
    "product-showcase":  {"mechanism": False, "note": "corpus scan bars"},
    "ledger":            {"mechanism": False, "note": "verdict history, reads upward"},
    "cta-banner":        {"mechanism": True,  "note": "copy-command button"},
    "footer":            {"mechanism": False, "note": "status bar"},
}

# the canonical sheet order (10 bands, two how-it-works slots)
DEFAULT_PLAN = [
    "nav", "hero", "features-grid", "how-it-works", "feature-spotlight",
    "product-showcase", "how-it-works", "ledger", "cta-banner", "footer",
]
MECHANISM_BUDGET = 4  # nav, hero, second how-it-works (step select), cta-banner
# the second how-it-works slot is the step-select mechanism — the type's
# default contract (how-it-works: passive) does not cover it, so slot 7 (0-based 6) opts in
MECHANISM_SLOTS = {6: True}


def plan(brief: str, direction: str = "") -> dict:
    """The band contract: declared counts + per-band mechanism flags."""
    if not brief or not brief.strip():
        raise ValueError("brief must not be empty")
    bands = []
    for i, t in enumerate(DEFAULT_PLAN, 1):
        spec = BAND_TYPES[t]
        bands.append({
            "index": i,
            "type": t,
            "mechanism": bool(spec["mechanism"] or MECHANISM_SLOTS.get(i - 1, False)),
            "note": spec["note"],
        })
    return {
        "brief": brief.strip(),
        "direction": direction.strip(),
        "declared_bands": len(bands),
        "mechanism_budget": MECHANISM_BUDGET,
        "bands": bands,
        "rationale": (
            "v1 curated contract — 10 bands across 9 types; mechanism budget 4 "
            "(nav theme toggle, hero hover, step select, copy command). "
            "Every declared count is measured by the verdict rubric against "
            "the rendered document."
        ),
        "direction_vote": _direction_vote(direction),
    }


def _direction_vote(direction: str) -> dict:
    """Corpus vote for a direction: top archetype tags matching the words."""
    si = ROOT / "library" / "style-index.json"
    if not si.exists():
        return {"note": "style-index.json not found — vote skipped"}
    import json as _json
    data = _json.loads(si.read_text(encoding="utf-8"))
    cards = data.get("cards", data) if isinstance(data, dict) else data
    if isinstance(cards, dict):
        cards = list(cards.values())
    words = {w for w in (direction or "").lower().split() if len(w) > 3}
    if not words:
        return {"note": "no direction given — vote skipped"}
    votes = {}
    for c in cards:
        for a in (c.get("archetypes") or []):
            al = a.lower()
            if any(w in al or al in w for w in words):
                votes[a] = votes.get(a, 0) + 1
    top = sorted(votes.items(), key=lambda kv: -kv[1])[:4]
    return {"votes": top, "note": "archetype tags matching direction words, counted from style-index.json"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brief", required=True, help="what the page is for")
    ap.add_argument("--direction", default="", help="style direction words")
    args = ap.parse_args()
    try:
        print(json.dumps(plan(args.brief, args.direction), indent=2, ensure_ascii=False))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
