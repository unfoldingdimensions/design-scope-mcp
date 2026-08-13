"""design-scope page_structure unit tests — the band contract.

Usage:
  python tests/test_page_structure.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from page_structure import DEFAULT_PLAN, MECHANISM_BUDGET, BAND_TYPES, plan  # noqa: E402


def test_plan_shape():
    p = plan("blueprint sheet for design-scope", "measured technical")
    check("10 declared bands", p["declared_bands"] == 10, str(p["declared_bands"]))
    check("mechanism budget 4", p["mechanism_budget"] == 4, str(p["mechanism_budget"]))
    check("band order matches sheet", [b["type"] for b in p["bands"]] == DEFAULT_PLAN)
    check("every band type known", all(b["type"] in BAND_TYPES for b in p["bands"]))
    check("every band carries a note", all(b["note"] for b in p["bands"]))
    check("brief preserved", p["brief"] == "blueprint sheet for design-scope")
    check("direction preserved", p["direction"] == "measured technical")
    mechs = [b for b in p["bands"] if b["mechanism"]]
    check("mechanism bands match budget", len(mechs) == MECHANISM_BUDGET, str(len(mechs)))


def test_plan_validation():
    try:
        plan("   ")
        check("empty brief rejected", False)
    except ValueError:
        check("empty brief rejected", True)


def test_direction_vote():
    p = plan("sheet", "funky")
    v = p["direction_vote"]
    check("vote ran", "votes" in v, str(v))


if __name__ == "__main__":
    test_plan_shape()
    test_plan_validation()
    test_direction_vote()
    finish()
