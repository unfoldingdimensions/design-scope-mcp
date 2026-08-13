"""design-scope blueprint unit tests — the skeleton contract.

Usage:
  python tests/test_blueprint.py

The rendered skeleton must declare exactly what the structure declared —
the verdict measures the rendered document against those meta tags.
"""
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
    # mechanism flags rendered
    for b in st["bands"]:
        if b["mechanism"]:
            check(f"mechanism band {b['type']} marked", "data-mechanism" in html, b["type"])
    # markers preserved for the builder
    check("data marker kept", "/*__DATA__*/" in html)
    check("token markers kept", "/*__TOKENS_LIGHT__*/" in html and "/*__TOKENS_DARK__*/" in html)
    # scroll-linked scaffolding present (fabric floor 3/3)
    check("scroll scaffolding present", "data-band-scroll" in html)
    check("IO wiring present", "IntersectionObserver" in html)
    # theme toggle + status dot (ambient + pointer field)
    check("theme toggle present", 'id="themeBtn"' in html)
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
