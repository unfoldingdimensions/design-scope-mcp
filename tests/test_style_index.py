"""design-scope style_index unit tests — vectors, hue boundaries, fixture cards.

Runs against a temp fixture library — NEVER touches the real library/cards.

Usage:
  python tests/test_style_index.py

Exits 0 on success, 1 on any failed check.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

import style_index  # noqa: E402

from _harness import check, finish  # noqa: E402


def test_hex_to_hsl():
    check("hex form", style_index._hex_to_hsl("#ff0000") == (0.0, 1.0, 0.5))
    check("rgb form", style_index._hex_to_hsl("rgb(255, 0, 0)") == (0.0, 1.0, 0.5))
    check("garbage → None", style_index._hex_to_hsl("var(--x)") is None)
    # producer contract: semantic_pass._hex emits 3- and 8-digit forms — the
    # consumer must parse them or those colors drop out of the vectors
    check("short hex parses", style_index._hex_to_hsl("#fff") == (0.0, 0.0, 1.0))
    check("8-digit hex parses (alpha stripped)",
          style_index._hex_to_hsl("#ff0000e6") == (0.0, 1.0, 0.5))


def test_hue_family_boundaries():
    cases = [(0, "red"), (14.9, "red"), (15, "orange"), (44.9, "orange"),
             (45, "yellow"), (69.9, "yellow"), (70, "green"), (159.9, "green"),
             (160, "cyan"), (199.9, "cyan"), (200, "blue"), (259.9, "blue"),
             (260, "purple"), (289.9, "purple"), (290, "pink"), (344.9, "pink"),
             (345, "red")]
    for h, want in cases:
        check(f"hue {h} → {want}", style_index._hue_family(h) == want,
              style_index._hue_family(h))


def _write(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def test_build_vectors_fixture():
    with tempfile.TemporaryDirectory() as tmp:
        cards = Path(tmp) / "cards"

        # card a: serif-led editorial-ish, blue accent, soft corners, flat
        _write(cards / "serif-a" / "semantic.json", {
            "url": "https://a.example",
            "semantic_colors": {"light": {"--accent": "#336699"}},
            "design_intent": {"vibe": ["clean"], "corner_style": "soft",
                              "flat": True, "type_mood": ["serif-led"]},
        })
        _write(cards / "serif-a" / "fingerprint.json", {})

        # card b: dark mono with neutral palette + legacy vocabulary strings
        _write(cards / "dark-b" / "semantic.json", {
            "url": "https://b.example",
            "design_intent": {"vibe": ["clean"], "corner_style": "rounded",
                              "flat": True, "type_mood": ["mono accents"]},
        })
        _write(cards / "dark-b" / "fingerprint.json", {
            "colors": {"palette": [{"normalized": "#111111"}]},
        })

        style_index.CARDS = cards
        style_index.OUT_JSON = Path(tmp) / "style-index.json"
        style_index.OUT_MD = Path(tmp) / "style-summary.md"

        index = style_index.build_vectors()
        check("fixture: 2 cards indexed", len(index["cards"]) == 2,
              str(sorted(index["cards"])))

        a = index["cards"]["serif-a"]
        check("vector hue from palette", a["vector"]["hue_family"] == "blue",
              str(a["vector"]))
        check("vector saturation vibrant", a["vector"]["saturation"] == "vibrant",
              str(a["vector"]["saturation"]))
        check("vector corners from semantic", a["vector"]["corners"] == "soft")
        check("vector flatness", a["vector"]["flatness"] == "flat")
        check("vector type mood", a["vector"]["type_mood"] == "serif-led")
        check("paths present", a["paths"]["screenshot"].endswith("cards/serif-a/screenshot-desktop.png"))
        check("palette curated", a["palette"] == [{"name": "--accent", "hex": "#336699"}])

        b = index["cards"]["dark-b"]
        check("legacy type_mood normalized", b["vector"]["type_mood"] == "mono-accent",
              str(b["vector"]["type_mood"]))
        check("neutral hue from gray palette", b["vector"]["hue_family"] == "neutral")
        check("brightness unknown w/o bg", b["vector"]["brightness"] == "unknown")

        # artifact writes
        style_index.write_summary(index)
        check("summary written", style_index.OUT_MD.exists())
        check("summary search path is library/",
              "library/style_search.py" in style_index.OUT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    test_hex_to_hsl()
    test_hue_family_boundaries()
    test_build_vectors_fixture()
    finish()
