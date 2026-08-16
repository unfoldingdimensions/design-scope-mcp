"""design-scope blueprint unit tests — the skeleton contract.

Usage:
  python tests/test_blueprint.py

The rendered skeleton must declare exactly what the structure declared —
the verdict measures the rendered document against those meta tags.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from blueprint import render  # noqa: E402
import page_structure as ps  # noqa: E402


def test_skeleton_matches_structure():
    st = ps.plan("blueprint sheet for design-scope", "measured technical")
    html = render(st)
    # meta contract
    check("meta bands matches structure",
          f'name="bands" content="{st["declared_bands"]}"' in html)
    check("meta mechanisms matches structure",
          f'name="mechanisms" content="{st["mechanism_budget"]}"' in html)
    # one data-band per structure band
    for b in st["bands"]:
        check(f"band {b['type']} rendered",
              f'data-band="{b["type"]}"' in html)
    # mechanism flags rendered ON THE BAND, not merely anywhere in the page
    for b in st["bands"]:
        if b["mechanism"]:
            pat = re.compile(
                r'<[^>]*data-band="%s"[^>]*' % re.escape(b["type"]))
            on_band = any("data-mechanism" in m for m in pat.findall(html))
            check(f"mechanism band {b['type']} marked on its band", on_band, b["type"])
    # every internal anchor resolves (id/href parity — the shipped one-shot
    # sheet once had 10/10 dead links from unpadded ids vs padded hrefs)
    ids = set(re.findall(r'id="(s\d+)"', html))
    hrefs = set(re.findall(r'href="#(s\d+)"', html))
    dead = sorted(hrefs - ids)
    check("all internal anchors resolve", not dead, f"dead: {dead}")
    # band ids are zero-padded to two digits (s01..sNN)
    padded = all(len(i[1:]) == 2 for i in ids)
    check("band ids zero-padded", padded, str(sorted(ids)))
    # the sticky nav must live OUTSIDE the .sheet container (full-width stick)
    check("nav outside .sheet",
          re.search(r'<nav class="nav"[^>]*>', html).start()
          < html.index('<div class="sheet">'), "nav must precede .sheet")
    # markers preserved for the builder
    check("data marker kept", "/*__DATA__*/" in html)
    check("token markers kept", "/*__TOKENS_LIGHT__*/" in html and "/*__TOKENS_DARK__*/" in html)
    # scroll-linked scaffolding present (fabric floor 3/3)
    check("scroll scaffolding present", "data-band-scroll" in html)
    check("IO wiring present", "IntersectionObserver" in html)
    # reveal is real: bands hidden only when JS present, revealed class armed
    check("reveal gated on .js", ".js .band" in html and ".js .band.revealed" in html)
    # theme toggle + status dot (ambient + pointer field)
    check("theme toggle present", 'id="themeBtn"' in html)
    check("theme toggle state exposed", 'aria-pressed' in html)
    check("status dot present", "status-dot" in html)
    # fill markers tell the agent what to do
    check("fill markers present", 'class="fill"' in html)


def test_curated_fallback_contract():
    import tempfile
    old = ps.BAND_INDEX
    ps.BAND_INDEX = Path(tempfile.mkdtemp()) / "no-band-index.json"
    try:
        st = ps.plan("pricing page for a design tool")
        check("curated fallback declares 10", st["declared_bands"] == 10, st["basis"])
        check("curated basis labeled", "curated" in st["basis"])
    finally:
        ps.BAND_INDEX = old


if __name__ == "__main__":
    test_skeleton_matches_structure()
    test_curated_fallback_contract()
    finish()
