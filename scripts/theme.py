#!/usr/bin/env python3
# MIRRORED from the design-scope skill (scripts/compare.py / theme.py).
# Canonical home: <skill>/scripts/ — update both copies together.
"""design-scope theme — borrow a reference card's palette as a theme.

Formalizes the improvised "swap this card's palette in" flow. Reads a card's
semantic.json (named tokens + curated semantic colors, light+dark) and emits:
  - a token remap table (current token → borrowed value)
  - a ready CSS :root block (both themes if the card has dark tokens)
  - a borrow list (what you're gaining vs your current fingerprint)

CONTRAST GUARD: any borrowed accent/text that fails WCAG AA against the
card's own background (or your target background when given) is darkened/
lightened until it passes, with before→after ratios logged — the R5 lesson
(mint #70ffaf was 3.06:1 on white, darkened to 4.58:1).

Usage:
  python theme.py <card-slug> [--target <project-dir>] [--out <dir>]
Output: <out>/.hermes/design/themes/<card>.md  (default out = target or cwd)
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Global library: DESIGN_SCOPE_LIBRARY env var, else the repo library relative
# to this file (the copy that ships in the repo lives in scripts/), else the
# canonical dev-machine location (the skill-dir copy has no library sibling).
def _default_library() -> Path:
    candidates = [Path(__file__).resolve().parent.parent / "library",
                  Path(r"E:\New-Personal-Projects\Ui Design MCP\library")]
    for c in candidates:
        if (c / "index.json").exists():
            return c
    return candidates[0]


GLOBAL_LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(_default_library()))).resolve()

AA_NORMAL = 4.5


def _lum(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a: str, b: str) -> float:
    la, lb = _lum(a), _lum(b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def _darken(hex_color: str, step: float = 0.03) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = max(0, round(r * (1 - step)))
    g = max(0, round(g * (1 - step)))
    b = max(0, round(b * (1 - step)))
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color: str, step: float = 0.03) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, round(r + (255 - r) * step))
    g = min(255, round(g + (255 - g) * step))
    b = min(255, round(b + (255 - b) * step))
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_of(value: str) -> str | None:
    """Normalize a CSS color to 6-digit hex. Accepts 3/6/8-digit hex (alpha
    stripped) and rgb() — 8-digit is common in real token dumps (#000000e6)."""
    v = value.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        elif len(h) == 8:
            h = h[:6]  # strip alpha
        return f"#{h.lower()}"
    m2 = re.fullmatch(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", v)
    if m2:
        return f"#{int(m2.group(1)):02x}{int(m2.group(2)):02x}{int(m2.group(3)):02x}"
    return None


def _hls_sat(hex_color: str) -> float:
    """HLS saturation of a hex color (0 = gray, 1 = full)."""
    import colorsys
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    _hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return ss * (1 - abs(2 * ll - 1))  # toward HSV-style saturation


def _guard(color: str, bg: str, dark_bg: str | None = None) -> tuple[str, list[str]]:
    """Darken/lighten until AA normal passes on the given bg. Logs the journey."""
    notes = []
    cur = color
    ratio = _contrast(cur, bg)
    if ratio >= AA_NORMAL:
        return cur, notes
    for _ in range(12):
        lighter = _lighten(cur)
        darker = _darken(cur)
        if _contrast(lighter, bg) > _contrast(cur, bg):
            cur = lighter
        else:
            cur = darker
        ratio = _contrast(cur, bg)
        if ratio >= AA_NORMAL:
            break
    notes.append(f"contrast guard: {color} {_contrast(color, bg):.2f}:1 → {cur} {ratio:.2f}:1 on {bg}")
    return cur, notes


def borrow_theme(slug: str, target: str = ".") -> dict:
    """Borrow a card's palette as a theme: roles + CSS + contrast-guard notes.

    Returns dict with roles (light+dark), css blocks, notes, and the full
    markdown. Shared with the MCP server (mcp_server.py imports this).
    Raises ValueError if the card has no usable tokens.
    """
    card_dir = GLOBAL_LIBRARY / "cards" / slug
    sem_path = card_dir / "semantic.json"
    if not sem_path.exists():
        raise ValueError(f"card '{slug}' has no semantic.json (looked in {card_dir})")
    sem = json.loads(sem_path.read_text(encoding="utf-8"))

    target_p = Path(target)
    fp_path = target_p / ".hermes" / "design" / "fingerprint.json"
    current = json.loads(fp_path.read_text(encoding="utf-8")) if fp_path.exists() else {}
    fp = current  # alias: the target's fingerprint defines "current"

    sc = sem.get("semantic_colors", {}).get("light", {})
    sc_dark = sem.get("semantic_colors", {}).get("dark", {})

    # fingerprint semantic colors as a bg/text tiebreaker — the card's token
    # vocabulary may be swatch-named (--swatch--accent) with no real bg token.
    # NOTE: Dembrandt's semantic keys are background/text/primary, not bg/text.
    fp_sem = (fp.get("colors") or {}).get("semantic", {}) or {}
    FP_KEY = {"bg": "background", "text": "text", "muted": "muted", "primary": "primary"}

    def pick_any(role: str, prefers: list[str]) -> tuple[str, str] | None:
        # 1. semantic-named tokens first
        for name in prefers:
            v = sc.get(name) or sc_dark.get(name)
            if v:
                hx = _hex_of(v)
                if hx:
                    return name, hx
        # 2. fingerprint semantic (real measured bg/text) — beats swatch tokens
        fp_key = FP_KEY.get(role)
        if fp_key and fp_sem.get(fp_key):
            hx = _hex_of(str(fp_sem[fp_key]))
            if hx:
                return f"(fingerprint {role})", hx
        # 3. swatch vocabularies (--swatch--*): role by luminance — lightest
        #    swatch ≈ bg, darkest ≈ text, mid ≈ muted, accent = first saturated
        if role in ("bg", "text", "muted"):
            swatches = [(name, v) for name, v in sc.items()
                        if v and _hex_of(v) and "swatch" in name]
            if swatches:
                graded = sorted(swatches, key=lambda kv: _lum(_hex_of(kv[1]) or "#000"))
                if role == "text":
                    return graded[0]  # darkest
                if role == "bg":
                    return graded[-1]  # lightest
                if len(graded) >= 3:
                    return graded[len(graded) // 2]  # mid
        # 4. role-aware last resort — "first color-valued token" for EVERY role
        #    once collapsed whole palettes to one value (all-black borrows)
        parsed = []
        for name, v in sc.items():
            hx = _hex_of(v) if v else None
            if hx:
                parsed.append((name, hx))
        if not parsed:
            return None
        if role == "text":
            return None  # no real text token — derived from bg after picking
        if role in ("accent", "primary"):
            return max(parsed, key=lambda kv: _hls_sat(kv[1]))
        if role == "muted":
            calm = [kv for kv in parsed if _hls_sat(kv[1]) <= 0.25] or parsed
            return sorted(calm, key=lambda kv: abs(_lum(kv[1]) - 0.5))[0]
        return parsed[0]

    roles = {}
    for role, prefers in {
        "primary": ["--blurple", "--brand", "--color-primary", "--primary", "--accent"],
        "accent": ["--spring-green", "--accent", "--color-accent", "--green", "--secondary"],
        "bg": ["--bg", "--background", "--color-bg", "--surface-0", "--black", "--white"],
        "text": ["--text", "--color-text", "--foreground", "--white", "--black"],
        "muted": ["--text-muted", "--muted", "--greyple", "--dim-grey", "--color-muted"],
    }.items():
        hit = pick_any(role, prefers)
        if hit:
            roles[role] = {"token": hit[0], "value": hit[1]}

    if not roles:
        raise ValueError(f"card '{slug}' has no color tokens usable for a theme")
    if "bg" not in roles:
        raise ValueError(f"card '{slug}' has no usable background token for a theme "
                         f"(looked for --bg/--background/--surface-0/--black/--white)")

    bg_hex = roles["bg"]["value"]
    notes: list[str] = []

    # integrity pass: text must read on bg and muted must differ from text —
    # cards without explicit text/muted tokens otherwise collapse the palette
    light_bg = _lum(bg_hex) >= 0.4
    tv = (roles.get("text") or {}).get("value")
    if not tv or tv.lower() == bg_hex.lower() or _contrast(tv, bg_hex) < 3.0:
        derived = "#ffffff" if not light_bg else "#000000"
        roles["text"] = {"token": "(derived from bg)", "value": derived}
        notes.append(f"text derived {derived} on bg {bg_hex} — card has no readable text token")
    mv = (roles.get("muted") or {}).get("value")
    text_hex = roles["text"]["value"]
    if not mv or mv.lower() in (text_hex.lower(), bg_hex.lower()):
        base = text_hex
        muted = _darken(base, 0.35) if light_bg else _lighten(base, 0.35)
        roles["muted"] = {"token": "(derived from text)", "value": muted}
        notes.append(f"muted derived {muted} from text {base} — card has no distinct muted token")
    av = ((roles.get("accent") or roles.get("primary")) or {}).get("value")
    if av and av.lower() in (text_hex.lower(), bg_hex.lower()):
        # one honest retry: the most saturated token distinct from bg/text
        cands = [(n, _hex_of(v)) for n, v in {**sc, **sc_dark}.items()
                 if v and _hex_of(v)
                 and _hex_of(v).lower() not in (text_hex.lower(), bg_hex.lower())]
        if cands:
            best = max(cands, key=lambda kv: _hls_sat(kv[1]))
            if "accent" in roles:
                roles["accent"] = {"token": best[0], "value": best[1]}
            if "primary" in roles:
                roles["primary"] = {"token": best[0], "value": best[1]}
            notes.append(f"accent re-picked {best[0]} {best[1]} — first pick matched text/bg")

    # contrast-guard: primary/accent/muted must read on bg
    for role in ("primary", "accent", "muted"):
        if role in roles:
            guarded, n = _guard(roles[role]["value"], bg_hex)
            roles[role]["value"] = guarded
            notes.extend(n)

    # dark theme: if the card has dark tokens, emit them too (guarded on dark bg).
    # Roles are picked from the DARK vocabulary — requiring a light-vocabulary
    # hit to also exist in the dark one silently dropped roles (the one-shot
    # sheet once shipped with dark_roles = {bg} only).
    dark_roles = {}
    if sc_dark:
        dark_bg = None
        for name in ("--bg", "--background", "--black", "--color-bg"):
            v = sc_dark.get(name)
            if v:
                dark_bg = _hex_of(v)
                break
        dark_roles["bg"] = dark_bg or "#000000"
        dark_prefers = {
            "primary": ["--blurple", "--brand", "--primary", "--accent"],
            "accent": ["--spring-green", "--accent", "--green"],
            "text": ["--text", "--foreground", "--white"],
            "muted": ["--text-muted", "--muted", "--greyple"],
        }
        for role, prefers in dark_prefers.items():
            for name in prefers:
                v = sc_dark.get(name)
                if not v:
                    continue
                hx = _hex_of(v)
                if hx:
                    guarded, n = _guard(hx, dark_roles["bg"])
                    dark_roles[role] = {"token": name, "value": guarded}
                    notes.extend(n)
                    break

    # remap table vs current fingerprint
    cur_colors = (current.get("colors") or {}).get("semantic", {}) or {}
    rows = []
    for role, r in roles.items():
        cur = _hex_of(str(cur_colors.get(role, ""))) if cur_colors.get(role) else "—"
        rows.append(f"| `{role}` | {cur} | `{r['token']}` → `{r['value']}` |")
    dark_rows = ""
    if dark_roles:
        dark_rows = "\n".join(
            f"| `{role}` | — | `{r['token'] if isinstance(r, dict) else role}` → `{r['value'] if isinstance(r, dict) else r}` |"
            for role, r in dark_roles.items())

    css_light = "\n".join(
        f"  --{role}: {r['value']};" for role, r in roles.items())
    css_dark = ""
    if dark_roles:
        css_dark = "\n".join(
            f"  --{role}: {r['value'] if isinstance(r, dict) else r};" for role, r in dark_roles.items())

    nl = chr(10)
    dark_md = ("| **dark** | | |" + nl + dark_rows) if dark_rows else ""
    css_dark_block = ("## CSS (dark)" + nl + nl + "```css" + nl + "[data-theme=\"dark\"] {" + nl
                      + css_dark + nl + "}" + nl + "```") if css_dark else ""
    md = f"""# Theme: {slug} (borrowed palette)

Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} from
`library/cards/{slug}/semantic.json`.

## Token remap

| Role | Current (your fingerprint) | Borrowed |
|---|---|---|
{nl.join(rows)}
{dark_md}

## CSS (light)

```css
:root {{
{css_light}
}}
```

{css_dark_block}

## Contrast guard

{nl.join(notes) if notes else "- no adjustments needed (all roles ≥ 4.5:1 on bg)"}

## Wire-in

1. Map `--primary`/`--accent`/`--bg`/`--text`/`--muted` onto your app's tokens
   (shadcn: primary/ring/destructive; Tailwind: theme colors).
2. Keep your existing font/spacing/radius tokens — this is a COLOR theme only.
3. Re-run `scripts/qa.py` on the next iteration — contrast is checked there.
"""

    return {"slug": slug, "roles": roles, "dark_roles": dark_roles,
            "css_light": css_light, "css_dark": css_dark, "notes": notes, "markdown": md}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("card", help="library card slug (e.g. deno, stripe, linear)")
    ap.add_argument("--target", default=None, help="project dir whose fingerprint.json defines 'current'")
    ap.add_argument("--out", default=None, help="output dir for themes/ (default: target or cwd)")
    args = ap.parse_args()

    try:
        result = borrow_theme(args.card, args.target or ".")
    except ValueError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    target = Path(args.target or ".")
    out_dir = Path(args.out or target) / ".hermes" / "design" / "themes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.card}.md"
    out_file.write_text(result["markdown"], encoding="utf-8")
    print(f"theme written → {out_file}")
    roles, dark_roles, notes = result["roles"], result["dark_roles"], result["notes"]
    role_summary = ", ".join(f"{k}={v['value']}" for k, v in roles.items())
    print("  roles: " + role_summary
          + (f" | dark: {', '.join(dark_roles.keys())}" if dark_roles else ""))
    if notes:
        print("  contrast guard applied:")
        for n in notes:
            print(f"    • {n}")


if __name__ == "__main__":
    main()
