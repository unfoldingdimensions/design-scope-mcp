"""design-scope page_structure unit tests — the band contract (v2).

Usage:
  python tests/test_page_structure.py

Covers both bases: the curated fallback (no band-index.json) and the
corpus-measured plan (fixture band-index). The band-index path is tested by
monkeypatching the module's BAND_INDEX constant to a temp file.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
import page_structure as ps  # noqa: E402


def test_curated_fallback():
    old = ps.BAND_INDEX
    ps.BAND_INDEX = Path(tempfile.mkdtemp()) / "no-band-index.json"  # force the fallback
    try:
        st = ps.plan("blueprint sheet for design-scope", "measured technical")
        check("curated declares 10 bands", st["declared_bands"] == 10, st["basis"])
        check("curated budget 4", st["mechanism_budget"] == 4, str(st["mechanism_budget"]))
        check("curated basis labeled", "curated" in st["basis"])
        mechs = [b for b in st["bands"] if b["mechanism"]]
        check("4 mechanism bands", len(mechs) == 4, str(len(mechs)))
        check("every band carries a note", all(b["note"] for b in st["bands"]))
        check("brief preserved", st["brief"] == "blueprint sheet for design-scope")
    finally:
        ps.BAND_INDEX = old


def test_plan_validation():
    try:
        ps.plan("   ")
        check("empty brief rejected", False)
    except ValueError:
        check("empty brief rejected", True)


def _corpus_index():
    return {"stats": {"scanned": 100, "bands": 400, "per_type": {
        "nav": {"count": 50, "with_state": 10, "share": 0.2},
        "hero": {"count": 60, "with_state": 40, "share": 0.667},
        "footer": {"count": 50, "with_state": 28, "share": 0.56},
        "features-grid": {"count": 40, "with_state": 5, "share": 0.125},
        "product-showcase": {"count": 35, "with_state": 28, "share": 0.8},
        "pricing": {"count": 30, "with_state": 20, "share": 0.667},
        "how-it-works": {"count": 25, "with_state": 8, "share": 0.32},
        "faq": {"count": 20, "with_state": 2, "share": 0.1},
        "feature-spotlight": {"count": 18, "with_state": 9, "share": 0.5},
        "testimonials": {"count": 15, "with_state": 3, "share": 0.2},
        "comparison": {"count": 12, "with_state": 6, "share": 0.5},
        "cta-banner": {"count": 10, "with_state": 9, "share": 0.9},
    }}}


def test_corpus_plan():
    old = ps.BAND_INDEX
    with tempfile.TemporaryDirectory() as td:
        ps.BAND_INDEX = Path(td) / "band-index.json"
        ps.BAND_INDEX.write_text(json.dumps(_corpus_index()), encoding="utf-8")
        try:
            st = ps.plan("pricing page for a design tool")
            types = [b["type"] for b in st["bands"]]
            check("corpus basis labeled", "corpus-measured" in st["basis"], st["basis"])
            check("nav first, footer last", types[0] == "nav" and types[-1] == "footer", str(types))
            check("pricing from brief keyword", "pricing" in types, str(types))
            check("band count ≤ 10", st["declared_bands"] <= 10, str(st["declared_bands"]))
            check("corpus evidence on bands",
                  all(b.get("corpus", {}).get("measured", 0) > 0 for b in st["bands"]),
                  str([b["type"] for b in st["bands"]]))
            mechs = [b for b in st["bands"] if b["mechanism"]]
            check("mechanism budget equals armed count",
                  len(mechs) == st["mechanism_budget"], f"{len(mechs)} vs {st['mechanism_budget']}")
            # footer must stay passive even when its bands hold state (56%)
            ftr = next(b for b in st["bands"] if b["type"] == "footer")
            check("footer stays passive at high state share", not ftr["mechanism"])

            # a brief-requested type the corpus has not measured still renders
            st2 = ps.plan("a ledger and a verdict rubric page")
            types2 = [b["type"] for b in st2["bands"]]
            check("unmeasured purpose types still included",
                  "ledger" in types2 and "feature-spotlight" in types2, str(types2))
            ld = next(b for b in st2["bands"] if b["type"] == "ledger")
            check("unmeasured band carries zeroed corpus evidence",
                  ld["corpus"]["measured"] == 0, str(ld["corpus"]))
        finally:
            ps.BAND_INDEX = old


def test_direction_vote():
    st = ps.plan("sheet", "funky")
    check("vote ran", "votes" in st["direction_vote"], str(st["direction_vote"]))


if __name__ == "__main__":
    test_curated_fallback()
    test_plan_validation()
    test_corpus_plan()
    test_direction_vote()
    finish()
