"""design-scope section_blueprint unit tests — the contracted recipe.

Usage:
  python tests/test_section_blueprint.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from section_blueprint import RECIPES, blueprint  # noqa: E402


def test_every_recipe_complete():
    for t, r in RECIPES.items():
        check(f"{t} has label", bool(r.get("label")))
        check(f"{t} has contents", len(r.get("contents", [])) >= 1)
        check(f"{t} has mechanism contract", bool(r.get("mechanism")))


def test_blueprint_shape():
    b = blueprint("pricing")
    check("type echoed", b["type"] == "pricing")
    check("label present", b["label"] == "Pricing")
    check("contents list", isinstance(b["contents"], list) and len(b["contents"]) >= 3)
    check("mechanism present", bool(b["mechanism"]))
    check("corpus block shaped",
          isinstance(b.get("corpus"), dict)
          and {"measured", "with_state", "share"} <= set(b["corpus"]),
          str(b.get("corpus")))
    # corpus numbers are internally consistent: with_state ≤ measured, share in [0,1]
    c = b["corpus"]
    if c.get("measured"):
        check("with_state within measured", c["with_state"] <= c["measured"], str(c))
        check("share in [0,1]", 0 <= c["share"] <= 1, str(c))


def test_unknown_type_rejected():
    try:
        blueprint("nonsense")
        check("unknown type rejected", False)
    except ValueError:
        check("unknown type rejected", True)


if __name__ == "__main__":
    test_every_recipe_complete()
    test_blueprint_shape()
    test_unknown_type_rejected()
    finish()
