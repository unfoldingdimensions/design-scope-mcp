"""design-scope cross-module vocabulary consistency — the guard that would
have caught the dead-search-terms bug class.

Asserts that every value the producers can emit (style_index hue families,
semantic_pass type moods, the archetype rule set) is reachable through
style_search.ATTR_INDEX, and that ATTR_INDEX has no duplicate keys.

Usage:
  python tests/test_vocabulary_consistency.py

Exits 0 on success, 1 on any failed check.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

from semantic_pass import _classify_intent  # noqa: E402
from style_index import _hue_family  # noqa: E402
from style_search import ATTR_INDEX  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)


def specs(kind: str) -> set[str]:
    out = set()
    for specs_list in ATTR_INDEX.values():
        for spec in specs_list:
            k, v = spec.split(":", 1)
            if k == kind:
                out.add(v)
    return out


def emitted_type_moods() -> set[str]:
    base = {"radiusTop": [[4, 5]], "total": 100, "withShadow": 1,
            "lineHeights": [], "weights": [["400", 90]]}
    moods = set()
    for fams in (["Georgia"], ["ui-monospace"], ["Arial"]):
        moods |= set(_classify_intent({**base, "fontFamilies": fams}, {})["type_mood"])
    moods |= set(_classify_intent({**base, "fontFamilies": ["Arial"],
                                   "weights": [["800", 9]]}, {})["type_mood"])
    return moods


def main():
    check("ATTR_INDEX has no duplicate keys", len(ATTR_INDEX) == len(set(ATTR_INDEX)),
          f"{len(ATTR_INDEX)} entries / {len(set(ATTR_INDEX))} unique")

    # every term maps to well-formed specs of known kinds
    known_kinds = {"archetype", "tag", "type_mood", "hue_family", "brightness",
                   "saturation", "corners", "flatness"}
    bad = [spec for lst in ATTR_INDEX.values() for spec in lst
           if spec.split(":", 1)[0] not in known_kinds]
    check("all specs have known kinds", not bad, str(bad))

    # every hue family _hue_family can emit is reachable
    emitted_hues = {_hue_family(h) for h in (0, 30, 55, 100, 180, 230, 275, 320)}
    hue_specs = specs("hue_family")
    missing_hues = emitted_hues - hue_specs
    check("every emitted hue_family reachable in ATTR_INDEX", not missing_hues,
          f"missing: {missing_hues} (have: {sorted(hue_specs)})")

    # every type mood the classifier can emit is reachable
    moods = emitted_type_moods()
    missing_moods = moods - specs("type_mood")
    check("every emitted type_mood reachable in ATTR_INDEX", not missing_moods,
          f"missing: {missing_moods} (emitted: {sorted(moods)})")

    # every archetype the indexer rules can add is a searchable term
    indexer_archetypes = {"funky", "editorial", "brutalist", "minimalist",
                          "glassmorphic", "dark-minimal", "warm-minimal",
                          "playful", "premium", "retro"}
    arch_specs = specs("archetype")
    missing_arch = indexer_archetypes - arch_specs
    check("every indexer archetype reachable in ATTR_INDEX", not missing_arch,
          f"missing: {missing_arch} (have: {sorted(arch_specs)})")

    # the warm/cool alias families cover the warm/cool hues exactly
    warm_specs = set(s.split(":", 1)[1] for s in ATTR_INDEX.get("warm", []))
    check("warm aliases are hue_family specs",
          warm_specs == {"orange", "yellow", "red", "pink"}, str(sorted(warm_specs)))
    cool_specs = set(s.split(":", 1)[1] for s in ATTR_INDEX.get("cool", []))
    check("cool aliases are hue_family specs",
          cool_specs == {"blue", "cyan", "green", "purple"}, str(sorted(cool_specs)))

    # the multi-spec terms from the duplicate-key bug class match BOTH categories
    soft_kinds = {s.split(":", 1)[0] for s in ATTR_INDEX.get("soft", [])}
    check("soft covers saturation AND corners",
          soft_kinds == {"saturation", "corners"}, str(sorted(soft_kinds)))
    bold_kinds = {s.split(":", 1)[0] for s in ATTR_INDEX.get("bold", [])}
    check("bold covers type_mood AND tag",
          bold_kinds == {"type_mood", "tag"}, str(sorted(bold_kinds)))

    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
        sys.exit(1)
    print("ALL PASS")


if __name__ == "__main__":
    main()
