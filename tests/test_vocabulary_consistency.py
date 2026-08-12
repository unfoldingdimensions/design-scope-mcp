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

from _harness import check, finish  # noqa: E402
from semantic_pass import _classify_intent  # noqa: E402
from style_index import _hue_family  # noqa: E402
from style_search import ARCHETYPE_KIN, ATTR_INDEX  # noqa: E402


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
    # NOT `len(ATTR_INDEX) == len(set(ATTR_INDEX))` — ATTR_INDEX is a dict
    # literal, so Python collapsed any duplicate key at parse time and that
    # comparison is a tautology that passes no matter what. A duplicate key is
    # only observable as a LOST spec, so assert the specs are all still there.
    every_spec = [s for lst in ATTR_INDEX.values() for s in lst]
    multi = {k: v for k, v in ATTR_INDEX.items() if len(v) > 1}
    check("multi-category terms kept all their specs (dup-key class)",
          all(isinstance(v, list) and v for v in ATTR_INDEX.values()) and len(multi) >= 4,
          f"{len(every_spec)} specs, {len(multi)} multi-spec terms")

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

    # Every archetype needs kin tags, or queries for it tie at a single score
    # and top_n degenerates into an alphabetical slice (the 53 "funky" hits
    # all scored an identical 3 before ARCHETYPE_KIN existed).
    missing_kin = indexer_archetypes - set(ARCHETYPE_KIN)
    check("every indexer archetype has ranking kin", not missing_kin,
          f"missing: {sorted(missing_kin)}")
    thin = {a: len(k) for a, k in ARCHETYPE_KIN.items() if len(k) < 2}
    check("kin sets can clear the 2-hit threshold", not thin, str(thin))
    stray = set(ARCHETYPE_KIN) - indexer_archetypes
    check("no kin for archetypes the indexer cannot emit", not stray, str(sorted(stray)))

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

    # Same contract genre: every CLI prints characters outside cp1252 ("→",
    # "✓", "✗"), so each must configure its console or it dies mid-run on a
    # Windows terminal — which is exactly how all six shipped.
    lib = Path(__file__).resolve().parent.parent / "library"
    for name in ("style_search", "style_index", "capture", "backfill",
                 "annotate", "regenerate_media"):
        src = (lib / f"{name}.py").read_text(encoding="utf-8")
        check(f"{name} CLI configures utf-8 console", "utf8_stdout()" in src)

    finish()


if __name__ == "__main__":
    main()
