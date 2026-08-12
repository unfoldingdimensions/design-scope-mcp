#!/usr/bin/env python3
"""design-scope style search — natural-language query over the style index.

Maps free-text queries to (a) archetype names, (b) vector attributes,
(c) tags/why-text keywords. Supports exclusions ("but not" / "avoid" /
"no <term>").

Usage:
  python style_search.py "funky"
  python style_search.py "editorial but not brutalist"
  python style_search.py "dark minimal serif"
  python style_search.py "vibrant rounded, avoid brutalism"
  python style_search.py --top 5 "warm muted"

Exit 0 always; prints ranked cards (slug, archetypes, palette, paths).
"""
import argparse
import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent
INDEX = LIB / "library" / "style-index.json"

# query term → list of "kind:value" attribute specs (a term may match several:
# "soft" is both a saturation and a corners value; "warm" is a hue-family alias)
ATTR_INDEX = {
    # brightness
    "dark": ["brightness:dark"], "light": ["brightness:light"], "mid": ["brightness:mid"],
    # saturation
    "vibrant": ["saturation:vibrant"], "muted": ["saturation:muted"],
    "soft": ["saturation:soft", "corners:soft"],
    # hue — alias families cover the hues style_index actually emits
    "warm": ["hue_family:orange", "hue_family:yellow", "hue_family:red", "hue_family:pink"],
    "cool": ["hue_family:blue", "hue_family:cyan", "hue_family:green", "hue_family:purple"],
    "neutral": ["hue_family:neutral"],
    "orange": ["hue_family:orange"], "yellow": ["hue_family:yellow"],
    "pink": ["hue_family:pink"], "cyan": ["hue_family:cyan"],
    "green": ["hue_family:green"], "purple": ["hue_family:purple"], "blue": ["hue_family:blue"],
    "red": ["hue_family:red"],
    "multicolor": ["hue_family:multicolor"], "colorful": ["hue_family:multicolor"],
    # corners
    "sharp": ["corners:sharp"],
    "rounded": ["corners:rounded"], "generous": ["corners:generous"],
    # flatness
    "flat": ["flatness:flat"], "elevated": ["flatness:elevated"], "shadow": ["flatness:elevated"],
    # type — values MUST match semantic_pass._classify_intent output exactly
    "serif": ["type_mood:serif-led"], "mono": ["type_mood:mono-accent"],
    "monospace": ["type_mood:mono-accent"],
    "bold": ["type_mood:bold-led", "tag:bold"],
    "sans": ["type_mood:neutral-sans"],
    # archetype names
    "funky": ["archetype:funky"], "editorial": ["archetype:editorial"],
    "brutalist": ["archetype:brutalist"], "brutalism": ["archetype:brutalist"],
    "minimal": ["archetype:minimalist"], "minimalist": ["archetype:minimalist"],
    "glass": ["archetype:glassmorphic"], "glassmorphic": ["archetype:glassmorphic"],
    "dark-minimal": ["archetype:dark-minimal"], "warm-minimal": ["archetype:warm-minimal"],
    "playful": ["archetype:playful"], "premium": ["archetype:premium"],
    "retro": ["archetype:retro"],
    # tags
    "3d": ["tag:3d"], "noise": ["tag:noise"], "grain": ["tag:grain"], "photo": ["tag:photography"],
    "photography": ["tag:photography"], "elegant": ["tag:elegant"], "clean": ["tag:clean"],
    "tech": ["tag:tech"], "saas": ["tag:saas"], "dashboard": ["tag:dashboard"],
    "landing": ["tag:landing"], "ecommerce": ["tag:ecommerce"], "fintech": ["tag:fintech"],
    "gaming": ["tag:fun"], "fun": ["tag:fun"], "vintage": ["tag:vintage"],
}


def parse_query(q: str) -> tuple[list[str], list[str]]:
    """Returns (include-terms, exclude-terms)."""
    q = q.lower()
    include, exclude = [], []
    # split on exclusion markers
    parts = re.split(r"\b(?:but\s+not|avoid|excluding|no|without)\b", q)
    include_raw = parts[0]
    for extra in parts[1:]:
        exclude.extend(extra.split())
    include.extend(include_raw.split())
    # strip stopwords + punctuation from includes/excludes
    stop = {"a", "an", "the", "and", "or", "some", "suggest", "suggestion",
            "style", "styles", "design", "designs", "for", "me", "like", "with"}
    clean = lambda terms: [t for t in (re.sub(r"[^a-z0-9-]+", "", t) for t in terms)
                           if t and t not in stop]
    return clean(include), clean(exclude)


def is_excluded(card: dict, term: str) -> bool:
    """True if an exclusion term matches the card (archetype/vector/tag/why).

    Shared with the MCP server (mcp_server.py imports this).
    """
    specs = ATTR_INDEX.get(term, [])
    if specs:
        for spec in specs:
            kind, val = spec.split(":", 1)
            if kind == "archetype" and val in card.get("archetypes", []):
                return True
            if kind == "tag" and val in card.get("tags", []):
                return True
            if card.get("vector", {}).get(kind) == val:
                return True
    elif term and (term in card.get("why", "").lower()
                   or term in " ".join(card.get("tags", []))):
        return True
    return False


def score(card: dict, terms: list[str]) -> int:
    total = 0
    vec = card.get("vector", {})
    arch = card.get("archetypes", [])
    tags = card.get("tags", [])
    why = card.get("why", "").lower()
    for t in terms:
        specs = ATTR_INDEX.get(t)
        if not specs:
            # free-text: search why + tags + slug
            if t in why or t in " ".join(tags) or t in card.get("slug", ""):
                total += 1
            continue
        for spec in specs:
            kind, val = spec.split(":", 1)
            if kind == "archetype" and val in arch:
                total += 3
            elif kind == "tag" and val in tags:
                total += 2
            elif vec.get(kind) == val:
                total += 2
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+", help='e.g. "funky" or "editorial but not brutalist"')
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = ap.parse_args()

    if not INDEX.exists():
        print(f"style-index.json missing — run library/style_index.py first ({INDEX})", file=sys.stderr)
        sys.exit(1)
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    include, exclude = parse_query(" ".join(args.query))
    if not include:
        print("no meaningful query terms (try: funky / editorial / dark minimal serif)")
        sys.exit(0)

    scored = []
    for slug, card in index["cards"].items():
        s = score(card, include)
        if s <= 0:
            continue
        # exclusions: drop if any excluded term matches (shared helper)
        if any(is_excluded(card, t) for t in exclude):
            continue
        scored.append((s, slug, card))
    scored.sort(key=lambda x: -x[0])

    results = scored[: args.top]
    if args.json:
        print(json.dumps([{"slug": s, "score": sc, "archetypes": c["archetypes"],
                           "tags": c["tags"], "vector": c["vector"],
                           "palette": c["palette"], "why": c["why"][:200],
                           "paths": c["paths"]} for sc, s, c in results], indent=2))
        sys.exit(0)

    print(f"query: {' '.join(args.query)}  → {len(results)} result(s)")
    print("=" * 72)
    for sc, slug, c in results:
        pal = " ".join(f"`{p['hex']}`" for p in c["palette"][:4])
        print(f"\n[{sc} pts] {slug}  ({', '.join(c['archetypes']) or 'no archetype'})")
        print(f"  vector: {c['vector'].get('hue_family')} · {c['vector'].get('brightness')} · "
              f"{c['vector'].get('saturation')} · {c['vector'].get('corners')} · "
              f"{c['vector'].get('flatness')} · {c['vector'].get('type_mood')}")
        if pal:
            print(f"  palette: {pal}")
        if c.get("why"):
            print(f"  why: {c['why'][:120]}…")
        print(f"  → {c['paths']['semantic']}  |  screenshot: {c['paths']['screenshot']}")


if __name__ == "__main__":
    main()
