"""
design-scope interaction probe — documents HOW a design moves and reacts,
not just how it looks. Merges the former motion pass (video + hover-state
captures) and behavior pass (computed-style diffs, scroll triggers,
interaction model) into ONE scripted session on a shared page.

Session order (load-bearing — see capture-pipeline-collapse plan):
  interaction-model probe → scroll-reveal sweep → back to top → scroll
  probe (top vs scrolled) → state inventory → hover diffs (before/after
  computed styles + screenshots) → click + go_back LAST (resets page state).

Outputs into <card_dir>/motion/:
  card-motion.webm            — recorded session (finalized by the CALLER
                                after context.close(); video spans the whole
                                shared session, not just this probe)
  behaviors.md                — human-readable behavior bible
  behaviors.json              — machine-readable same data
  hover-before-NN.png / hover-after-NN.png — element default vs hovered
  hover-inventory.json        — element selector + captured state per diff

`interaction_model` in behaviors.json is the classified STRING
("scroll-driven" / "click-driven" / "static"); the raw counter dict lives
in `interaction_signals`.

Usage (called from capture.py / backfill.py):
    interaction_probe(page, card_dir, url) -> dict summary
    behavior_pass(card_dir, url, browser)  -> thin wrapper (own context)

Never raises — additive to the card. If a page is static, the report
honestly says "no behaviors detected" instead of fabricating any.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from capture import CHROME_UA, DESKTOP_VIEWPORT, NAV_TIMEOUT_MS

# JS: hover-diff probe — snap computed styles of the Nth element matching a
# selector (index pinned so before/after hit the SAME element that was hovered).
# NO scrollIntoView: it moved the element out from under the mouse before the
# 'after' screenshot. NO outline: its computed value embeds currentColor, so it
# mirrors any color change — 252 of the library's hover reports were that noise.
HOVER_PROBE_JS = """(arg) => {
  const { selector, index } = JSON.parse(arg);
  const els = document.querySelectorAll(selector);
  const el = els[index] || els[0];
  if (!el) return null;
  const props = ['color','backgroundColor','borderColor','boxShadow','transform',
    'opacity','filter','textDecoration','backgroundImage','scale'];
  const snap = () => {
    const cs = getComputedStyle(el);
    const out = {};
    props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto') out[p] = v; });
    return out;
  };
  return JSON.stringify(snap());
}"""


def diff_states(before: dict, after: dict) -> dict:
    """Diff two computed-style snapshots over the UNION of keys.

    The probe omits 'none'/'normal'/'auto' values, so hover effects that ADD a
    property (box-shadow, transform — the two most common on the web) appear
    only in the `after` snapshot; diffing over `before` alone made them
    invisible. Added properties record before=None, removed record after=None.
    """
    out = {}
    for k in set(before) | set(after):
        b, a = before.get(k), after.get(k)
        if b != a:
            out[k] = {"before": b, "after": a}
    return out

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


def _js(page, script: str, arg=None) -> str | None:
    try:
        if arg is None:
            return page.evaluate(script)
        return page.evaluate(script, arg)
    except Exception:  # noqa: BLE001
        return None


def classify_interaction_model(model: dict) -> str:
    """Deterministic interaction-model classification from the raw counter
    dict produced by INTERACTION_PROBE_JS. Pure — also used to backfill
    legacy behaviors.json files."""
    if (model.get("scrollSnap") or model.get("smoothScroll") or model.get("observers")):
        return "scroll-driven"
    if (model.get("tabs") or model.get("accordions") or model.get("carousels")
            or model.get("clickables", 0) > 30):
        return "click-driven"
    return "static"


# union of the former motion + behavior selector lists (behavior ⊆ motion)
HOVER_SELECTORS = ["a[href]", "button", "input[type=submit]", "[role=button]",
                   ".card", "nav a"]


def interaction_probe(page, card_dir: Path, url: str) -> dict:
    """The merged motion+behavior session on an ALREADY-LOADED page.

    Video is recorded by the caller's context; this probe only does
    interactions and writes the artifact files. The caller finalizes the
    video (context.close() must happen first). Never raises.

    Session order is load-bearing: the click + go_back at the end resets
    page state — nothing may run after it.
    """
    motion_dir = card_dir / "motion"
    motion_dir.mkdir(parents=True, exist_ok=True)
    out = {"ok": False, "hover_diffs": 0, "hovers": 0, "clicks": 0,
           "scroll_triggers": 0, "interaction_model": None, "video": None,
           "error": None, "behaviors_file": "motion/behaviors.md"}
    report = {"url": url, "captured": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "hover_diffs": [], "scroll_probe": [], "interaction_model": {},
              "interaction_signals": {}, "states": []}
    try:
        # 1. interaction model probe
        model_raw = _js(page, INTERACTION_PROBE_JS)
        if model_raw:
            signals = json.loads(model_raw)
            report["interaction_signals"] = signals
            report["interaction_model"] = classify_interaction_model(signals)
            out["interaction_model"] = report["interaction_model"]
            print(f"      behavior: interaction model = {out['interaction_model']} "
                  f"(clickables={signals.get('clickables')}, tabs={signals.get('tabs')}, "
                  f"observers={signals.get('observers')}, snap={signals.get('scrollSnap')})")

        # 2. scroll-reveal sweep, then back to top (motion)
        for _ in range(8):
            page.mouse.wheel(0, 700)
            page.wait_for_timeout(350)
        page.mouse.wheel(0, -99999)
        page.wait_for_timeout(600)

        # 3. scroll-trigger probe: header/nav state at top, scroll, re-capture
        page.evaluate("window.scrollTo(0, 0)")
        scroll_before = _js(page, SCROLL_PROBE_JS)
        for _ in range(6):
            page.mouse.wheel(0, 600)
            page.wait_for_timeout(300)
        scroll_after = _js(page, SCROLL_PROBE_JS)
        if scroll_before and scroll_after:
            try:
                before = json.loads(scroll_before)
                after = json.loads(scroll_after)
                # match by selector — element sets can change between scroll
                # positions (sticky headers appear/hide), and index-paired
                # zip would diff element i against a different element i
                after_by_sel = {}
                for a in after:
                    after_by_sel.setdefault(a["sel"], a)
                for b in before:
                    a = after_by_sel.get(b["sel"])
                    if not a:
                        continue
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

        # 4. state inventory (tabs/pills/accordions) — after scroll reset
        page.evaluate("window.scrollTo(0, 0)")
        states_raw = _js(page, STATES_PROBE_JS)
        if states_raw:
            try:
                report["states"] = json.loads(states_raw)
            except Exception:  # noqa: BLE001
                pass

        # 5. hover diffs: hover interactive elements, diff computed styles,
        #    save before/after screenshots; inventory for elements that changed
        seen = set()
        hovered = 0
        for sel in HOVER_SELECTORS:
            try:
                els = page.query_selector_all(sel)
            except Exception:  # noqa: BLE001
                continue
            for el_index, el in enumerate(els[:4]):
                if len(report["hover_diffs"]) >= 5:
                    break
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
                    hovered += 1
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
        out["hovers"] = hovered
        if out["hover_diffs"]:
            print(f"      behavior: {out['hover_diffs']} hover diffs recorded (before/after computed styles)")
            (motion_dir / "hover-inventory.json").write_text(
                json.dumps({"url": url, "hovers": [
                    {"selector": h["selector"], "file": h["before_png"], "box": {}} for h in report["hover_diffs"]
                ]}, indent=2, ensure_ascii=False), encoding="utf-8")

        # 6. micro-interaction: click the first safe-looking link/button —
        #    LAST: it navigates away and back, resetting all page state
        try:
            clickable = page.query_selector("a[href]") or page.query_selector("button")
            if clickable:
                clickable.click()
                page.wait_for_timeout(700)
                out["clicks"] = 1
                page.go_back(wait_until="load")
                page.wait_for_timeout(500)
        except Exception:  # noqa: BLE001
            pass

        # write behaviors.md + behaviors.json
        md = ["# Behavior report", "",
              f"- **URL:** {url}", f"- **Captured:** {report['captured']}",
              f"- **Interaction model:** {out['interaction_model']}", "",
              "## Interaction model", f"- {json.dumps(report['interaction_signals'], indent=2)}", ""]
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
        (motion_dir / "behaviors.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        out["ok"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:200]
    return out


def behavior_pass(card_dir: Path, url: str, browser) -> dict:
    """Thin wrapper — own context (kept for backfill's selective per-pass
    runs). Returns the behavior-shaped summary. Never raises."""
    ctx = None
    try:
        ctx = browser.new_context(
            viewport=DESKTOP_VIEWPORT, user_agent=CHROME_UA)
        page = ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)
        resp = page.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
        status = resp.status if resp else 0
        if status and status >= 400:
            raise RuntimeError(f"HTTP {status}")
        page.wait_for_timeout(2000)
        res = interaction_probe(page, card_dir, url)
        return {k: res.get(k) for k in ("ok", "hover_diffs", "scroll_triggers",
                                        "interaction_model", "error", "behaviors_file")}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)[:200], "behaviors_file": "motion/behaviors.md"}
    finally:
        if ctx:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001
                pass
