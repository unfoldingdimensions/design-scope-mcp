"""
design-scope semantic pass — the INTENT layer of a design system, matching
what uidrop-style extractors report. Complements fingerprint.json (measured
evidence) + behaviors.md (interaction mechanisms).

Outputs into <card_dir>/semantic.json:
  1. named_tokens    — CSS custom properties from :root / [data-theme=dark],
                       with one level of var() resolution (--blurple → #5865f2)
  2. design_intent   — deterministic classifier: vibe, rhythm, flatness,
                       corner style, type mood (from measured data, honest)
  3. z_index         — max z-index per component role (nav/dropdown/modal/...)
  4. responsive      — @media rules as "at <bp>px — <selector> → <change>"

Usage (called from capture.py / backfill.py):
    semantic_pass(card_dir, url, browser) -> dict summary

Never raises — additive. If a layer finds nothing, it says so.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from capture import CHROME_UA, NAV_TIMEOUT_MS

# JS: walk all stylesheets, extract CSS custom property declarations from
# theme-ish blocks, z-index rules, and @media rules — all in one pass.
# Cross-origin sheets (CDN-hosted CSS) are unreadable via cssRules; we
# record them as unreadable and ALSO collect inline <style> text so the
# Python side can regex-fallback for :root tokens.
SEMANTIC_JS = r"""() => {
  const out = { customProps: [], zIndex: [], media: [], unreadable: [], inlineCss: [] };
  const roleRe = /nav|dropdown|modal|toast|tooltip|popover|overlay|menu|notification|sidebar|header|dialog|banner|snackbar|drawer/i;
  const mediaThreshRe = /(\d+(?:\.\d+)?)\s*px/;

  const isThemeSelector = (sel) => {
    const s = sel.toLowerCase();
    return s.includes(':root') || s === 'html' || s.includes('data-theme') ||
           s.includes('theme-dark') || s.includes('theme-light') || s.includes('.dark');
  };

  const walk = (rules, mediaCtx) => {
    for (const rule of rules) {
      try {
        if (rule.type === 4) { // @media
          const th = mediaThreshRe.exec(rule.conditionText);
          const ctx = {
            query: rule.conditionText,
            threshold: th ? parseFloat(th[1]) : null,
            entries: []
          };
          walk(rule.cssRules, ctx);
          if (ctx.entries.length) out.media.push(ctx);
        } else if (rule.type === 1) { // style rule
          const sel = rule.selectorText;
          const style = rule.style;
          if (style) {
            // custom properties (only from theme-ish selectors)
            if (isThemeSelector(sel)) {
              for (let i = 0; i < style.length; i++) {
                const p = style[i];
                if (p.startsWith('--')) {
                  out.customProps.push({ selector: sel, name: p, value: style.getPropertyValue(p).trim() });
                }
              }
            }
            // z-index
            if (sel && roleRe.test(sel)) {
              const z = style.getPropertyValue('z-index');
              if (z && z !== 'auto') {
                out.zIndex.push({ selector: sel.slice(0, 80), value: z });
              }
            }
            // inside a media query: record property changes
            if (mediaCtx && style.length) {
              for (let i = 0; i < style.length && i < 6; i++) {
                const p = style[i];
                if (p.startsWith('--')) continue;
                const v = style.getPropertyValue(p).trim();
                if (v && p !== 'display' || (p === 'display' && v && v !== 'flex' && v !== 'block')) {
                  // keep meaningful changes; skip empty
                  mediaCtx.entries.push({ selector: sel.slice(0, 80), prop: p, value: v.slice(0, 60) });
                }
              }
            }
          }
        }
      } catch (e) { /* cross-origin sheets are unreadable — skip */ }
    }
  };

  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules, null); }
    catch (e) {
      if (sheet.href) out.unreadable.push(sheet.href.slice(0, 120));
    }
  }
  // inline <style> text — always readable, fallback for :root tokens
  document.querySelectorAll('style').forEach(s => { out.inlineCss.push(s.textContent.slice(0, 60000)); });
  return JSON.stringify(out);
}"""

# JS: design-intent probes — measured facts the classifier consumes
INTENT_JS = r"""() => {
  const els = [...document.querySelectorAll('body *')].slice(0, 4000);
  let withShadow = 0, total = els.length;
  let radiusCount = {}, shadowSeen = 0, lineHeights = {}, lineCount = 0;
  let fontFamilies = new Set(), weights = {};
  els.forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.boxShadow && cs.boxShadow !== 'none') { withShadow++; shadowSeen++; }
    const r = parseFloat(cs.borderRadius);
    if (r > 0) { radiusCount[r] = (radiusCount[r] || 0) + 1; }
    if (el.tagName === 'P' || el.tagName === 'DIV') {
      const lh = parseFloat(cs.lineHeight);
      if (lh > 0 && lh < 5) { lineHeights[lh.toFixed(1)] = (lineHeights[lh.toFixed(1)] || 0) + 1; lineCount++; }
    }
    const ff = (cs.fontFamily || '').split(',')[0].trim().toLowerCase();
    if (ff && ff !== 'inherit') fontFamilies.add(ff);
    const w = cs.fontWeight;
    weights[w] = (weights[w] || 0) + 1;
  });
  const topRadius = Object.entries(radiusCount).sort((a, b) => b[1] - a[1]).slice(0, 4);
  const topLine = Object.entries(lineHeights).sort((a, b) => b[1] - a[1]).slice(0, 3);
  return JSON.stringify({
    total, withShadow,
    radiusTop: topRadius.map(([r, c]) => [parseFloat(r), c]),
    lineHeights: topLine,
    fontFamilies: [...fontFamilies].slice(0, 6),
    weights: Object.entries(weights).sort((a, b) => b[1] - a[1]).slice(0, 4)
  });
}"""


def _js(page, script: str):
    try:
        return page.evaluate(script)
    except Exception:  # noqa: BLE001
        return None


def _hex(value: str) -> str | None:
    """Resolve a CSS value to a plain hex color when possible."""
    v = value.strip().lower()
    m = re.fullmatch(r'#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})', v)
    if m:
        return v
    m2 = re.fullmatch(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', v)
    if m2:
        r, g, b = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


def _resolve_vars(custom: list[dict]) -> dict[str, str]:
    """Resolve one level of var() references; returns name -> concrete value."""
    by_selector: dict[str, dict[str, str]] = {}
    for cp in custom:
        by_selector.setdefault(cp["selector"], {})[cp["name"]] = cp["value"]
    resolved: dict[str, str] = {}
    for sel, props in by_selector.items():
        for name, value in props.items():
            v = value.strip()
            m = re.fullmatch(r'var\((--[\w-]+)\)', v)
            if m and m.group(1) in props:
                v = props[m.group(1)].strip()
            resolved[name] = v
    return resolved


def _classify_intent(raw: dict, named: dict) -> dict:
    """Deterministic design-intent classifier from measured facts."""
    intent = {"vibe": [], "rhythm": [], "flat": None, "corner_style": None,
              "type_mood": [], "note": "heuristic synthesis of measured data"}

    # corner style from dominant radius
    rt = raw.get("radiusTop") or []
    if rt:
        r, c = rt[0]
        if r <= 2:
            intent["corner_style"] = "sharp"
        elif r <= 8:
            intent["corner_style"] = "soft"
        elif r <= 16:
            intent["corner_style"] = "rounded"
        else:
            intent["corner_style"] = "generous"
    # flatness
    total = raw.get("total") or 1
    shadow_ratio = (raw.get("withShadow") or 0) / total
    intent["flat"] = shadow_ratio < 0.02

    # vibe — honest heuristic from generic named tokens (no brand-specific
    # names): muted/grey tokens read as "soft", otherwise "clean"
    vibes = []
    if any(k in named for k in ("--muted", "--text-muted", "--grey", "--subtle")):
        vibes.append("soft")
    if not vibes:
        vibes.append("clean")
    intent["vibe"] = vibes

    # rhythm from line heights + corners
    rhythm = []
    lh = raw.get("lineHeights") or []
    if lh:
        top_lh = float(lh[0][0])
        rhythm.append("tight line-height" if top_lh <= 1.4 else "airy line-height")
    if intent["corner_style"]:
        rhythm.append(f"{intent['corner_style']} corners")
    if intent["flat"]:
        rhythm.append("flat (no shadows)")
    else:
        rhythm.append("elevated (soft shadows)")
    intent["rhythm"] = rhythm

    # type mood — vocabulary MUST match style_search.ATTR_INDEX type_mood values
    # (case-insensitive: the JS probe lowercases, but other callers may not)
    mood = []
    families = [f.lower() for f in (raw.get("fontFamilies") or [])]
    if any("serif" in f for f in families):
        mood.append("serif-led")
    if any("mono" in f or "monospace" in f for f in families):
        mood.append("mono-accent")
    weights = raw.get("weights") or []
    if weights and int(weights[0][0]) >= 700:
        mood.append("bold-led")
    if not mood:
        mood.append("neutral-sans")
    intent["type_mood"] = mood
    return intent


def semantic_pass(card_dir: Path, url: str, browser) -> dict:
    """Extract the intent layer: named tokens, design intent, z-index, responsive."""
    out = {"ok": False, "named_tokens": 0, "z_index": 0, "responsive_rules": 0,
           "design_intent": None, "error": None, "file": "semantic.json"}
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
        page.wait_for_timeout(1800)

        raw = _js(page, SEMANTIC_JS) or "{}"
        data = json.loads(raw)
        intent_raw = json.loads(_js(page, INTENT_JS) or "{}")

        # cross-origin fallback: if cssRules extraction found nothing (CDN CSS),
        # (a) regex :root / [data-theme] blocks from inline <style> text,
        # (b) fetch unreadable stylesheet hrefs via page.evaluate(fetch) —
        #     network fetch is NOT subject to the CSSOM same-origin rule
        if not data.get("customProps"):
            css_text = "\n".join(data.get("inlineCss") or [])
            # (a) inline style text
            for m in re.finditer(r":root\s*\{([^}]*)\}", css_text):
                for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
                    data["customProps"].append({"selector": ":root", "name": name.strip(), "value": val.strip()})
            for m in re.finditer(r'\[data-theme="dark"\]\s*\{([^}]*)\}', css_text):
                for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
                    data["customProps"].append({"selector": '[data-theme="dark"]', "name": name.strip(), "value": val.strip()})
            # (b) fetch unreadable CDN sheets
            for href in (data.get("unreadable") or [])[:10]:
                try:
                    fetched = page.evaluate(
                        "async (u) => { try { const r = await fetch(u); return await r.text(); } catch (e) { return ''; } }",
                        href)
                except Exception:  # noqa: BLE001
                    fetched = ""
                if not fetched or len(fetched) < 200:
                    continue
                for m in re.finditer(r":root\s*\{([^}]*)\}", fetched[:200000]):
                    for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
                        data["customProps"].append({"selector": ":root", "name": name.strip(), "value": val.strip()})
                for m in re.finditer(r'\[data-theme="dark"\]\s*\{([^}]*)\}', fetched[:200000]):
                    for name, val in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", m.group(1)):
                        data["customProps"].append({"selector": '[data-theme="dark"]', "name": name.strip(), "value": val.strip()})

        # 1. named tokens (theme blocks only), var-resolved
        # selector parity with SEMANTIC_JS isThemeSelector: :root/html/
        # data-theme/theme-dark/theme-light/.dark
        custom = data.get("customProps", [])
        theme_props = [cp for cp in custom
                       if cp.get("selector") and (
                           ":root" in cp["selector"].lower()
                           or cp["selector"].lower() == "html"
                           or "data-theme" in cp["selector"].lower()
                           or "theme-dark" in cp["selector"].lower()
                           or "theme-light" in cp["selector"].lower()
                           or ".dark" in cp["selector"].lower())]
        named = _resolve_vars(theme_props)

        # split light/dark by selector
        named_light, named_dark = {}, {}
        for cp in theme_props:
            target = named_dark if "dark" in cp["selector"].lower() else named_light
            target.setdefault(cp["name"], cp["value"])
        for d in (named_light, named_dark):
            for k, v in list(d.items()):
                m = re.fullmatch(r'var\((--[\w-]+)\)', v.strip())
                if m and m.group(1) in d:
                    d[k] = d[m.group(1)]

        # curated semantic colors: names with NO digits (--blurple yes,
        # --brand-560 no) whose value resolves to a color — the uidrop-style
        # "Named color tokens" list
        def _semantic_colors(d: dict) -> dict:
            out = {}
            for k, v in d.items():
                if re.fullmatch(r"--[a-z][a-z-]*", k) and _hex(v):
                    out[k] = v
            return dict(sorted(out.items()))

        semantic_colors_light = _semantic_colors(named_light)
        semantic_colors_dark = _semantic_colors(named_dark)

        # 2. z-index by role (tolerant of var() references / non-numeric)
        z_by_role: dict[str, int] = {}
        z_rows = []
        for z in data.get("zIndex", []):
            raw_z = z.get("value", "0")
            try:
                m = re.search(r"-?\d+(?:\.\d+)?", raw_z)
                val = int(float(m.group(0))) if m else 0
            except Exception:  # noqa: BLE001
                val = 0
            sel = z.get("selector", "")
            role = None
            for word in ("nav", "dropdown", "modal", "toast", "tooltip", "popover",
                         "overlay", "menu", "notification", "sidebar", "header",
                         "dialog", "banner", "snackbar", "drawer"):
                if word in sel.lower():
                    role = word
                    break
            role = role or "other"
            z_by_role[role] = max(z_by_role.get(role, 0), val)
            z_rows.append({"role": role, "selector": sel, "value": raw_z})
        z_by_role = dict(sorted(z_by_role.items(), key=lambda kv: -kv[1]))

        # 3. responsive rules
        responsive = []
        for mq in data.get("media", []):
            th = mq.get("threshold")
            for e in mq.get("entries", [])[:12]:
                responsive.append({
                    "at": f"{int(th)}px" if th else mq.get("query", "?")[:40],
                    "selector": e.get("selector", "?"),
                    "change": f"{e.get('prop')}: {e.get('value')}",
                })
        responsive = responsive[:40]

        # 4. design intent
        intent = _classify_intent(intent_raw, named)

        sem = {
            "url": url,
            "captured": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "named_tokens": {"light": named_light, "dark": named_dark},
            "semantic_colors": {
                "light": semantic_colors_light,
                "dark": semantic_colors_dark,
                "note": "curated: names with no digits whose value is a color",
            },
            "design_intent": intent,
            "z_index": z_by_role,
            "z_index_rows": z_rows[:15],
            "responsive": responsive,
        }
        (card_dir / "semantic.json").write_text(
            json.dumps(sem, indent=2, ensure_ascii=False), encoding="utf-8")

        out.update({
            "ok": True,
            "named_tokens": len(named_light) + len(named_dark),
            "z_index": len(z_by_role),
            "responsive_rules": len(responsive),
            "design_intent": intent,
        })
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:200]
    finally:
        if ctx:
            try:
                ctx.close()
            except Exception:  # noqa: BLE001
                pass
    return out
