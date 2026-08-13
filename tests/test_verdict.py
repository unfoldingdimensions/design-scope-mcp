"""design-scope verdict unit tests — pure rubric logic, no Playwright.

Usage:
  python tests/test_verdict.py

Exits 0 on success, 1 on any failed check. The Playwright probe itself is
exercised end-to-end against the showcase artifact (see scripts/verdict.py
usage); these tests pin the pure parts: meta parsing, band counting, token
parsing, palette conformance, and the ledger.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from verdict import (  # noqa: E402
    conformance, count_bands, ledger_append, ledger_read, normalize_color,
    parse_meta, parse_tokens, token_color_values,
)


def test_parse_meta():
    html = '<meta name="bands" content="10"><meta name="mechanisms" content="4">'
    meta = parse_meta(html)
    check("bands meta parsed", meta.get("bands") == "10", str(meta))
    check("mechanisms meta parsed", meta.get("mechanisms") == "4", str(meta))
    check("missing meta -> absent key", "nope" not in meta, str(meta))


def test_count_bands():
    html = ('<section data-band="nav" data-band-type="nav"></section>'
            '<section data-band="hero" data-band-type="hero" data-mechanism></section>'
            '<div data-band-type="footer"></div>')  # type-only must NOT count
    check("data-band counted, data-band-type not", count_bands(html) == 2, str(count_bands(html)))


def test_parse_tokens():
    css = """:root {
      --paper: #F6F6F1;
      --accent: rgb(30, 94, 255);
      --ease: cubic-bezier(0.19, 1, 0.22, 1);
    }"""
    tokens = parse_tokens(css)
    check("hex token parsed", tokens.get("--paper") == "#F6F6F1", str(tokens))
    check("rgb token parsed", tokens.get("--accent") == "rgb(30, 94, 255)", str(tokens))
    check("non-color token kept", "--ease" in tokens, str(tokens))
    vals = token_color_values(tokens)
    check("token color values extracted", "rgb(30, 94, 255)" in vals and "rgb(246, 246, 241)" in vals,
          str(vals))
    check("non-color token excluded", len(vals) == 2, str(vals))


def test_normalize_color():
    n = normalize_color("rgba(30, 94, 255, 0.5)")
    check("rgba splits base+alpha", n == ("rgb(30, 94, 255)", 0.5), str(n))
    n = normalize_color("rgb(1, 2, 3)")
    check("rgb default alpha 1", n == ("rgb(1, 2, 3)", 1.0), str(n))
    check("non-color -> None", normalize_color("none") is None)


def test_conformance():
    tokens = {"--accent": "rgb(30, 94, 255)", "--ink": "#14181F"}
    vals = token_color_values(tokens)
    # exact token
    off = conformance(["rgb(30, 94, 255)"], vals)
    check("exact token passes", off == [], str(off))
    # token at fractional alpha (blend of ONE ink) passes
    off = conformance(["rgba(30, 94, 255, 0.4)"], vals)
    check("token@alpha passes (not a third colour)", off == [], str(off))
    # invented colour fails
    off = conformance(["rgb(200, 20, 20)"], vals)
    check("invented colour fails", len(off) == 1 and off[0]["normalized"] == "rgb(200, 20, 20)",
          str(off))
    # hex token value matched against rgb computed form
    off = conformance(["rgb(20, 24, 31)"], vals)
    check("hex token matched via rgb form", off == [], str(off))
    # tolerance: near-token passes only in loose mode
    off = conformance(["rgb(32, 96, 253)"], vals, tolerance=5)
    check("loose tolerance accepts AA noise", off == [], str(off))
    off = conformance(["rgb(32, 96, 253)"], vals)
    check("strict mode rejects near-token", len(off) == 1, str(off))


def test_ledger_roundtrip():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "verdicts.json"
        check("empty ledger reads []", ledger_read(p) == [])
        row = {"label": "R1", "score": "4 PASS · 2 UNDER", "pass": 4, "under": 2}
        ledger_append(p, row)
        ledger_append(p, {"label": "R2", "score": "5 PASS · 1 UNDER", "pass": 5, "under": 1})
        rows = ledger_read(p)
        check("ledger appends rows", len(rows) == 2 and rows[0]["label"] == "R1"
              and rows[1]["label"] == "R2", str(rows))
        check("ledger rows keep score", rows[1]["score"] == "5 PASS · 1 UNDER")
        # append must not clobber existing rows
        ledger_append(p, {"label": "R3"})
        check("ledger grows, never clobbers", len(ledger_read(p)) == 3)


def test_ledger_never_fabricated():
    """Rows are only ever appended by real runs — read of a missing file yields []."""
    with tempfile.TemporaryDirectory() as td:
        check("no ledger -> no rows", ledger_read(Path(td) / "nope.json") == [])


if __name__ == "__main__":
    test_parse_meta()
    test_count_bands()
    test_parse_tokens()
    test_normalize_color()
    test_conformance()
    test_ledger_roundtrip()
    test_ledger_never_fabricated()
    finish()
