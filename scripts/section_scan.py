#!/usr/bin/env python3
"""design-scope section scan — corpus band inventory (the measured structure).

Visits card URLs, enumerates the page's sections, classifies each into the
band taxonomy, and measures whether the band holds real state (interaction
or animation). Output: library/band-index.json — the corpus the v2
get_page_structure reads. Failures are recorded, never fabricated.

RUN WITH THE LIBRARY ENV'S PYTHON (same venv as capture.py / verdict.py).

Usage:
  python scripts/section_scan.py --sample 40        # first N cards (deterministic)
  python scripts/section_scan.py --cards slug1,slug2
  python scripts/section_scan.py --all              # whole corpus
  python scripts/section_scan.py --all --refresh    # re-scan everything
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()
INDEX = LIBRARY / "index.json"
BAND_INDEX = LIBRARY / "band-index.json"

NAV_TIMEOUT_MS = 25_000

# the taxonomy — aligned with page_structure.BAND_TYPES, plus the section
# types a landing page actually carries
TAXONOMY = [
    "nav", "hero", "features-grid", "how-it-works", "feature-spotlight",
    "product-showcase", "pricing", "faq", "testimonials", "comparison",
    "ledger", "cta-banner", "footer",
]


def _record_failure(idx: dict, slug: str, error: str) -> None:
    """Replace any prior failure for this slug — appending forever inflated
    stats.failed on every re-run even after a card later succeeded."""
    failures = [f for f in idx.get("failures", []) if f.get("slug") != slug]
    failures.append({"slug": slug, "error": error[:200]})
    idx["failures"] = failures

EXTRACT_JS = r"""(() => {
  const out = [];
  const seen = new Set();
  const q = s => document.querySelectorAll(s);
  const cls = el => (el.className && typeof el.className === 'string')
    ? el.className.toLowerCase() : '';
  const inFirst = el => {
    const r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  };
  const cands = [
    ...q('header, nav, main, section, footer, aside'),
    ...q('[data-section], [class*="section"], [class*="band"], [class*="hero"], [class*="pricing"], [class*="faq"], [class*="testimonial"], [class*="feature"], [class*="cta"], [class*="how-it-works"], [class*="steps"], [class*="comparison"], [class*="ledger"], [class*="history"], [class*="footer"], [class*="nav"]')
  ];
  for (const el of cands) {
    const c = cls(el);
    if (seen.has(el)) continue;
    seen.add(el);
    const r = el.getBoundingClientRect();
    if (r.height < 40 || r.width < 120) continue;         // too small to be a band
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') continue;
    // drop candidates nested inside another candidate (keep the topmost)
    if (el.closest('header,nav,main,section,footer,aside,[class*="section"],[class*="band"],[data-section]') && !el.matches('header,nav,main,section,footer,aside')) continue;
    const text = (el.innerText || '').trim();
    const imgs = el.querySelectorAll('img, video, [class*="screenshot"], [class*="product"]').length;
    const buttons = el.querySelectorAll('button, input[type="submit"], a[class*="btn"], a[class*="cta"]').length;
    const inputs = el.querySelectorAll('input, select, textarea').length;
    const details = el.querySelectorAll('details').length;
    const tables = el.querySelectorAll('table').length;
    const blockquotes = el.querySelectorAll('blockquote, [class*="quote"], [class*="testimonial"]').length;
    const links = el.querySelectorAll('a[href]').length;
    const navLinks = el.matches('nav, header') ? el.querySelectorAll('a[href]').length : 0;
    const lis = el.querySelectorAll('li').length;
    const hasOl = el.querySelectorAll('ol').length > 0;
    const price = /[$€£]\s?\d|per month|\/mo|pricing/i.test(text);
    const h1 = el.querySelectorAll('h1').length > 0;
    const animated = [...el.querySelectorAll('*')].some(e => {
      const es = getComputedStyle(e);
      return es.animationName !== 'none' && es.animationDuration !== '0s';
    });
    const interactive = buttons + inputs + details > 0;
    out.push({
      tag: el.tagName.toLowerCase(),
      cls: c.slice(0, 80),
      h1, textLen: text.length, links, navLinks, lis, hasOl,
      buttons, inputs, details, tables, blockquotes, imgs, price,
      animated, interactive,
      first: inFirst(el) && el.querySelector('h1') !== null
    });
  }
  return out;
})()"""


def classify(sig: dict) -> tuple[str, str]:
    """Deterministic classifier: (type, reason). Priority: explicit class
    hints first, then content heuristics. `other` when nothing matches —
    recorded, never guessed."""
    c = sig.get("cls", "")
    if sig.get("tag") == "nav" or "nav" in c or sig.get("navLinks", 0) > 4:
        return "nav", "nav landmark / link cluster"
    if sig.get("tag") == "footer" or "footer" in c:
        return "footer", "footer landmark"
    if "hero" in c or (sig.get("h1") and sig.get("first")):
        return "hero", "hero class or first-h1 block"
    if "pricing" in c or sig.get("price"):
        return "pricing", "pricing class or price markers"
    if "faq" in c or sig.get("details", 0) > 0:
        return "faq", "faq class or <details>"
    if "testimonial" in c or sig.get("blockquotes", 0) >= 2:
        return "testimonials", "testimonial class or quotes"
    if "comparison" in c or (sig.get("tables", 0) > 0 and sig.get("textLen", 0) > 200):
        return "comparison", "comparison class or data table"
    if "ledger" in c or "history" in c:
        return "ledger", "ledger/history class (append-only record table)"
    if "how-it-works" in c or "steps" in c or (sig.get("hasOl") and sig.get("lis", 0) >= 3):
        return "how-it-works", "steps class or ordered list"
    if "cta" in c or (sig.get("buttons", 0) >= 2 and sig.get("inputs", 0) >= 1):
        return "cta-banner", "cta class or button+form cluster"
    if "feature" in c:
        return "feature-spotlight" if sig.get("imgs", 0) >= 1 else "features-grid", "feature class"
    if "product" in c or "showcase" in c or "screenshot" in c or sig.get("imgs", 0) >= 2:
        return "product-showcase", "product/showcase class or media cluster"
    if sig.get("imgs", 0) >= 3 and sig.get("links", 0) >= 4:
        return "product-showcase", "rich media + links"
    if sig.get("lis", 0) >= 3 and sig.get("links", 0) >= 3:
        return "features-grid", "card list (li cluster)"
    return "other", "no strong signal"


def scan_one(page, url: str) -> dict:
    page.set_default_timeout(NAV_TIMEOUT_MS)
    page.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
    page.wait_for_timeout(2500)  # entrance choreography plays
    raw = page.evaluate(EXTRACT_JS)
    bands = []
    for i, sig in enumerate(raw, 1):
        kind, reason = classify(sig)
        bands.append({
            "index": i,
            "type": kind,
            "state": bool(sig.get("interactive") or sig.get("animated")),
            "reason": reason,
            "signals": {k: sig[k] for k in ("textLen", "buttons", "inputs", "details",
                                            "tables", "blockquotes", "imgs", "animated",
                                            "interactive")},
        })
    return {"url": url, "bands": bands}


def load_band_index() -> dict:
    if BAND_INDEX.exists():
        return json.loads(BAND_INDEX.read_text(encoding="utf-8"))
    return {"cards": {}, "stats": {}, "failures": []}


def save_band_index(idx: dict) -> None:
    idx["stats"] = compute_stats(idx)
    BAND_INDEX.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")


def compute_stats(idx: dict) -> dict:
    per = {}
    total = 0
    for slug, rec in (idx.get("cards") or {}).items():
        for b in rec.get("bands", []):
            total += 1
            t = b["type"]
            e = per.setdefault(t, {"count": 0, "with_state": 0})
            e["count"] += 1
            if b["state"]:
                e["with_state"] += 1
    return {
        "scanned": len(idx.get("cards", {})),
        "failed": len(idx.get("failures", [])),
        "bands": total,
        "per_type": {t: {**v, "share": round(v["with_state"] / v["count"], 3) if v["count"] else 0}
                     for t, v in sorted(per.items(), key=lambda kv: -kv[1]["count"])},
    }


def slugs_for(args, cards_dir: Path) -> list[str]:
    if args.cards:
        return [s.strip() for s in args.cards.split(",") if s.strip()]
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    all_slugs = list(idx.get("cards", {}).keys())
    if args.all:
        return all_slugs
    if args.sample:
        return all_slugs[: args.sample]
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", default=None, help="comma-separated slugs")
    ap.add_argument("--sample", type=int, default=0, help="first N cards (deterministic)")
    ap.add_argument("--all", action="store_true", help="whole corpus")
    ap.add_argument("--refresh", action="store_true", help="re-scan already-scanned cards")
    args = ap.parse_args()

    idx = load_band_index()
    already = set(idx.get("cards", {}))
    urls = {}
    if INDEX.exists():
        cards = json.loads(INDEX.read_text(encoding="utf-8")).get("cards", {})
        for slug in slugs_for(args, LIBRARY / "cards"):
            if slug in cards and (args.refresh or slug not in already):
                urls[slug] = cards[slug].get("url")
    if not urls:
        print("nothing to scan (all scanned? use --refresh)", file=sys.stderr)
        sys.exit(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        ok = 0
        for slug, url in urls.items():
            if not url or not url.startswith(("http://", "https://")):
                _record_failure(idx, slug, "no url in index")
                continue
            try:
                rec = scan_one(page, url)
                idx["cards"][slug] = {"url": url, "scanned_at": _now(), "bands": rec["bands"]}
                ok += 1
                print(f"  ok {slug}: {len(rec['bands'])} bands "
                      f"({', '.join(b['type'] for b in rec['bands'][:6])}…)")
            except Exception as e:  # noqa: BLE001 — record, never fabricate
                _record_failure(idx, slug, str(e))
                print(f"  FAIL {slug}: {str(e)[:120]}")
        browser.close()

    save_band_index(idx)
    st = idx["stats"]
    print(f"\nband-index: {st['scanned']} scanned · {st['failed']} failed · {st['bands']} bands")
    for t, v in st["per_type"].items():
        print(f"  {t:<18} {v['count']:>4} bands · {v['with_state']:>4} hold state ({v['share']:.0%})")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    main()
