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
import os
import re
import sys
from pathlib import Path

from _console import utf8_stdout

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
INDEX = LIBRARY / "style-index.json"

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
    # split on exclusion markers — "no" only when it stands alone as a word:
    # \bno\b also matched the "no" inside "no-code", turning the rest of the
    # phrase into exclusions and leaving no include terms at all
    parts = re.split(r"\b(?:but\s+not|avoid|excluding|no(?=\s|$)|without)\b", q)
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


# Archetype names are rule-set labels, not words the annotation pass writes:
# of the 10 archetypes only "minimalist" appears in the tag vocabulary at all.
# So an archetype query carries one bit per card and every hit ties (all 53
# "funky" hits scored an identical 3, making top_n alphabetical). These are the
# annotation tags each archetype actually co-occurs with — every term below is
# present in the shipped index, none are invented — and each hit adds evidence
# so the ranking comes from real per-card data.
ARCHETYPE_KIN = {
    "funky": ("vibrant", "gradient", "illustration", "bold", "geometric", "accent color"),
    "playful": ("illustration", "vibrant", "rounded corners", "gradient", "bold"),
    "editorial": ("typography", "serif", "serif typography", "white space", "hero", "grid layout"),
    "brutalist": ("high contrast", "high-contrast", "monochrome", "grid", "bold", "structured"),
    "minimalist": ("minimal", "white space", "whitespace", "clean layout", "spacious", "simple"),
    "glassmorphic": ("gradient", "soft", "card", "rounded corners"),
    "dark-minimal": ("dark", "dark mode", "monochrome", "high contrast", "minimal"),
    "warm-minimal": ("white space", "spacious", "soft", "minimal", "accent color"),
    "premium": ("sleek", "professional", "spacious", "contrast", "serif"),
    "retro": ("illustration", "geometric", "accent", "bold"),
}


def _word_in(term: str, text: str) -> bool:
    """Word-boundary match. Substring matching made 'ai' hit 106/201 cards
    (detail, chain, airbnb, plaid); a design query must not match mid-word."""
    return bool(term) and re.search(rf"\b{re.escape(term)}\b", text) is not None


def is_excluded(card: dict, term: str) -> bool:
    """True if an exclusion term matches the card (archetype/vector/tag/why).

    Shared with the MCP server (mcp_server.py imports this).
    """
    for spec in ATTR_INDEX.get(term, []):
        kind, val = spec.split(":", 1)
        if kind == "archetype":
            if val in card.get("archetypes", []):
                return True
        elif kind == "tag":
            if val in card.get("tags", []):
                return True
        elif card.get("vector", {}).get(kind) == val:
            return True
    # annotation evidence excludes too — a card tagged 'brutalist' is brutalist
    # even when the archetype rule set didn't fire for it
    return _word_in(term, f"{card.get('why', '').lower()} "
                          f"{' '.join(card.get('tags', []))}")


def score(card: dict, terms: list[str]) -> int:
    total = 0
    vec = card.get("vector", {})
    arch = card.get("archetypes", [])
    tags = card.get("tags", [])
    tag_text = " ".join(tags)
    why = card.get("why", "").lower()
    for t in terms:
        credited_tag = False
        for spec in ATTR_INDEX.get(t, []):
            kind, val = spec.split(":", 1)
            if kind == "archetype":
                if val in arch:
                    total += 3
            elif kind == "tag":
                if val in tags:
                    total += 2
                    credited_tag = True
            elif vec.get(kind) == val:
                total += 2
        # The annotation layer is ALWAYS scored, not only when ATTR_INDEX has
        # no entry for the term. The old `continue` here meant 169 of the 177
        # cards tagged "minimalist" scored zero for the query "minimalist".
        # It is also what breaks score ties: archetype-only scoring gave every
        # one of the 53 "funky" hits an identical 3, making top_n alphabetical.
        if not credited_tag and _word_in(t, tag_text):
            total += 2
        if _word_in(t, why):
            total += 1
        if _word_in(t, card.get("slug", "")):
            total += 1
        # archetype queries have no per-card signal of their own — let the
        # annotation tags they co-occur with supply the ranking. Two hits
        # minimum: one shared tag like "bold" is coincidence, not evidence
        # (crediting single hits matched all 201 cards for "minimalist").
        kin_hits = sum(1 for kin in ARCHETYPE_KIN.get(t, ()) if kin in tags)
        if kin_hits >= 2:
            total += kin_hits
    return total


def search(index: dict, query: str, top_n: int = 8) -> list[tuple[int, str, dict]]:
    """Rank cards for a query. The single implementation — the CLI and the MCP
    server both call this so a scoring fix lands in one place.

    Returns [(score, slug, card), ...] best first; [] for an empty query.
    """
    include, exclude = parse_query(query)
    if not include:
        return []
    scored = []
    for slug, card in index["cards"].items():
        s = score(card, include)
        if s <= 0 or any(is_excluded(card, t) for t in exclude):
            continue
        scored.append((s, slug, card))
    scored.sort(key=lambda x: (-x[0], x[1]))  # slug tie-break keeps it stable
    return scored[:top_n] if top_n > 0 else scored


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+", help='e.g. "funky" or "editorial but not brutalist"')
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = ap.parse_args()

    if not INDEX.exists():
        print(f"style-index.json missing — run library/style_index.py first ({INDEX})", file=sys.stderr)
        sys.exit(1)
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    query = " ".join(args.query)
    if not parse_query(query)[0]:
        print("no meaningful query terms (try: funky / editorial / dark minimal serif)")
        sys.exit(0)

    results = search(index, query, args.top)
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
