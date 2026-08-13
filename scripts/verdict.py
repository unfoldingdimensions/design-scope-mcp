#!/usr/bin/env python3
"""design-scope verdict — scored rubric reviewer (the review_page equivalent).

Reads a page's LIVE DOM and grades it against a six-check rubric. Unlike
qa.py (internal pass/fail), verdict.py produces a scored, labelled record —
PASS/UNDER rows with evidence numbers — that can be appended to a public
ledger. A rubric that only ever prints PASS is a logo; UNDER rows are kept.

RUN WITH THE LIBRARY ENV'S PYTHON — the same venv that runs capture.py /
qa.py (playwright installed).

Checks (measured off the rendered document, not the plan):
  1. STRUCTURE · Band allocation   — [data-band] rendered vs <meta name="bands">
  2. STRUCTURE · Mechanism budget  — [data-mechanism] bands actually armed
     (data-armed set by JS when wired, or data-interactive) vs <meta name="mechanisms">
  3. PALETTE  · Palette conformance— every computed ink resolves to a declared
     :root token, or a token at fractional alpha (interpolation of one token
     with transparency is not a third colour)
  4. FABRIC   · Fabric floor       — ambient motion above the fold + pointer
     field + scroll-linked band (data-band-scroll armed). PASS only at 3 of 3 —
     two of three is UNDER (a site can coast on ambient alone; the scroll
     mount is the one that takes deliberate work)
  5. MOTION   · Reduced motion     — every animated element covered by a
     prefers-reduced-motion guard (CSS MQ rule matching the element, or
     data-rm-guarded for JS-driven animation)
  6. MOTION   · Living artefacts   — elements still animating after settle
     (3.5 s) <= 2

Usage:
  python scripts/verdict.py <iteration.html> [--label R2] [--ledger ledger.json]
                             [--palette strict|loose] [--json out.json] [--md out.md]

Exit code = number of UNDER rows (0 = clean 6/6).
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------- pure logic

META_RE = re.compile(r'<meta\s+name="(\w+)"\s+content="([^"]*)"', re.I)
BAND_RE = re.compile(r'data-band=')  # note: does not match data-band-type=
TOKEN_RE = re.compile(r':root\s*\{([^}]*)\}', re.I)
PROP_RE = re.compile(r'(--[\w-]+)\s*:\s*([^;]+);?')
RGB_RE = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)')
HEX_RE = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgb({r}, {g}, {b})"


def parse_meta(html: str) -> dict:
    """Declared counts from <meta name="bands" content="N"> markers."""
    out = {}
    for name, content in META_RE.findall(html):
        out[name] = content
    return out


def count_bands(html: str) -> int:
    return len(BAND_RE.findall(html))


def parse_tokens(css_text: str) -> dict:
    """All --custom-property declarations (name -> raw value) from CSS text."""
    tokens = {}
    for block in TOKEN_RE.findall(css_text):
        for name, value in PROP_RE.findall(block):
            tokens[name.strip()] = value.strip()
    return tokens


def normalize_color(c: str):
    """'rgba(30, 94, 255, 0.5)' or '#1E5EFF' -> ('rgb(30, 94, 255)', alpha). None if not a color."""
    m = RGB_RE.search(c)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        alpha = float(m.group(4)) if m.group(4) is not None else 1.0
        return f"rgb({r}, {g}, {b})", alpha
    if HEX_RE.match(c.strip()):
        return _hex_to_rgb(c.strip()), 1.0
    return None


def token_color_values(tokens: dict) -> set:
    """The set of color VALUES declared by tokens (normalized, alpha stripped)."""
    vals = set()
    for v in tokens.values():
        if v.startswith("--"):
            continue  # var() references resolve elsewhere
        n = normalize_color(v)
        if n:
            vals.add(n[0])
    return vals


def conformance(colors, token_values, tolerance: int = 0) -> list:
    """colors: list of raw computed colors. Returns off-palette records.

    A color passes when its normalized rgb is in the token set, or (alpha < 1)
    its base rgb is in the token set — a token at fractional alpha is a blend
    of ONE declared ink and is not a third colour. tolerance = max per-channel
    distance in 0-255 units (loose mode: 5) for anti-aliasing noise.
    """
    off = []
    for c in colors:
        n = normalize_color(c)
        if not n:
            continue
        rgb, alpha = n
        if rgb in token_values:
            continue
        if tolerance:
            tr, tg, tb = (int(x) for x in re.findall(r"\d+", rgb)[:3])
            near = False
            for t in token_values:
                mr = re.search(r"rgb\((\d+),\s*(\d+),\s*(\d+)", t)
                if not mr:
                    continue
                d = max(abs(tr - int(mr.group(1))), abs(tg - int(mr.group(2))),
                        abs(tb - int(mr.group(3))))
                if d <= tolerance:
                    near = True
                    break
            if near:
                continue
        off.append({"color": c, "normalized": rgb, "alpha": alpha})
    return off


def ledger_read(path: Path) -> list:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def ledger_append(path: Path, row: dict) -> list:
    rows = ledger_read(path)
    rows.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


# ------------------------------------------------------------------ probing

PROBE_JS = r"""(async () => {
  const out = {
    bands: [], mechanisms: [], inks: [], ambient: [], pointerField: 0,
    scrollArmed: 0, animNames: [], living: [], reducedMqRules: []
  };
  const delay = ms => new Promise(res => setTimeout(res, ms));

  // 1. bands + mechanisms
  document.querySelectorAll('[data-band]').forEach(b => {
    out.bands.push({ type: b.getAttribute('data-band-type') || '',
                     mech: b.hasAttribute('data-mechanism'),
                     armed: b.hasAttribute('data-armed') || b.hasAttribute('data-interactive') });
  });

  // 3. inks: every computed background/color/border of visible elements
  const inkProps = ['backgroundColor', 'color', 'borderTopColor', 'borderBottomColor'];
  const seen = new Set();
  document.querySelectorAll('body *').forEach(el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return;
    for (const p of inkProps) {
      const v = s[p];
      if (!v || v === 'transparent' || v === 'rgba(0, 0, 0, 0)') continue;
      const key = p + '|' + v;
      if (seen.has(key)) continue;
      seen.add(key);
      out.inks.push(v);
    }
  });

  // 4. fabric: ambient (auto-animating element in the first viewport)
  const inFirstViewport = el => {
    const r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0 && r.width > 0;
  };
  const ambientTargets = new Set();
  document.getAnimations().forEach(a => {
    const t = a.effect && a.effect.target;
    if (t && inFirstViewport(t) && a.playState === 'running') ambientTargets.add(t);
  });
  out.ambient = [...ambientTargets].map(t =>
    t.tagName.toLowerCase() + '.' + String(t.className).split(' ')[0]).slice(0, 5);
  // pointer field: interactive elements with a transition
  out.pointerField = [...document.querySelectorAll('a, button, [role="button"]')]
    .filter(el => parseFloat(getComputedStyle(el).transitionDuration || '0s') > 0).length;
  // scroll-linked band (armed by JS when actually wired)
  out.scrollArmed = document.querySelectorAll('[data-band-scroll][data-scroll-armed]').length;

  // 5. reduced motion: animated elements + MQ guard rules
  const animEls = [...document.querySelectorAll('*')].filter(el => {
    const s = getComputedStyle(el);
    return s.animationName !== 'none' && s.animationDuration !== '0s';
  });
  const guardSelectors = [];
  // scan stylesheets for prefers-reduced-motion rules that null motion
  for (let s = 0; s < document.styleSheets.length; s++) {
    try {
      const rules = document.styleSheets[s].cssRules;
      for (let i = 0; i < rules.length; i++) {
        const r = rules[i];
        if (r.type === 4 && /prefers-reduced-motion/.test(r.conditionText)) {
          for (let j = 0; j < r.cssRules.length; j++) {
            const rr = r.cssRules[j];
            // a guard rule is one that nulls motion: animation-name: none,
            // animation shorthand, or a near-zero duration/iteration count
            const animProps = ['animation', 'animation-name', 'animation-duration',
                               'animation-iteration-count', 'transition', 'transition-duration'];
            const setsMotion = animProps.some(p => rr.style.getPropertyValue(p) !== '');
            if (setsMotion) {
              guardSelectors.push(rr.selectorText);
              out.reducedMqRules.push({ selector: rr.selectorText, cond: r.conditionText });
            }
          }
        }
      }
    } catch (e) {}
  }
  const coveredByGuard = el => guardSelectors.some(sel => {
    try { return el.matches(sel); } catch (e) { return false; }
  });
  animEls.forEach(el => {
    const s = getComputedStyle(el);
    out.animNames.push({ sel: el.tagName.toLowerCase() + '.' + String(el.className).split(' ')[0],
                         name: s.animationName,
                         guarded: el.hasAttribute('data-rm-guarded') || coveredByGuard(el) });
  });

  // 6. living artefacts: still running after settle
  await delay(3500);
  const livingTargets = new Set();
  document.getAnimations().forEach(a => {
    const t = a.effect && a.effect.target;
    if (t && a.playState === 'running') livingTargets.add(t);
  });
  out.living = [...livingTargets].map(t =>
    t.tagName.toLowerCase() + '.' + String(t.className).split(' ')[0]).slice(0, 8);

  return JSON.stringify(out);
})()"""


def run_verdict(html_path: Path, palette_mode: str = "strict") -> dict:
    """Grade one HTML file. Returns the verdict record (no ledger side effect)."""
    html_abs = html_path.resolve()
    html_text = html_abs.read_text(encoding="utf-8")
    meta = parse_meta(html_text)
    declared_bands = int(meta.get("bands", 0))
    declared_mechs = int(meta.get("mechanisms", 0))
    tokens = parse_tokens(html_text)
    token_vals = token_color_values(tokens)
    tolerance = 5 if palette_mode == "loose" else 0

    checks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        pg = browser.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(html_abs.as_uri(), wait_until="load")
        pg.wait_for_timeout(2500)  # entrance choreography runs once and rests

        raw = pg.evaluate(PROBE_JS)
        data = json.loads(raw) if isinstance(raw, str) else (raw or {})
        browser.close()

    bands = data.get("bands", [])
    rendered_bands = len(bands)
    # 1. band allocation
    checks.append({
        "group": "STRUCTURE", "name": "Band allocation",
        "status": "PASS" if rendered_bands == declared_bands else "UNDER",
        "detail": f"{rendered_bands} of {declared_bands} bands rendered",
        "evidence": {"rendered": rendered_bands, "declared": declared_bands,
                     "types": [b["type"] for b in bands]},
    })

    # 2. mechanism budget
    mech_bands = [b for b in bands if b["mech"]]
    armed = [b for b in mech_bands if b["armed"]]
    checks.append({
        "group": "STRUCTURE", "name": "Mechanism budget",
        "status": "PASS" if len(armed) >= declared_mechs else "UNDER",
        "detail": f"{len(armed)} of {declared_mechs} declared mechanisms armed",
        "evidence": {"armed": len(armed), "declared": declared_mechs,
                     "unarmed": [b["type"] for b in mech_bands if not b["armed"]]},
    })

    # 3. palette conformance
    off = conformance(data.get("inks", []), token_vals, tolerance)
    checks.append({
        "group": "PALETTE", "name": "Palette conformance",
        "status": "PASS" if not off else "UNDER",
        "detail": f"{len(data.get('inks', []))} inks · {len(off)} off-palette · {len(token_vals)} distinct token colors",
        "evidence": {"inks": len(data.get("inks", [])), "off_palette": off[:8],
                     "tokens": len(token_vals), "mode": palette_mode},
    })

    # 4. fabric floor — all three mounts (ambient, pointer field, scroll-linked)
    fabric = {
        "ambient": bool(data.get("ambient")),
        "pointer_field": (data.get("pointerField") or 0) >= 1,
        "scroll_linked": (data.get("scrollArmed") or 0) >= 1,
    }
    fabric_score = sum(fabric.values())
    checks.append({
        "group": "FABRIC", "name": "Fabric floor",
        "status": "PASS" if fabric_score == 3 else "UNDER",
        "detail": f"{fabric_score} of 3 — ambient {fabric['ambient']}, pointer field {fabric['pointer_field']}, scroll-linked {fabric['scroll_linked']}",
        "evidence": fabric,
    })

    # 5. reduced motion guard
    anims = data.get("animNames", [])
    mq_sel = sorted(set(r["selector"] for r in data.get("reducedMqRules", [])))
    unguarded = [a for a in anims if not a.get("guarded")]
    checks.append({
        "group": "MOTION", "name": "Reduced motion",
        "status": "PASS" if not unguarded else "UNDER",
        "detail": f"{len(anims)} animated elements · {len(mq_sel)} MQ guard rules · {len(unguarded)} unguarded",
        "evidence": {"animated": len(anims), "mq_rules": sorted(mq_sel),
                     "unguarded": unguarded[:8]},
    })

    # 6. living artefacts cap
    living = data.get("living", [])
    checks.append({
        "group": "MOTION", "name": "Living artefacts",
        "status": "PASS" if len(living) <= 2 else "UNDER",
        "detail": f"{len(living)} of 2 cap still animating after settle",
        "evidence": {"living": living},
    })

    under = [c for c in checks if c["status"] == "UNDER"]
    return {
        "file": str(html_path),
        "label": None,
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "checks": checks,
        "summary": {
            "pass": len(checks) - len(under),
            "under": len(under),
            "total": len(checks),
            "score": f"{len(checks) - len(under)} PASS · {len(under)} UNDER",
        },
    }


def render_md(verdict: dict) -> str:
    lines = [
        f"# VERDICT — {verdict['label'] or verdict['file']}",
        "",
        f"Graded {verdict['date']} · read off the rendered document, not the plan",
        "",
        "| # | GROUP | CHECK | STATUS |",
        "|---|-------|-------|--------|",
    ]
    for i, c in enumerate(verdict["checks"], 1):
        lines.append(f"| {i} | {c['group']} | {c['name']} | {c['status']} |")
        lines.append(f"|   |       | {c['detail']} | |")
    lines += ["", f"**{verdict['summary']['score']}**", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="HTML file to grade")
    ap.add_argument("--label", default=None, help="row label for the ledger")
    ap.add_argument("--ledger", default=None, help="JSON ledger path to append to")
    ap.add_argument("--palette", choices=["strict", "loose"], default="strict")
    ap.add_argument("--json", default=None, help="write verdict JSON to this path")
    ap.add_argument("--md", default=None, help="write verdict markdown to this path")
    args = ap.parse_args()

    html = Path(args.target)
    if not html.exists():
        print(f"file not found: {html}", file=sys.stderr)
        sys.exit(2)

    verdict = run_verdict(html, args.palette)
    verdict["label"] = args.label

    print(f"VERDICT — {args.label or html.name}")
    for i, c in enumerate(verdict["checks"], 1):
        print(f"  {c['status']:<5} {c['group']:<8} {c['name']}: {c['detail']}")
    print(f"\n  {verdict['summary']['score']}")

    if args.json:
        Path(args.json).write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        print(f"  json -> {args.json}")
    if args.md:
        Path(args.md).write_text(render_md(verdict), encoding="utf-8")
        print(f"  md   -> {args.md}")
    if args.ledger:
        ledger_append(Path(args.ledger), {
            "label": args.label, "date": verdict["date"], "file": str(html),
            "score": verdict["summary"]["score"], "pass": verdict["summary"]["pass"],
            "under": verdict["summary"]["under"],
            "rows": [{"group": c["group"], "name": c["name"], "status": c["status"]}
                     for c in verdict["checks"]],
        })
        print(f"  ledger -> {args.ledger}")

    sys.exit(verdict["summary"]["under"])


if __name__ == "__main__":
    main()
