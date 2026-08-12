"""design-scope semantic_pass classifier unit tests — pure function, no browser.

Usage:
  python tests/test_semantic_pass.py

Exits 0 on success, 1 on any failed check.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

from _harness import check, finish  # noqa: E402
from semantic_pass import _classify_intent  # noqa: E402


def classify(named=None, **over):
    raw = {"radiusTop": [[4, 5]], "total": 100, "withShadow": 1,
           "lineHeights": [["1.5", 8]], "fontFamilies": ["Arial"],
           "weights": [["400", 90]]}
    raw.update(over)
    return _classify_intent(raw, named or {})


def test_corner_style_boundaries():
    for r, want in ((1, "sharp"), (2, "sharp"), (4, "soft"), (8, "soft"),
                    (12, "rounded"), (16, "rounded"), (20, "generous")):
        got = classify(radiusTop=[[r, 5]])["corner_style"]
        check(f"radius {r}px → {want}", got == want, str(got))


def test_flatness():
    check("shadow ratio <2% → flat",
          classify(withShadow=1)["flat"] is True)
    check("shadow ratio ≥2% → elevated",
          classify(withShadow=5)["flat"] is False)
    check("no elements → not flat", classify(total=0)["flat"] is False)


def test_type_mood():
    check("serif family → serif-led",
          classify(fontFamilies=["Source Serif Pro", "Arial"])["type_mood"] == ["serif-led"])
    check("mono family → mono-accent",
          classify(fontFamilies=["ui-monospace"])["type_mood"] == ["mono-accent"])
    check("heavy weights → bold-led",
          classify(weights=[["700", 60], ["400", 30]])["type_mood"] == ["bold-led"])
    check("nothing → neutral-sans",
          classify(fontFamilies=["Arial"], weights=[["400", 90]])["type_mood"] == ["neutral-sans"])


def test_vibe_no_brand_tokens():
    check("--muted token → soft", classify(named={"--muted": "#888"})["vibe"] == ["soft"])
    check("no tokens → clean", _classify_intent(
        {"radiusTop": [[4, 5]], "total": 10, "withShadow": 0,
         "lineHeights": [], "fontFamilies": [], "weights": []},
        {"--blurple": "#5865f2"})["vibe"] == ["clean"],
        "brand tokens must not influence the heuristic")
    check("generic --grey → soft", _classify_intent(
        {"radiusTop": [], "total": 10, "withShadow": 0,
         "lineHeights": [], "fontFamilies": [], "weights": []},
        {"--grey": "#777"})["vibe"] == ["soft"])


def test_vocabulary_guard():
    """The classifier may only emit values the search layer understands."""
    allowed_moods = {"serif-led", "mono-accent", "bold-led", "neutral-sans"}
    allowed_corners = {"sharp", "soft", "rounded", "generous"}
    samples = [
        classify(fontFamilies=["Georgia"]),
        classify(fontFamilies=["ui-monospace"]),
        classify(weights=[["800", 9]]),
        classify(fontFamilies=["Arial"]),
        classify(radiusTop=[[1, 1]]),
        classify(radiusTop=[[8, 1]]),
        classify(radiusTop=[[16, 1]]),
        classify(radiusTop=[[40, 1]]),
        classify(withShadow=0),
        classify(withShadow=50),
    ]
    for s in samples:
        check("type_mood in vocabulary",
              all(m in allowed_moods for m in s["type_mood"]), str(s["type_mood"]))
        if s["corner_style"] is not None:
            check("corner_style in vocabulary",
                  s["corner_style"] in allowed_corners, str(s["corner_style"]))


if __name__ == "__main__":
    test_corner_style_boundaries()
    test_flatness()
    test_type_mood()
    test_vibe_no_brand_tokens()
    test_vocabulary_guard()
    finish()
