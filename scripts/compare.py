# MIRRORED from the design-scope skill (scripts/compare.py / theme.py).
# Canonical home: <skill>/scripts/ — update both copies together.

#!/usr/bin/env python3
"""design-scope compare — reference card fingerprint vs project fingerprint.

Answers "what would this reference actually give us?" — concrete borrow
candidates, not vibes. Output is compact markdown for a recommendation's
evidence block.

Usage:
  python compare.py <reference-fingerprint.json> <project-fingerprint.json>
  python compare.py <reference-fingerprint.json> <project-dir>   # auto-reads .hermes/design/fingerprint.json
  python compare.py --card stripe <project-dir>                  # resolves card from global library index
"""
import argparse
import json
import os
import sys
from pathlib import Path

GLOBAL_LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY",
                                     r"E:\New-Personal-Projects\Ui Design MCP\library"))


def load_fp(path: Path) -> dict:
    if path.is_dir():
        path = path / ".hermes" / "design" / "fingerprint.json"
    return json.loads(path.read_text(encoding="utf-8"))


def norm_colors(fp: dict) -> list[str]:
    """Dominant hex colors, deduped, most-used first. Handles BOTH schemas:
    - raw dembrandt card: colors.palette[] = {normalized, count, ...}
    - normalized project fp: palette.raw[] = hex strings
    """
    colors = fp.get("colors") or {}
    raw = colors.get("palette") or []
    if not raw:
        raw = (fp.get("palette") or {}).get("raw") or []
    scored = []
    for c in raw:
        if isinstance(c, dict):
            v = c.get("normalized") or c.get("value") or c.get("color")
            count = c.get("count") or 0
        else:
            v, count = c, 0
        if isinstance(v, str) and v.startswith("#"):
            scored.append((v[:7].lower(), count))
    seen = set()
    out = []
    for v, _ in sorted(scored, key=lambda x: -x[1]):
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out[:12]


def norm_fonts(fp: dict) -> list[str]:
    """Handles: raw dembrandt typography.styles[].family OR normalized typography.fonts[]"""
    styles = (fp.get("typography") or {}).get("styles") or []
    fonts = sorted({s.get("family") for s in styles if s.get("family")})
    if not fonts:
        fonts = (fp.get("typography") or {}).get("fonts") or []
    return fonts[:8]


def norm_spacing(fp: dict) -> list[str]:
    """Handles: raw dembrandt spacing.commonValues[].px OR normalized spacing.scale[]"""
    common = (fp.get("spacing") or {}).get("commonValues") or []
    seen = set()
    out = []
    for v in sorted(common, key=lambda x: -(x.get("count") or 0)):
        px = v.get("px")
        if px and px not in seen:
            seen.add(px)
            out.append(str(px))
    if not out:
        out = [str(x) for x in ((fp.get("spacing") or {}).get("scale") or [])]
    return out[:12]


def norm_radii(fp: dict) -> list[str]:
    """Handles: raw dembrandt borderRadius.values[].value OR normalized borders.radius[]"""
    radii = (fp.get("borderRadius") or {}).get("values") or []
    seen = set()
    out = []
    for v in sorted(radii, key=lambda x: -(x.get("count") or 0)):
        val = v.get("value")
        if val and val not in seen:
            seen.add(val)
            out.append(str(val))
    if not out:
        out = [str(r) for r in (fp.get("borders") or {}).get("radius", [])]
    return out[:8]


def resolve_card(slug: str) -> Path | None:
    idx = GLOBAL_LIBRARY / "index.json"
    if not idx.exists():
        return None
    data = json.loads(idx.read_text(encoding="utf-8"))
    card = data.get("cards", {}).get(slug)
    if not card:
        return None
    fp = card.get("files", {}).get("fingerprint")
    if not fp:
        return None
    return GLOBAL_LIBRARY / fp


def compare_card(slug: str, project_dir: str) -> dict:
    """Compare a library card's fingerprint against a project's fingerprint.

    Returns a dict of borrow candidates (colors/fonts/spacing/radii gaps).
    Shared with the MCP server (mcp_server.py imports this).
    """
    ref_path = resolve_card(slug)
    if not ref_path:
        raise ValueError(f"card not found in library index: {slug}")
    ref = load_fp(ref_path)
    proj_path = Path(project_dir)
    proj = load_fp(proj_path)

    ref_colors, proj_colors = norm_colors(ref), norm_colors(proj)
    ref_fonts, proj_fonts = norm_fonts(ref), norm_fonts(proj)
    ref_spacing, proj_spacing = norm_spacing(ref), norm_spacing(proj)
    ref_radii, proj_radii = norm_radii(ref), norm_radii(proj)

    missing_colors = [c for c in ref_colors if c not in proj_colors]
    shared = [c for c in ref_colors if c in proj_colors]
    missing_fonts = [f for f in ref_fonts if f not in proj_fonts]
    missing_sp = [s for s in ref_spacing if s not in proj_spacing]

    return {
        "reference": ref.get("slug") or str(ref_path.stem),
        "project": str(proj.get("slug") or proj.get("target", proj_path)),
        "colors_lacking": missing_colors[:8],
        "colors_shared": shared[:6],
        "fonts_lacking": missing_fonts[:6],
        "spacing_ref": ref_spacing[:8],
        "spacing_lacking": missing_sp,
        "radii_ref": ref_radii[:6],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reference", help="card slug (--card) or fingerprint JSON path")
    ap.add_argument("project", help="project fingerprint JSON or project dir")
    ap.add_argument("--card", action="store_true", help="reference is a library card slug")
    args = ap.parse_args()

    if args.card:
        try:
            result = compare_card(args.reference, args.project)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        lines = [f"### Borrow from `{result['reference']}` vs `{result['project']}`", ""]
        if result["colors_lacking"]:
            lines.append(f"- **Colors project lacks ({len(result['colors_lacking'])}):** {', '.join(result['colors_lacking'])}")
        else:
            lines.append("- **Colors:** no gap — project already covers the reference palette")
        if result["colors_shared"]:
            lines.append(f"- **Shared:** {', '.join(result['colors_shared'])}")
        if result["fonts_lacking"]:
            lines.append(f"- **Fonts project lacks:** {', '.join(result['fonts_lacking'])}")
        else:
            lines.append("- **Fonts:** no gap")
        if result["spacing_ref"]:
            lines.append(f"- **Spacing ref scale:** {', '.join(result['spacing_ref'])}"
                         + (f" (project lacks {len(result['spacing_lacking'])})" if result["spacing_lacking"] else " (project covers it)"))
        if result["radii_ref"]:
            lines.append(f"- **Radii ref:** {', '.join(result['radii_ref'])}")
        print("\n".join(lines))
        return

    # legacy path: two explicit fingerprint files
    ref_path = Path(args.reference)
    ref = load_fp(ref_path)
    proj = load_fp(Path(args.project))

    ref_colors, proj_colors = norm_colors(ref), norm_colors(proj)
    ref_fonts, proj_fonts = norm_fonts(ref), norm_fonts(proj)
    ref_spacing, proj_spacing = norm_spacing(ref), norm_spacing(proj)
    ref_radii, proj_radii = norm_radii(ref), norm_radii(proj)

    lines = [f"### Borrow from `{ref.get('slug') or Path(str(ref_path)).stem}` vs `{proj.get('slug') or proj.get('target', args.project)}`", ""]

    missing_colors = [c for c in ref_colors if c not in proj_colors]
    if missing_colors:
        lines.append(f"- **Colors project lacks ({len(missing_colors)}):** {', '.join(missing_colors[:8])}")
    else:
        lines.append("- **Colors:** no gap — project already covers the reference palette")
    shared = [c for c in ref_colors if c in proj_colors]
    if shared:
        lines.append(f"- **Shared:** {', '.join(shared[:6])}")

    missing_fonts = [f for f in ref_fonts if f not in proj_fonts]
    if missing_fonts:
        lines.append(f"- **Fonts project lacks:** {', '.join(missing_fonts[:6])}")
    else:
        lines.append("- **Fonts:** no gap")

    if ref_spacing:
        missing_sp = [s for s in ref_spacing if s not in proj_spacing]
        lines.append(f"- **Spacing ref scale:** {', '.join(ref_spacing[:8])}"
                     + (f" (project lacks {len(missing_sp)})" if missing_sp else " (project covers it)"))
    if ref_radii:
        lines.append(f"- **Radii ref:** {', '.join(ref_radii[:6])}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
