#!/usr/bin/env python3
"""design-scope page structure — the band contract for a one-shot build.

v2 CORPUS-MEASURED: when library/band-index.json exists (built by
section_scan.py), the plan is measured — band types are chosen by corpus
frequency + brief keywords, and mechanism slots go to the types whose bands
actually hold state. v1 CURATED remains the fallback when the index is absent,
so the tool never breaks on a fresh checkout.

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
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()
BAND_INDEX = LIBRARY / "band-index.json"

# the sheet taxonomy — band types with their interaction contract
BAND_TYPES = {
    "nav":               {"mechanism": True,  "note": "theme toggle + anchor state"},
    "hero":              {"mechanism": True,  "note": "hover-lift CTAs, entrance choreography"},
    "features-grid":     {"mechanism": False, "note": "corpus numbers, equal-height cards"},
    "how-it-works":      {"mechanism": False, "note": "connection / pipeline explanation"},
    "feature-spotlight": {"mechanism": False, "note": "self-grade rubric table"},
    "product-showcase":  {"mechanism": False, "note": "corpus scan bars"},
    "pricing":           {"mechanism": False, "note": "plan tiers, per-page-build economics"},
    "faq":               {"mechanism": False, "note": "details/summary pairs"},
    "testimonials":      {"mechanism": False, "note": "quotes, read upward"},
    "comparison":        {"mechanism": False, "note": "feature rows vs alternatives"},
    "ledger":            {"mechanism": False, "note": "verdict history, reads upward"},
    "cta-banner":        {"mechanism": True,  "note": "copy-command button"},
    "footer":            {"mechanism": False, "note": "status bar"},
}
# types that always open/close the sheet
ALWAYS = ["nav", "hero", "footer"]
MECHANISM_THRESHOLD = 0.30  # a type earns a mechanism slot when ≥30% of its bands hold state
MAX_BANDS = 10

# brief keywords → purpose band types (the measured fallback fills the rest)
PURPOSE_KEYWORDS = {
    "pricing": ["pricing", "price", "plan", "credit"],
    "faq": ["faq", "question", "frequent"],
    "comparison": ["comparison", "compare", "versus", "vs", "alternat"],
    "testimonials": ["testimonial", "customers", "social proof", "quote"],
    "how-it-works": ["how it works", "pipeline", "process", "workflow", "register", "receipt"],
    "product-showcase": ["showcase", "gallery", "scan", "index", "product"],
    "features-grid": ["features", "grid", "capabilit"],
    "feature-spotlight": ["spotlight", "verdict", "grade", "rubric", "highlight"],
    "ledger": ["ledger", "record", "history"],
    "cta-banner": ["start", "signup", "get started", "cta"],
}


def _load_corpus() -> dict | None:
    if not BAND_INDEX.exists():
        return None
    try:
        idx = json.loads(BAND_INDEX.read_text(encoding="utf-8"))
        st = idx.get("stats") or {}
        if st.get("scanned", 0) == 0 or not st.get("per_type"):
            return None
        return st
    except Exception:
        return None


def _curated(brief: str, direction: str) -> dict:
    order = ["nav", "hero", "features-grid", "how-it-works", "feature-spotlight",
             "product-showcase", "how-it-works", "ledger", "cta-banner", "footer"]
    bands = []
    for i, t in enumerate(order, 1):
        spec = BAND_TYPES[t]
        mech = spec["mechanism"] or (t == "how-it-works" and order[:i].count("how-it-works") == 2)
        bands.append({"index": i, "type": t, "mechanism": bool(mech), "note": spec["note"]})
    return {
        "brief": brief.strip(), "direction": direction.strip(),
        "declared_bands": len(bands), "mechanism_budget": 4, "bands": bands,
        "basis": "curated (v1 fallback — no band-index.json)",
        "rationale": ("v1 curated contract — 10 bands, mechanism budget 4. "
                      "Run scripts/section_scan.py to make the plan corpus-measured."),
        "direction_vote": _direction_vote(direction),
    }


def _corpus(brief: str, direction: str, st: dict) -> dict:
    per = st["per_type"]
    # `other` is the honest unclassified bucket, not a renderable band type
    freq = [t for t, v in sorted(per.items(), key=lambda kv: -kv[1]["count"])
            if t in BAND_TYPES]
    used: list[str] = []
    for t in ALWAYS:
        if t in per:
            used.append(t)
    # brief keywords → purpose types, in corpus order when several match.
    # A brief-requested type is included even when the corpus has measured
    # none of it yet (e.g. ledger on a landing-page corpus) — the brief asked,
    # so the band renders with zeroed corpus evidence, honestly labelled.
    brief_l = brief.lower()
    for t, words in PURPOSE_KEYWORDS.items():
        if t in used:
            continue
        if any(w in brief_l for w in words):
            used.append(t)
    # fill with the most frequent remaining types
    for t in freq:
        if len(used) >= MAX_BANDS:
            break
        if t not in used:
            used.append(t)
    # footer last
    if "footer" in used:
        used.remove("footer")
        used.append("footer")

    bands, mech_count = [], 0
    for i, t in enumerate(used[:MAX_BANDS], 1):
        spec = BAND_TYPES[t]
        v = per.get(t, {})
        # footer is a passive close — it never earns a mechanism slot even
        # when measured bands of that type hold state
        earns = (t != "footer" and v.get("share", 0) >= MECHANISM_THRESHOLD
                 and v.get("count", 0) >= 3)
        mech = bool(spec["mechanism"] or earns)
        if mech:
            mech_count += 1
        bands.append({
            "index": i, "type": t, "mechanism": mech, "note": spec["note"],
            "corpus": {"measured": v.get("count", 0), "with_state": v.get("with_state", 0),
                       "share": v.get("share", 0)},
        })
    return {
        "brief": brief.strip(), "direction": direction.strip(),
        "declared_bands": len(bands), "mechanism_budget": mech_count, "bands": bands,
        "basis": f"corpus-measured — {st.get('scanned')} pages scanned, {st.get('bands')} bands",
        "rationale": ("v2 measured contract — band types chosen by corpus frequency + brief "
                      "keywords; mechanism slots go to types where ≥30% of measured bands "
                      "hold state (threshold from band-index.json)."),
        "direction_vote": _direction_vote(direction),
    }


def plan(brief: str, direction: str = "") -> dict:
    """The band contract: corpus-measured when the index exists, curated otherwise."""
    if not brief or not brief.strip():
        raise ValueError("brief must not be empty")
    st = _load_corpus()
    return _corpus(brief, direction, st) if st else _curated(brief, direction)


def _direction_vote(direction: str) -> dict:
    """Corpus vote for a direction: top archetype tags matching the words."""
    si = LIBRARY / "style-index.json"  # env-aware, not a hardcoded sibling
    if not si.exists():
        return {"note": "style-index.json not found — vote skipped"}
    data = json.loads(si.read_text(encoding="utf-8"))
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
