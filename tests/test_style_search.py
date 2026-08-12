"""design-scope style_search unit tests — plain asserts, no framework.

Usage:
  python tests/test_style_search.py

Exits 0 on success, 1 on any failed check. Never touches the library
(tests operate on synthetic cards in memory).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

from style_search import ATTR_INDEX, parse_query, score, is_excluded  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)


def card(slug="x", archetypes=(), tags=(), vector=None, why=""):
    return {"slug": slug, "archetypes": list(archetypes), "tags": list(tags),
            "vector": vector or {}, "why": why}


def test_parse_query():
    inc, exc = parse_query("editorial but not brutalist")
    check("exclusion 'but not' splits", inc == ["editorial"] and exc == ["brutalist"],
          f"include={inc} exclude={exc}")
    inc, exc = parse_query("dark no grain")
    check("exclusion 'no' splits", "dark" in inc and "grain" in exc, f"include={inc} exclude={exc}")
    inc, _ = parse_query("some style designs for me")
    check("stopwords stripped", inc == [], str(inc))
    inc, exc = parse_query("vibrant rounded, avoid brutalism")
    check("exclusion 'avoid' splits", "vibrant" in inc and "rounded" in inc and "brutalism" in exc,
          f"include={inc} exclude={exc}")


def test_duplicate_key_regression():
    """A term appearing in multiple categories must match each (no silent overwrite)."""
    check("soft → saturation:soft", score(card(vector={"saturation": "soft"}), ["soft"]) > 0)
    check("soft → corners:soft", score(card(vector={"corners": "soft"}), ["soft"]) > 0)
    check("bold → type_mood:bold-led", score(card(vector={"type_mood": "bold-led"}), ["bold"]) > 0)
    check("bold → tag:bold", score(card(tags=["bold"]), ["bold"]) > 0)


def test_warm_cool_families():
    """warm/cool are family aliases over the hues the indexer actually emits."""
    for hue in ("orange", "yellow", "red", "pink"):
        check(f"warm matches hue_family:{hue}", score(card(vector={"hue_family": hue}), ["warm"]) > 0)
    for hue in ("blue", "cyan", "green", "purple"):
        check(f"cool matches hue_family:{hue}", score(card(vector={"hue_family": hue}), ["cool"]) > 0)
    check("warm does NOT match cool hue", score(card(vector={"hue_family": "blue"}), ["warm"]) == 0)
    check("cool does NOT match warm hue", score(card(vector={"hue_family": "orange"}), ["cool"]) == 0)


def test_type_mood_reachable():
    """mono/sans map to the exact strings the producer emits."""
    check("mono → type_mood:mono-accent", score(card(vector={"type_mood": "mono-accent"}), ["mono"]) > 0)
    check("sans → type_mood:neutral-sans", score(card(vector={"type_mood": "neutral-sans"}), ["sans"]) > 0)
    check("serif → type_mood:serif-led", score(card(vector={"type_mood": "serif-led"}), ["serif"]) > 0)


def test_archetype_terms():
    check("retro archetype reachable", score(card(archetypes=["retro"]), ["retro"]) > 0)
    check("warm-minimal archetype reachable", score(card(archetypes=["warm-minimal"]), ["warm-minimal"]) > 0)
    check("funky archetype reachable", score(card(archetypes=["funky"]), ["funky"]) > 0)


def test_is_excluded():
    check("exclude by archetype", is_excluded(card(archetypes=["brutalist"]), "brutalist"))
    check("exclude by tag", is_excluded(card(tags=["noise"]), "noise"))
    check("exclude by vector", is_excluded(card(vector={"brightness": "dark"}), "dark"))
    check("exclude by why text", is_excluded(card(why="elegant serif story"), "story"))
    check("no false exclusion", not is_excluded(card(vector={"brightness": "light"}), "dark"))


def test_attr_index_no_duplicate_keys():
    dups = [k for k in ATTR_INDEX if k in ("soft", "bold") and isinstance(ATTR_INDEX[k], str)]
    check("no single-string values left (dup-key class)", not dups, str(dups))


if __name__ == "__main__":
    test_parse_query()
    test_duplicate_key_regression()
    test_warm_cool_families()
    test_type_mood_reachable()
    test_archetype_terms()
    test_is_excluded()
    test_attr_index_no_duplicate_keys()
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
        sys.exit(1)
    print("ALL PASS")
