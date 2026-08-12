"""
design-scope behavior pass — captures HOW a design moves and reacts,
not just how it looks. Upgrade over the plain motion pass: instead of a
video + hover screenshots, this documents the *mechanisms* with exact
before/after computed values, per the interaction-sweep methodology from
ai-website-cloner-template (MIT, see library/extraction/).

Outputs into <card_dir>/motion/ (alongside the existing motion pass):
  behaviors.md               — human-readable behavior bible (scroll triggers,
                               hover diffs, interaction models, state captures)
  behaviors.json             — machine-readable same data
  hover-before-NN.png        — element in default state
  hover-after-NN.png         — same element hovered (computed diff recorded)

Usage (called from capture.py):
    behavior_pass(card_dir, url, browser) -> dict summary

Never raises — additive to the card. If a page is static, the report
honestly says "no behaviors detected" instead of fabricating any.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from capture import CHROME_UA, NAV_TIMEOUT_MS

# JS: hover-diff probe — snap computed styles of the Nth element matching a
# selector (index pinned so before/after hit the SAME element that was hovered).
#
# No scrollIntoView here: it used to run after the snap but BEFORE the "after"
# screenshot, sliding the element out from under the mouse so the capture could
# show the un-hovered state. The probe only reads; the caller does the scrolling.
#
# 'outline' is deliberately not probed — the computed value embeds currentColor,
# so it changes whenever 'color' does. It was the single most-reported "hover
# behavior" in the library (252 occurrences) while carrying no signal of its own.
HOVER_PROBE_JS = """(arg) => {
  const { selector, index } = JSON.parse(arg);
  const els = document.querySelectorAll(selector);
  const el = els[index] || els[0];
  if (!el) return null;
  const props = ['color','backgroundColor','borderColor','boxShadow','transform',
    'opacity','filter','textDecoration','backgroundImage','scale'];
  const cs = getComputedStyle(el);
  const out = {};
  props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto') out[p] = v; });
  return JSON.stringify(out);
}"""

# JS: scroll-trigger probe — does any element change computed style at scroll?
SCROLL_PROBE_JS = """() => {
  const interesting = [...document.querySelectorAll('header, nav, [class*="nav"], [class*="header"], [class*="sticky"], [class*="fixed"]')];
  const out = [];
  interesting.slice(0, 12).forEach(el => {
    const cs = getComputedStyle(el);
    const box = el.getBoundingClientRect();
    out.push({ sel: el.tagName.toLowerCase() + '.' + (el.className?.toString().split(' ')[0] || ''),
               top: Math.round(box.top), position: cs.position,
               boxShadow: cs.boxShadow, background: cs.backgroundColor,
               backdropFilter: cs.backdropFilter });
  });
  return JSON.stringify(out);
}"""

# JS: interaction model detection — find click-driven vs scroll-driven sections
INTERACTION_PROBE_JS = """() => {
  const out = { clickables: 0, tabs: 0, accordions: 0, carousels: 0, observers: 0,
                scrollSnap: 0, smoothScroll: null, marquees: 0 };
  out.clickables = document.querySelectorAll('a[href], button, [role="button"], input, select, [onclick]').length;
  out.tabs = document.querySelectorAll('[role="tab"], [role="tablist"], [class*="tab"], [class*="pill"]').length;
  out.accordions = document.querySelectorAll('[class*="accordion"], details, summary').length;
  out.carousels = document.querySelectorAll('[class*="carousel"], [class*="slider"], [class*="marquee"]').length;
  out.observers = document.querySelectorAll('[data-observer], [data-animate], [class*="reveal"], [class*="fade-in"], [class*="animate-"]').length;
  out.scrollSnap = document.querySelectorAll('[class*="scroll-snap"], [class*="snap-"]').length;
  out.smoothScroll = document.querySelector('.lenis, .locomotive-scroll, [data-scroll-container]') ? 'smooth-scroll-lib' : null;
  out.marquees = document.querySelectorAll('[class*="marquee"], [class*="ticker"]').length;
  return JSON.stringify(out);
}"""

# JS: full behavior snapshot of key interactive elements (states & content)
STATES_PROBE_JS = """() => {
  const els = [...document.querySelectorAll('[role="tab"], [class*="tab"], [class*="pill"], [class*="accordion"] summary, [class*="carousel"] button, [class*="slider"] button')].slice(0, 8);
  return JSON.stringify(els.map((el, i) => ({
    idx: i,
    tag: el.tagName.toLowerCase(),
    classes: el.className?.toString().slice(0, 80),
    text: el.textContent?.trim().slice(0, 60),
    ariaSelected: el.getAttribute('aria-selected'),
    ariaExpanded: el.getAttribute('aria-expanded')
  })));
}"""


def diff_states(before: dict, after: dict) -> dict:
    """Computed-style diff for one element, default state vs hovered.

    Iterates the UNION of both snapshots. The probe omits 'none' values, so a
    hover that ADDS a box-shadow or transform yields a key present only in
    `after`; iterating `before` alone silently dropped it.
    """
    return {k: {"before": before.get(k), "after": after.get(k)}
            for k in sorted(set(before) | set(after))
            if before.get(k) != after.get(k)}


def _js(page, script: str, arg=None) -> str | None:
    try:
        if arg is None:
            return page.evaluate(script)
        return page.evaluate(script, arg)
    except Exception:  # noqa: BLE001
        return None


def behavior_pass(card_dir: Path, url: str, browser) -> dict:
    """Document design behavior: scroll triggers, hover diffs, interaction models."""
    motion_dir = card_dir / "motion"
    motion_dir.mkdir(parents=True, exist_ok=True)
    out = {"ok": False, "hover_diffs": 0, "scroll_triggers": 0, "interaction_model": None,
           "error": None, "behaviors_file": "motion/behaviors.md"}
    report = {"url": url, "captured": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "hover_diffs": [], "scroll_probe": [], "interaction_model": {}, "states": []}

    ctx = None
    try:
        ctx = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=CHROME_UA,
        )
        page = ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)
        resp = page.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
        status = resp.status if resp else "?"
        if status and status >= 400:
            raise RuntimeError(f"HTTP {status}")
        page.wait_for_timeout(2000)

        # 1. interaction model probe
        model_raw = _js(page, INTERACTION_PROBE_JS)
        if model_raw:
            report["interaction_model"] = json.loads(model_raw)
            model = report["interaction_model"]
            out["interaction_model"] = (
                "scroll-driven" if (model.get("scrollSnap") or model.get("smoothScroll") or model.get("observers"))
                else "click-driven" if (model.get("tabs") or model.get("accordions") or model.get("carousels")
                                        or model.get("clickables", 0) > 30)
                else "static")
            print(f"      behavior: interaction model = {out['interaction_model']} "
                  f"(clickables={model.get('clickables')}, tabs={model.get('tabs')}, "
                  f"observers={model.get('observers')}, snap={model.get('scrollSnap')})")

        # 2. scroll-trigger probe: capture header/nav state at top, scroll, re-capture
        scroll_before = _js(page, SCROLL_PROBE_JS)
        for _ in range(6):
            page.mouse.wheel(0, 600)
            page.wait_for_timeout(300)
        scroll_after = _js(page, SCROLL_PROBE_JS)
        if scroll_before and scroll_after:
            try:
                before = json.loads(scroll_before)
                after = json.loads(scroll_after)
                for b, a in zip(before, after):
                    # position props always change on scroll — not triggers; skip them
                    diffs = {k: f"{b.get(k)} → {a.get(k)}" for k in b
                             if b.get(k) != a.get(k) and k not in ("top", "left", "right", "bottom")}
                    if diffs:
                        report["scroll_probe"].append({"selector": b["sel"], "diffs": diffs})
                        out["scroll_triggers"] += 1
                if report["scroll_probe"]:
                    print(f"      behavior: {len(report['scroll_probe'])} scroll-triggered style changes")
            except Exception:  # noqa: BLE001
                pass

        # 3. state inventory (tabs/pills/accordions)
        states_raw = _js(page, STATES_PROBE_JS)
        if states_raw:
            try:
                report["states"] = json.loads(states_raw)
            except Exception:  # noqa: BLE001
                pass

        # 4. hover diffs: pick interactive elements, hover, diff computed styles,
        #    save before/after screenshots
        selectors = ["a[href]", "button", ".card", "[role=button]"]
        seen = set()
        for sel in selectors:
            try:
                els = page.query_selector_all(sel)
            except Exception:  # noqa: BLE001
                continue
            for el_index, el in enumerate(els[:4]):
                try:
                    box = el.bounding_box()
                    if not box or box["width"] < 20 or box["height"] < 16:
                        continue
                    key = (sel, round(box["x"]), round(box["y"]))
                    if key in seen:
                        continue
                    seen.add(key)
                    before_json = _js(page, HOVER_PROBE_JS, json.dumps({"selector": sel, "index": el_index}))
                    before = json.loads(before_json) if before_json else {}
                    n = len(report["hover_diffs"]) + 1
                    b_png = motion_dir / f"hover-before-{n:02d}.png"
                    el.screenshot(path=str(b_png))
                    el.hover()
                    page.wait_for_timeout(400)
                    after_json = _js(page, HOVER_PROBE_JS, json.dumps({"selector": sel, "index": el_index}))
                    after = json.loads(after_json) if after_json else {}
                    a_png = motion_dir / f"hover-after-{n:02d}.png"
                    try:
                        el.screenshot(path=str(a_png))
                    except Exception:  # noqa: BLE001
                        b_png.unlink(missing_ok=True)  # keep pairs consistent
                        raise
                    diffs = diff_states(before, after)
                    if diffs:
                        report["hover_diffs"].append({"selector": sel, "index": n, "diffs": diffs,
                                                      "before_png": b_png.name, "after_png": a_png.name})
                        out["hover_diffs"] += 1
                    else:
                        # no visual change — drop the screenshots, keep it honest
                        b_png.unlink(missing_ok=True)
                        a_png.unlink(missing_ok=True)
                except Exception:  # noqa: BLE001
                    continue
            if len(report["hover_diffs"]) >= 5:
                break
        if out["hover_diffs"]:
            print(f"      behavior: {out['hover_diffs']} hover diffs recorded (before/after computed styles)")

        # write behaviors.md + behaviors.json
        md = ["# Behavior report", "",
              f"- **URL:** {url}", f"- **Captured:** {report['captured']}",
              f"- **Interaction model:** {out['interaction_model']}", "",
              "## Interaction model", f"- {json.dumps(report['interaction_model'], indent=2)}", ""]
        md.append("## Scroll-triggered changes")
        if report["scroll_probe"]:
            for sp in report["scroll_probe"]:
                md.append(f"- `{sp['selector']}`")
                for k, v in sp["diffs"].items():
                    md.append(f"  - {k}: {v}")
        else:
            md.append("- none detected (header/nav unchanged on scroll)")
        md.append("")
        md.append("## Hover diffs (before → after)")
        if report["hover_diffs"]:
            for hd in report["hover_diffs"]:
                md.append(f"- `{hd['selector']}` ({hd['before_png']} → {hd['after_png']})")
                for k, d in hd["diffs"].items():
                    md.append(f"  - {k}: `{d['before']}` → `{d['after']}`")
        else:
            md.append("- none detected (elements did not change computed style on hover)")
        md.append("")
        md.append("## State inventory")
        if report["states"]:
            for s in report["states"]:
                md.append(f"- `{s['tag']}.{s['classes']}` text={s['text']!r} "
                          f"selected={s['ariaSelected']} expanded={s['ariaExpanded']}")
        else:
            md.append("- no tabs/pills/accordions detected")
        (motion_dir / "behaviors.md").write_text("\n".join(md), encoding="utf-8")
        (motion_dir / "behaviors.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        out["ok"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:200]
    finally:
        if ctx:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001
                pass
    return out
