#!/usr/bin/env python3
"""design-scope section blueprint — the contracted recipe for one band type.

What a band of this type typically contains, which mechanisms it usually
carries (measured from band-index.json — the share of real bands of this type
that hold state), and the scaffold the renderer emits for it. This is the
"contracted interaction recipe" — the agent fills content, the contract is
decided.

Usage:
  python scripts/section_blueprint.py pricing
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()
BAND_INDEX = LIBRARY / "band-index.json"

# contents + scaffold per type (the contracted recipe)
RECIPES = {
    "nav": {
        "label": "Navigation",
        "contents": ["brand mark", "anchor links", "theme toggle", "primary CTA", "status"],
        "mechanism": "theme toggle (JS), hover underlines",
    },
    "hero": {
        "label": "Hero",
        "contents": ["kicker label", "headline", "sub copy", "claim strip", "CTA row", "fig art"],
        "mechanism": "hover-lift CTAs (CSS), entrance choreography",
    },
    "features-grid": {
        "label": "Features grid",
        "contents": ["band head", "3–6 equal-height cards", "per-card note"],
        "mechanism": "card hover (border/lift)",
    },
    "how-it-works": {
        "label": "How it works",
        "contents": ["band head", "ordered steps", "detail pane"],
        "mechanism": "step select (JS)",
    },
    "feature-spotlight": {
        "label": "Feature spotlight",
        "contents": ["band head", "rubric/verdict table", "caption"],
        "mechanism": "row hover (background)",
    },
    "product-showcase": {
        "label": "Product showcase",
        "contents": ["band head", "metrics bars", "insight line"],
        "mechanism": "bar width transition",
    },
    "pricing": {
        "label": "Pricing",
        "contents": ["plan tiers", "per-unit economics", "CTA per tier"],
        "mechanism": "tier hover, CTA hover",
    },
    "faq": {
        "label": "FAQ",
        "contents": ["question/answer pairs"],
        "mechanism": "details/summary (native)",
    },
    "testimonials": {
        "label": "Testimonials",
        "contents": ["quote cards", "attribution"],
        "mechanism": "card hover",
    },
    "comparison": {
        "label": "Comparison",
        "contents": ["feature rows", "alternative columns"],
        "mechanism": "row hover",
    },
    "ledger": {
        "label": "Ledger",
        "contents": ["verdict rows", "reads upward", "caption"],
        "mechanism": "row hover",
    },
    "cta-banner": {
        "label": "CTA banner",
        "contents": ["commands", "copy buttons", "start note"],
        "mechanism": "copy-command buttons (JS)",
    },
    "footer": {
        "label": "Footer",
        "contents": ["end tag", "status dot"],
        "mechanism": "—",
    },
}


def blueprint(section_type: str) -> dict:
    """The recipe for one band type + its measured corpus backing."""
    recipe = RECIPES.get(section_type)
    if not recipe:
        raise ValueError(f"unknown section type '{section_type}' — "
                         f"known: {', '.join(RECIPES)}")
    corpus = None
    if BAND_INDEX.exists():
        try:
            st = json.loads(BAND_INDEX.read_text(encoding="utf-8")).get("stats", {})
            v = st.get("per_type", {}).get(section_type)
            if v:
                corpus = {"measured": v.get("count", 0),
                          "with_state": v.get("with_state", 0),
                          "share": v.get("share", 0)}
        except Exception:
            corpus = None
    return {
        "type": section_type,
        "label": recipe["label"],
        "contents": recipe["contents"],
        "mechanism": recipe["mechanism"],
        "corpus": corpus or {"measured": 0, "with_state": 0, "share": 0},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("section_type", help="one of the band taxonomy types")
    args = ap.parse_args()
    try:
        print(json.dumps(blueprint(args.section_type), indent=2, ensure_ascii=False))
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
