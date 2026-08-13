#!/usr/bin/env python3
"""design-scope one-shot — the pipeline that makes "one-shotted" truthful.

prepare: decisions by the server. Runs the real tools in sequence and writes
the receipt (register.json) + borrowed tokens + band contract:

    style_search(direction)      → ranked cards, dark-palette preference
    card_get(slug)               → evidence (why it works)
    theme_borrow(slug)           → roles + contrast-guard log (theme.py)
    get_page_structure(brief)    → band contract (page_structure.py)

grade:   grading by the server. verdict.py against the rendered page → ledger
row, then rebuilds the sheet with the register + verdict embedded.

Rendering (copy, SVG, motion) stays the agent's job — the page says so.

Usage:
  python scripts/one_shot.py prepare --brief "blueprint sheet for design-scope" \
      [--direction "measured technical blueprint"] [--out showcase/one-shot] [--fresh]
  python scripts/one_shot.py grade --label "R1 one-shot" [--out showcase/one-shot]

RUN WITH THE LIBRARY ENV'S PYTHON (same venv as capture.py / verdict.py).
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "library"))
sys.path.insert(0, str(ROOT / "scripts"))

LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()

# roles theme.py emits
ROLE_NAMES = ("primary", "accent", "bg", "text", "muted")
# local semantic roles — deliberately NOT borrowed (status colors carry
# meaning, not palette); documented on the sheet
STATUS_LIGHT = {"--pass": "rgb(14, 122, 61)", "--under": "rgb(179, 64, 31)"}
STATUS_DARK = {"--pass": "rgb(63, 206, 129)", "--under": "rgb(255, 138, 92)"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ranked(results, cards_dir: Path) -> list[tuple[str, str]]:
    """Ranked candidates, dark-palette cards first (in rank order).

    Returns [(slug, why)] — the pick rule is: first candidate whose borrowed
    palette passes the usability gate; rejects are recorded in the register.
    """
    dark, rest = [], []
    for _sc, slug, _c in results:
        try:
            sem = json.loads((cards_dir / slug / "semantic.json").read_text(encoding="utf-8"))
            nt = sem.get("named_tokens") or {}
            if "dark" in nt and nt["dark"]:
                dark.append((slug, "dark-palette preference"))
                continue
        except Exception:
            pass
        rest.append((slug, "ranked"))
    return dark + rest


def _palette_usable(borrowed: dict) -> tuple[bool, str]:
    """Deterministic usability gate on a borrow.

    text must read on bg (≥ 3.0:1) and the accent must separate (≥ 2.5:1).
    theme.py's guard walks 12 steps and may give up short — this gate refuses
    palettes the guard could not save, and the refusal is recorded.
    """
    roles = borrowed.get("roles") or {}
    bg = (roles.get("bg") or {}).get("value")
    text = (roles.get("text") or {}).get("value")
    accent = ((roles.get("primary") or roles.get("accent")) or {}).get("value")
    if not (bg and text and accent):
        return False, "borrow missing bg/text/accent roles"
    t = _contrast(text, bg)
    if t < 3.0:
        return False, f"text {t:.2f}:1 on bg — below 3.0 floor"
    a = _contrast(accent, bg)
    if a < 2.5:
        return False, f"accent {a:.2f}:1 on bg — below 2.5 floor"
    return True, f"text {t:.2f}:1 · accent {a:.2f}:1 on bg"


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def _contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def _walk(hex_color: str, toward: str, target_ratio: float, bg: str) -> tuple[str, str]:
    """Walk a color toward black/white until it contrasts ≥ target on bg.
    Returns (final_hex, log_line). Deterministic; bounded at 30 steps."""
    cur = hex_color
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    toward_white = toward.lower() == "white"
    ratio = _contrast(cur, bg)
    steps = 0
    while ratio < target_ratio and steps < 30:
        if toward_white:
            r = min(255, r + 18); g = min(255, g + 18); b = min(255, b + 18)
        else:
            r = max(0, r - 18); g = max(0, g - 18); b = max(0, b - 18)
        cur = f"#{r:02x}{g:02x}{b:02x}"
        ratio = _contrast(cur, bg)
        steps += 1
    log = (f"derivation: {hex_color} → {cur} to reach {ratio:.2f}:1 on {bg} "
           f"({'lighten' if toward_white else 'darken'} walk)")
    return cur, log


def _on_accent(accent_hex: str) -> str:
    """Black or white, whichever contrasts more against the accent."""
    w, k = "#ffffff", "#000000"
    return w if _contrast(w, accent_hex) >= _contrast(k, accent_hex) else k


def derive_tokens(roles: dict, dark_roles: dict, notes: list) -> tuple[dict, dict, list]:
    """Map theme.py's borrowed roles onto the sheet's token vocabulary.

    Every emitted value is a borrowed role value or a single-token alpha
    blend (rgba of one ink) — interpolation of one token with transparency
    is not a third colour. Derivation steps are logged into `notes`.
    """
    def val(role, fallback=None):
        r = roles.get(role) or {}
        return r.get("value") or fallback

    light = {}
    derivations = []
    bg = val("bg", "#f4f3ee")
    ink = val("text", "#16181d")
    muted = val("muted", "#5b606b")
    primary = val("primary", "#1e5eff")
    accent = val("accent", primary)

    light["--paper"] = bg
    light["--card"] = "rgba(%s, 0.03)" % _rgb_triplet(ink)
    light["--paper-2"] = "rgba(%s, 0.05)" % _rgb_triplet(ink)
    light["--ink"] = ink
    light["--muted"] = muted
    light["--line"] = "rgba(%s, 0.14)" % _rgb_triplet(ink)
    light["--track"] = "rgba(%s, 0.07)" % _rgb_triplet(ink)
    light["--grid"] = "rgba(%s, 0.05)" % _rgb_triplet(ink)
    light["--accent"] = accent
    at, log = _walk(accent, "black" if _luminance(bg) > 0.5 else "white", 4.5, bg)
    light["--accent-text"] = at
    derivations.append(log)
    light["--accent-soft"] = "rgba(%s, 0.09)" % _rgb_triplet(accent)
    light["--accent-line"] = "rgba(%s, 0.35)" % _rgb_triplet(accent)
    light["--on-accent"] = _on_accent(accent)
    light["--sel"] = "rgba(%s, 0.07)" % _rgb_triplet(accent)
    light["--shadow"] = "rgba(%s, 0.08)" % _rgb_triplet(ink)
    light.update(STATUS_LIGHT)

    dark = {}
    d = dark_roles or {}

    def dv(role):
        v = d.get(role)
        return v.get("value") if isinstance(v, dict) else v

    dbg = dv("bg")
    if dbg is None:
        dbg, log = _walk(bg, "black", 9.0, "#ffffff")  # dark paper: walk bg dark until near-black
        derivations.append(log)
    dark["--paper"] = dbg
    dink = dv("text")
    if dink is None:
        dink, log = _walk(dbg, "white", 10.0, dbg)
        derivations.append(log)
    dark["--ink"] = dink
    dark["--card"] = "rgba(%s, 0.06)" % _rgb_triplet(dink)
    dark["--paper-2"] = "rgba(%s, 0.08)" % _rgb_triplet(dink)
    dmuted = dv("muted")
    if dmuted is None:
        dmuted, log = _walk(dink, "black", 4.5, dbg)
        derivations.append(log)
    dark["--muted"] = dmuted
    dark["--line"] = "rgba(%s, 0.16)" % _rgb_triplet(dink)
    dark["--track"] = "rgba(%s, 0.08)" % _rgb_triplet(dink)
    dark["--grid"] = "rgba(%s, 0.045)" % _rgb_triplet(dink)
    daccent = dv("primary") or dv("accent")
    if daccent is None:
        daccent, log = _walk(accent, "white", 4.5, dbg)
        derivations.append(log)
    dark["--accent"] = daccent
    dat, log = _walk(daccent, "white" if _luminance(dbg) < 0.5 else "black", 4.5, dbg)
    dark["--accent-text"] = dat
    derivations.append(log)
    dark["--accent-soft"] = "rgba(%s, 0.12)" % _rgb_triplet(daccent)
    dark["--accent-line"] = "rgba(%s, 0.4)" % _rgb_triplet(daccent)
    dark["--on-accent"] = _on_accent(daccent)
    dark["--sel"] = "rgba(%s, 0.1)" % _rgb_triplet(daccent)
    dark["--shadow"] = "rgba(%s, 0.25)" % _rgb_triplet(dink)
    dark.update(STATUS_DARK)

    notes.append("local status roles (--pass/--under) kept from design-scope "
                 "semantics — status colors carry meaning, not palette")
    return light, dark, derivations


def _rgb_triplet(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"


def prepare(brief: str, direction: str, out: Path, fresh: bool = False) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    register = {"brief": brief, "direction": direction, "created": _now(),
                "credits": "0 — local-first", "entries": []}

    # 1. style_search → ranked candidates (dark palettes first)
    from style_search import search  # library/
    index = json.loads((LIBRARY / "style-index.json").read_text(encoding="utf-8"))
    query = direction or "measured technical"
    results = search(index, query, 8)
    if not results:
        raise ValueError(f"style_search('{query}') returned nothing")
    cards_dir = LIBRARY / "cards"
    ranked = _ranked(results, cards_dir)
    register["entries"].append({
        "stage": "direction", "tool": "style_search",
        "input": query,
        "output": {"candidates": [s for s, _w in ranked],
                   "ordering": "dark-palette cards first, then rank"},
        "ts": _now(),
    })

    # 2. theme_borrow, gated — first usable borrow wins; rejects recorded
    import theme as th  # scripts/
    slug, borrowed, rejects = None, None, []
    for cand, why in ranked:
        try:
            b = th.borrow_theme(cand, str(out))
        except ValueError as e:
            rejects.append({"slug": cand, "reason": str(e)})
            continue
        ok, reason = _palette_usable(b)
        if ok:
            slug, borrowed = cand, b
            break
        rejects.append({"slug": cand, "reason": reason})
    if slug is None:
        raise ValueError("no borrow passed the usability gate in the top 8 — "
                         f"rejects: {[r['slug'] for r in rejects]}")
    notes = list(borrowed.get("notes") or [])
    register["entries"].append({
        "stage": "palette", "tool": "theme_borrow",
        "input": slug,
        "output": {
            "roles": {k: v["value"] for k, v in (borrowed.get("roles") or {}).items()},
            "dark_roles": {k: v["value"] if isinstance(v, dict) else v
                           for k, v in (borrowed.get("dark_roles") or {}).items()},
            "contrast_guard": notes,
        },
        "gate": {"usable": True, "reason": reason, "rejects": rejects},
        "ts": _now(),
    })

    # 3. card_get (evidence on the final pick)
    card_dir = cards_dir / slug
    card_md = (card_dir / "card.md").read_text(encoding="utf-8", errors="replace")
    why = next((ln.strip() for ln in card_md.splitlines() if ln.strip() and not ln.startswith("#")), "")[:400]
    sem = json.loads((card_dir / "semantic.json").read_text(encoding="utf-8"))
    register["entries"].append({
        "stage": "evidence", "tool": "card_get",
        "input": slug, "output": {"why": why, "captured": sem.get("captured")},
        "artifacts": [str(card_dir / "screenshot-desktop.png")], "ts": _now(),
    })

    # 4. get_page_structure (band contract)
    import page_structure as ps
    structure = ps.plan(brief, direction)
    register["entries"].append({
        "stage": "structure", "tool": "get_page_structure",
        "input": {"brief": brief, "direction": direction},
        "output": {"bands": structure["declared_bands"],
                   "mechanism_budget": structure["mechanism_budget"],
                   "types": [b["type"] for b in structure["bands"]]},
        "ts": _now(),
    })

    # 5. derive the token vocabulary (documented, deterministic)
    light, dark, derivations = derive_tokens(borrowed.get("roles") or {},
                                             borrowed.get("dark_roles") or {}, notes)
    register["entries"].append({
        "stage": "tokens", "tool": "derive_tokens (deterministic)",
        "input": "borrowed roles", "output": {"light": len(light), "dark": len(dark)},
        "ts": _now(),
    })
    register["derivations"] = derivations
    register["card"] = {"slug": slug, "why": why,
                        "screenshot": str(card_dir / "screenshot-desktop.png")}

    (out / "register.json").write_text(json.dumps(register, indent=2, ensure_ascii=False), encoding="utf-8")
    (out / "tokens.json").write_text(json.dumps(
        {"light": light, "dark": dark}, indent=2), encoding="utf-8")
    (out / "bands.json").write_text(json.dumps(structure, indent=2, ensure_ascii=False), encoding="utf-8")
    return register


def grade(label: str, out: Path) -> dict:
    html = out / "index.html"
    if not html.exists():
        raise FileNotFoundError(f"{html} not found — compose the page first, then grade")
    import verdict as vd  # scripts/
    verdict = vd.run_verdict(html, "strict")
    verdict["label"] = label
    (out / "verdict.json").write_text(json.dumps(verdict, indent=2, ensure_ascii=False), encoding="utf-8")
    vd.ledger_append(out / "verdicts.json", {
        "label": label, "date": verdict["date"], "file": str(html),
        "score": verdict["summary"]["score"], "pass": verdict["summary"]["pass"],
        "under": verdict["summary"]["under"],
        "rows": [{"group": c["group"], "name": c["name"], "status": c["status"]}
                 for c in verdict["checks"]],
    })
    import build_showcase as bs
    bs.build_variant("one-shot")
    return verdict


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prepare", help="run the tools, write the receipt")
    p.add_argument("--brief", required=True, help="what the page is for")
    p.add_argument("--direction", default="measured technical blueprint",
                   help="style direction words for style_search")
    p.add_argument("--out", default=str(ROOT / "showcase" / "one-shot"))
    p.add_argument("--fresh", action="store_true", help="capture a new card instead of reusing")

    g = sub.add_parser("grade", help="verdict + ledger + rebuild")
    g.add_argument("--label", default="R1 one-shot")
    g.add_argument("--out", default=str(ROOT / "showcase" / "one-shot"))

    args = ap.parse_args()
    out = Path(args.out)
    if args.cmd == "prepare":
        register = prepare(args.brief, args.direction, out, args.fresh)
        gate = register["entries"][1].get("gate", {})
        rejects = ", ".join(f"{r['slug']} ({r['reason']})" for r in gate.get("rejects", [])) or "none"
        print(f"one-shot prepared → {out}")
        print(f"  card:   {register['card']['slug']} — gate: {gate.get('reason', 'n/a')}")
        if rejects:
            print(f"  rejects: {rejects}")
        print(f"  palette: {register['entries'][1]['output']['roles']}")
        print(f"  bands:  {register['entries'][3]['output']['bands']} · "
              f"mechanism budget {register['entries'][3]['output']['mechanism_budget']}")
        print("  register.json + tokens.json + bands.json written — compose the page, then grade")
    elif args.cmd == "grade":
        verdict = grade(args.label, out)
        print(f"one-shot graded: {verdict['summary']['score']} ({args.label})")
        for c in verdict["checks"]:
            print(f"  {c['status']:<5} {c['group']:<8} {c['name']}: {c['detail']}")


if __name__ == "__main__":
    main()
