"""design-scope section_scan unit tests — the deterministic classifier.

Usage:
  python tests/test_section_scan.py

Synthetic signals, no network. Covers every taxonomy type, priority order,
the `other` bucket, and band-index stats.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from section_scan import TAXONOMY, classify, compute_stats  # noqa: E402


def sig(**kw):
    base = dict(tag="section", cls="", h1=False, textLen=200, links=4, navLinks=0,
                lis=0, hasOl=False, buttons=0, inputs=0, details=0, tables=0,
                blockquotes=0, imgs=0, price=False, animated=False, interactive=False,
                first=False)
    base.update(kw)
    return base


def test_classifier_priority():
    cases = [
        (sig(tag="nav", links=6), "nav"),
        (sig(tag="footer"), "footer"),
        (sig(cls="hero", h1=True, first=True), "hero"),
        (sig(cls="pricing-section", price=True), "pricing"),
        (sig(cls="faq", details=3), "faq"),
        (sig(cls="testimonials", blockquotes=3), "testimonials"),
        (sig(cls="comparison", tables=1), "comparison"),
        (sig(cls="how-it-works", hasOl=True, lis=4), "how-it-works"),
        (sig(cls="cta-banner", buttons=2, inputs=1), "cta-banner"),
        (sig(cls="feature-spotlight", imgs=1), "feature-spotlight"),
        (sig(cls="features", imgs=0), "features-grid"),
        (sig(cls="product-showcase", imgs=3), "product-showcase"),
        (sig(cls="", imgs=4, links=5), "product-showcase"),
        (sig(cls="", lis=4, links=3), "features-grid"),
    ]
    for s, want in cases:
        got, _ = classify(s)
        check(f"{want} classified", got == want, f"got {got} for {s['cls']!r}")


def test_hero_content_fallback():
    got, reason = classify(sig(h1=True, first=True, cls=""))
    check("first-h1 block is hero", got == "hero", f"{got} {reason}")


def test_other_bucket_honest():
    got, reason = classify(sig(cls="", textLen=30, imgs=0, lis=1))
    check("no signal → other (never guessed)", got == "other", f"{got} {reason}")
    check("reason explains", bool(reason))


def test_taxonomy_covered():
    covered = {"nav", "hero", "features-grid", "how-it-works", "feature-spotlight",
               "product-showcase", "pricing", "faq", "testimonials", "comparison",
               "cta-banner", "footer"}
    check("all taxonomy types reachable", covered == set(TAXONOMY))


def test_stats():
    idx = {"cards": {
        "a": {"bands": [{"type": "nav", "state": True},
                        {"type": "pricing", "state": False}]},
        "b": {"bands": [{"type": "nav", "state": False}]},
    }, "failures": [{"slug": "c", "error": "wall"}]}
    st = compute_stats(idx)
    check("scanned count", st["scanned"] == 2)
    check("failed count", st["failed"] == 1)
    check("band total", st["bands"] == 3)
    nav = st["per_type"]["nav"]
    check("per-type state share", nav["count"] == 2 and nav["with_state"] == 1
          and abs(nav["share"] - 0.5) < 1e-9, str(nav))


if __name__ == "__main__":
    test_classifier_priority()
    test_hero_content_fallback()
    test_other_bucket_honest()
    test_taxonomy_covered()
    test_stats()
    finish()
