#!/usr/bin/env python3
"""design-scope style index — builds a natural-language-searchable summary
of every captured design.

Scans library/cards/* once and writes:
  library/style-index.json   — per-card style vector + archetypes + tags
  library/style-summary.md   — human-readable landscape (one line per card)

Style vector (computed from semantic.json + fingerprint.json):
  hue_family   neutral/warm/cool/green/purple/red/multicolor (from top colors)
  brightness   dark/mid/light (bg luminance)
  saturation   muted/soft/vibrant (avg saturation)
  corners      sharp/soft/rounded/generous (dominant radius)
  flatness     flat/elevated (shadow ratio)
  type_mood    serif-led/mono-accent/bold-led/neutral-sans
  gradient     yes/no

Aesthetic archetypes (rule sets over the vector — additive; an LLM pass can
extend later):
  funky, editorial, brutalist, minimalist, glassmorphic, dark-minimal,
  warm-minimal, playful, premium, retro

Usage:
  python style_index.py            # rebuild from cards/
  python style_index.py --summary  # rebuild + print the summary table
"""
import argparse
import colorsys
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from _console import utf8_stdout

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
CARDS = LIBRARY / "cards"
OUT_JSON = LIBRARY / "style-index.json"
OUT_MD = LIBRARY / "style-summary.md"

NEUTRAL_MAX_SAT = 0.12


def _hex_to_hsl(value: str):
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", value.strip())
    if not m:
        m = re.fullmatch(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", value.strip())
        if m:
            r, g, b = int(m.group(1)) / 255, int(m.group(2)) / 255, int(m.group(3)) / 255
        else:
            return None
    else:
        h = m.group(1)
        r, g, b = int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return (hh * 360, ss, ll)


def _hue_family(hue: float) -> str:
    if hue < 15 or hue >= 345:
        return "red"
    if hue < 45:
        return "orange"
    if hue < 70:
        return "yellow"
    if hue < 160:
        return "green"
    if hue < 200:
        return "cyan"
    if hue < 260:
        return "blue"
    if hue < 290:
        return "purple"
    if hue < 345:
        return "pink"
    return "red"


def build_vectors() -> dict:
    index = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "version": 2, "cards": {}}
    for card_dir in sorted(CARDS.iterdir()):
        if not card_dir.is_dir():
            continue
        slug = card_dir.name
        sem_path = card_dir / "semantic.json"
        fp_path = card_dir / "fingerprint.json"
        entry = {"slug": slug, "url": "", "palette": [], "why": "", "tags": [],
                 "archetypes": [], "vector": {}, "paths": {}}

        sem = json.loads(sem_path.read_text(encoding="utf-8")) if sem_path.exists() else {}
        fp = json.loads(fp_path.read_text(encoding="utf-8")) if fp_path.exists() else {}

        entry["url"] = sem.get("url") or fp.get("url") or ""
        entry["paths"] = {"semantic": f"cards/{slug}/semantic.json",
                          "fingerprint": f"cards/{slug}/fingerprint.json",
                          "screenshot": f"cards/{slug}/screenshot-desktop.png"}

        # palette: curated semantic colors first, else fingerprint palette
        sc = sem.get("semantic_colors", {}).get("light", {})
        palette: list[tuple[str, str]] = []
        if sc:
            palette = [(k, v) for k, v in sc.items() if isinstance(v, str)][:8]
        if not palette:
            raw = (fp.get("colors") or {}).get("palette") or []
            for c in raw[:8]:
                v = c.get("normalized") if isinstance(c, dict) else c
                if isinstance(v, str) and v.startswith("#"):
                    palette.append((f"c{len(palette)}", v))
        entry["palette"] = [{"name": k, "hex": v} for k, v in palette]

        # why text — annotation.json (LLM what_works) PREFERRED, card.md fallback
        ann = {}
        ann_path = card_dir / "annotation.json"
        if ann_path.exists():
            try:
                ann = json.loads(ann_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                ann = {}
        card_md = card_dir / "card.md"
        if ann.get("what_works"):
            entry["why"] = " ".join(str(w) for w in ann["what_works"])[:400]
        elif card_md.exists():
            text = card_md.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"## Why it's in the library\s*\n+(.*?)(?:\n##|\Z)", text, re.S)
            if m:
                entry["why"] = " ".join(m.group(1).split())[:400]
        entry["annotated"] = bool(ann)
        if ann.get("search_terms"):
            entry["search_terms"] = [str(t)[:60] for t in ann["search_terms"]][:12]
        if ann.get("design_intent"):
            entry["llm_intent"] = {k: str(v)[:80] for k, v in
                                   ann["design_intent"].items() if k != "keywords"}

        # ── vector ────────────────────────────────────────────────────────
        vec: dict = {}

        # hue family + saturation from palette (non-neutral colors)
        families: dict[str, int] = {}
        sats = []
        for _, hx in palette:
            hsl = _hex_to_hsl(hx)
            if not hsl:
                continue
            h, s, _ = hsl
            sats.append(s)
            if s > NEUTRAL_MAX_SAT:
                families[_hue_family(h)] = families.get(_hue_family(h), 0) + 1
        if not families:
            vec["hue_family"] = "neutral"
        else:
            top = sorted(families.items(), key=lambda kv: -kv[1])
            vec["hue_family"] = "multicolor" if len(top) >= 3 else top[0][0]
        avg_sat = sum(sats) / len(sats) if sats else 0
        vec["saturation"] = ("vibrant" if avg_sat > 0.45 else
                             "soft" if avg_sat > 0.18 else "muted")

        # brightness from bg (semantic background / bg token / first color)
        bg_hx = None
        bg_raw = (sem.get("named_tokens", {}).get("light", {}) or {}).get("--bg")
        if not bg_raw:
            bg_raw = (fp.get("colors") or {}).get("semantic", {}).get("background")
        if bg_raw:
            bg_hx = _hex_to_hsl(bg_raw)
        if bg_hx:
            lum = bg_hx[2]
            vec["brightness"] = ("dark" if lum < 0.35 else "mid" if lum < 0.7 else "light")
        else:
            vec["brightness"] = "unknown"

        # corners from dominant radius (fingerprint) or intent
        radii = (fp.get("borderRadius") or {}).get("values") or []
        corner = None
        if radii:
            dom = max(radii, key=lambda r: r.get("count", 0))
            try:
                px = float(re.search(r"[\d.]+", str(dom.get("value", "0"))).group())
                corner = ("sharp" if px <= 2 else
                          "soft" if px <= 8 else
                          "rounded" if px <= 16 else "generous")
            except Exception:
                corner = None
        if not corner:
            di = sem.get("design_intent", {})
            corner = di.get("corner_style")
        vec["corners"] = corner or "unknown"

        # flatness
        di = sem.get("design_intent", {})
        flat = di.get("flat")
        if flat is None:
            shadows = fp.get("shadows") or []
            flat = len(shadows) == 0
        vec["flatness"] = "flat" if flat else "elevated"

        # type mood — normalize legacy vocabulary (semantic.json written before
        # 2026-08-13 used "mono accents"/"neutral sans"; search reads the new forms)
        moods = [{"mono accents": "mono-accent", "neutral sans": "neutral-sans"}.get(m, m)
                 for m in (di.get("type_mood") or [])]
        vec["type_mood"] = moods[0] if moods else "neutral-sans"
        entry["vector"] = vec

        # ── archetypes (rule sets over the vector) ────────────────────────
        a: set[str] = set()
        hf, sat, bri, corn, flatn, mood = (
            vec["hue_family"], vec["saturation"], vec["brightness"],
            vec["corners"], vec["flatness"], vec["type_mood"])
        if sat == "vibrant" and hf in ("multicolor", "pink", "red", "orange", "yellow", "green"):
            a.add("funky")
        if sat == "vibrant" and hf in ("multicolor", "pink", "green") and corn in ("rounded", "generous") and flatn == "flat":
            a.add("playful")
        if mood == "serif-led" and bri == "light" and sat in ("muted", "soft"):
            a.add("editorial")
        if corn == "sharp" and flatn == "flat" and sat in ("muted", "soft"):
            a.add("brutalist")
        if hf == "neutral" and sat in ("muted", "soft") and corn in ("soft", "rounded") and flatn == "flat":
            a.add("minimalist")
        if bri == "dark" and hf == "neutral" and sat in ("muted", "soft"):
            a.add("dark-minimal")
        if hf in ("orange", "yellow", "red", "pink") and bri == "light" and sat in ("muted", "soft"):
            a.add("warm-minimal")
        if mood in ("serif-led", "mono-accent") and bri == "dark" and sat in ("muted", "soft"):
            a.add("premium")
        if hf in ("orange", "yellow", "red", "pink") and sat in ("soft", "vibrant") and mood == "serif-led":
            a.add("retro")
        # glassmorphic: gradients + light + rounded (heuristic)
        gradients = fp.get("gradients") or []
        if gradients and bri == "light" and corn in ("rounded", "generous"):
            a.add("glassmorphic")
        entry["archetypes"] = sorted(a)

        # ── tags: keyword match on why + annotation keywords/search_terms ──
        why = entry["why"].lower()
        for kw in ("minimal", "editorial", "serif", "mono", "dark", "glass", "gradient",
                   "brutalist", "playful", "fun", "premium", "elegant", "retro",
                   "vintage", "tech", "bold", "clean", "warm", "muted", "vibrant",
                   "rounded", "sharp", "flat", "3d", "noise", "grain", "photography",
                   "hero", "dashboard", "landing", "ecommerce", "saas", "fintech"):
            if kw in why:
                entry["tags"].append(kw)
        for v in (di.get("vibe") or []):
            entry["tags"].append(v.lower())
        # annotation keywords (LLM design words) — the search upgrade
        for kw in (ann.get("design_intent", {}).get("keywords") or []):
            entry["tags"].append(str(kw).lower()[:40])
        for t in (ann.get("search_terms") or []):
            entry["tags"].append(str(t).lower()[:40])
        entry["tags"] = sorted(set(entry["tags"]))

        index["cards"][slug] = entry
    return index


def write_summary(index: dict) -> None:
    lines = ["# design-scope style summary", "",
             f"Generated {index['generated']} · {len(index['cards'])} cards · "
             "search via `python library/style_search.py \"<query>\"`", ""]
    lines.append("| slug | archetypes | hue | brightness | sat | corners | flat | type |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for slug, c in sorted(index["cards"].items()):
        v = c["vector"]
        lines.append(f"| {slug} | {', '.join(c['archetypes']) or '—'} | {v['hue_family']} | "
                     f"{v['brightness']} | {v['saturation']} | {v['corners']} | "
                     f"{v['flatness']} | {v['type_mood']} |")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", action="store_true", help="print the summary table")
    args = ap.parse_args()
    index = build_vectors()
    OUT_JSON.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(index)
    print(f"style-index.json: {len(index['cards'])} cards → {OUT_JSON}")
    if args.summary:
        print(OUT_MD.read_text(encoding="utf-8")[:4000])


if __name__ == "__main__":
    main()
