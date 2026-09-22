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


def test_vendor_tokens_filtered():
    """A capture must not advertise an embedded framework's tokens as the site's.

    Regression: cards/linear/semantic.json shipped X's --tweet-* embed tokens as
    Linear's palette (metabase the Bootstrap --bs-* set, ledger/oura the
    WordPress --wp--preset--* set), so theme_borrow returned the embed's colors.
    """
    from semantic_pass import curated_semantic_colors, is_vendor_token

    raw = {
        "--tweet-bg-color": "#fff",                # X embed
        "--tweet-color-blue-primary": "#1d9bf0",   # X embed
        "--bs-blue": "#0d6efd",                    # Bootstrap
        "--wp--preset--color--black": "#000000",   # WordPress
        "--chakra-colors-black": "#000000",        # Chakra UI
        "--brand": "#1e5eff",                      # the site's own
        "--blurple": "#5865f2",                    # the site's own
        "--brand-560": "#112233",                  # digits: not curated
        "not-a-token": "#fff",                     # not a custom property
    }
    kept, dropped = curated_semantic_colors(raw)
    check("site tokens survive the vendor filter",
          set(kept) == {"--brand", "--blurple"}, str(sorted(kept)))
    check("vendor tokens are dropped from curated colors",
          not ({"--tweet-bg-color", "--bs-blue", "--wp--preset--color--black",
                "--chakra-colors-black"} & set(kept)), str(sorted(kept)))
    check("dropped vendor names are recorded, not silently discarded",
          set(dropped) == {"--tweet-bg-color", "--tweet-color-blue-primary",
                           "--bs-blue", "--wp--preset--color--black",
                           "--chakra-colors-black"}, str(dropped))
    check("digit names still excluded", "--brand-560" not in kept, str(sorted(kept)))
    check("double-dash namespace does not catch a site's own --wp-* token",
          not is_vendor_token("--wp-brand") and is_vendor_token("--wp--preset--color--black"))
    check("ordinary tokens are not vendor",
          not is_vendor_token("--swatch--accent") and not is_vendor_token("--bg"))


if __name__ == "__main__":
    test_corner_style_boundaries()
    test_flatness()
    test_type_mood()
    test_vibe_no_brand_tokens()
    test_vocabulary_guard()
    test_vendor_tokens_filtered()
    finish()
