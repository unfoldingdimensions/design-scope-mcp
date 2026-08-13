"""design-scope stats unit tests — corpus counting over a synthetic fixture.

Usage:
  python tests/test_stats.py

Exits 0 on success, 1 on any failed check. Builds a tiny fake library in a
temp dir so the real 204-card library is never touched.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from stats import compute  # noqa: E402


def make_library(td: Path) -> Path:
    """A 3-card fake library: one fully verified, one missing annotation,
    one dark-themed, one missing motion."""
    lib = td / "library"
    cards = lib / "cards"
    cards.mkdir(parents=True)

    def card(slug, dark=False, annotated=True, motion=True, why=True):
        d = cards / slug
        d.mkdir()
        (d / "fingerprint.json").write_text("{}", encoding="utf-8")
        (d / "source.md").write_text("# src", encoding="utf-8")
        nt = {"light": {"--a": "1px"}}
        if dark:
            nt["dark"] = {"--b": "2px"}
        (d / "semantic.json").write_text(
            json.dumps({"named_tokens": nt, "semantic_colors": {}}), encoding="utf-8")
        if annotated:
            (d / "annotation.json").write_text("[]", encoding="utf-8")
        if motion:
            m = d / "motion"
            m.mkdir()
            (m / "behaviors.json").write_text("[]", encoding="utf-8")
        md = "## why\nfine" if why else "## why\n(annotation pending)"
        (d / "card.md").write_text(md, encoding="utf-8")

    card("one", annotated=True, why=True)            # full
    card("two", dark=True, annotated=False, why=True)  # no annotation, dark
    card("tre", motion=False, why=False)             # no motion, pending why

    (lib / "index.json").write_text(json.dumps(
        {"version": 1, "cards": {"one": {}, "two": {}, "tre": {}},
         "stats": {"total": 3}}), encoding="utf-8")
    (lib / "style-index.json").write_text(json.dumps(
        {"cards": {
            "one": {"archetypes": ["funky"], "vector": {"hue_family": "blue"}},
            "two": {"archetypes": ["funky", "retro"], "vector": {"hue_family": "blue"}},
            "tre": {"archetypes": ["editorial"], "vector": {"hue_family": "neutral"}},
        }}), encoding="utf-8")
    return lib


def test_counts():
    with tempfile.TemporaryDirectory() as td:
        s = compute(make_library(Path(td)))
        c = s["corpus"]
        check("captured counts card dirs", c["captured"] == 3, str(c))
        check("annotated excludes pending", c["annotated"] == 2, str(c))
        check("motion excludes missing", c["motion"] == 2, str(c))
        check("behaviors matches motion", c["behaviors"] == 2, str(c))
        check("dark themed detected from named_tokens", c["dark_themed"] == 1, str(c))
        check("annotated_why excludes pending", c["annotated_why"] == 2, str(c))
        check("style indexed", c["style_indexed"] == 3, str(c))


def test_style_tallies():
    with tempfile.TemporaryDirectory() as td:
        s = compute(make_library(Path(td)))
        st = s["styles"]
        arch = dict(st["top_archetypes"])
        hues = dict(st["top_hues"])
        check("archetypes tallied", arch.get("funky") == 2 and arch.get("retro") == 1, str(arch))
        check("hues tallied", hues.get("blue") == 2 and hues.get("neutral") == 1, str(hues))
        check("archetype tag total", st["archetype_total_tags"] == 4, str(st))


def test_mcp_contract():
    with tempfile.TemporaryDirectory() as td:
        s = compute(make_library(Path(td)))
        m = s["mcp"]
        check("server name", m["name"] == "design-scope", str(m))
        check("both transports listed", set(m["transports"]) == {"stdio", "streamable-http"}, str(m))
        names = [t[0] for t in m["tools"]]
        check("9 tools", len(names) == 9 and "style_search" in names and "theme_borrow" in names,
              str(names))


if __name__ == "__main__":
    test_counts()
    test_style_tallies()
    test_mcp_contract()
    finish()
