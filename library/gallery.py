#!/usr/bin/env python3
"""design-scope gallery builder — renders an HTML gallery of captured cards.

Reads library/index.json and writes library/gallery.html (self-contained,
dark themed, thumbnails via file:// relative paths).
"""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()
INDEX = LIBRARY / "index.json"
OUT = LIBRARY / "gallery.html"

CATEGORY_COLORS = {
    "fintech": "#3b82f6", "devtools": "#22d3ee", "design-tools": "#a78bfa",
    "ai": "#f472b6", "consumer": "#34d399", "media": "#fbbf24",
    "ecommerce": "#f87171", "saas": "#60a5fa", "education": "#4ade80",
    "wellness": "#2dd4bf", "travel": "#38bdf8", "crypto": "#facc15",
    "gaming": "#c084fc", "healthcare": "#fb7185", "productivity": "#a3e635",
}

def esc(s):
    return re.sub(r"[&<>\"']", lambda m: {
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[m.group(0)], str(s))

def build():
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    cards = idx.get("cards", {})
    stats = idx.get("stats", {})
    items = sorted(cards.values(), key=lambda c: c.get("captured_at", ""), reverse=True)

    rows = []
    for c in items:
        cat = c.get("category") or "other"
        color = CATEGORY_COLORS.get(cat, "#94a3b8")
        desk = c.get("files", {}).get("desktop")
        thumb = f"cards/{c['slug']}/screenshot-desktop.png" if desk else ""
        fonts = ", ".join(c.get("fingerprint_summary", {}).get("fonts", [])[:2]) or "—"
        ncol = c.get("fingerprint_summary", {}).get("colors", 0)
        ncomp = c.get("fingerprint_summary", {}).get("components", 0)
        rows.append(f"""
<div class="card" style="--c:{color}">
  <a href="{esc(thumb)}" target="_blank"><img loading="lazy" src="{esc(thumb)}" alt="{esc(c['name'])} screenshot"></a>
  <div class="body">
    <div class="head"><span class="name">{esc(c['name'])}</span><span class="cat">{esc(cat)}</span></div>
    <div class="why">{esc(c.get('why') or '')}</div>
    <div class="meta">{ncol} colors · {ncomp} comps · fonts: {esc(fonts)}</div>
    <a class="url" href="{esc(c['url'])}" target="_blank">{esc(c['url'])}</a>
  </div>
</div>""")

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>design-scope library — {len(items)} cards</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background:#0d1117; color:#e6edf3; font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; padding:32px; }}
  h1 {{ font-size:22px; margin-bottom:4px; }}
  .sub {{ color:#8b949e; margin-bottom:24px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:20px; }}
  .card {{ background:#161b22; border:1px solid #30363d; border-radius:10px; overflow:hidden; display:flex; flex-direction:column; }}
  .card img {{ width:100%; height:200px; object-fit:cover; object-position:top; border-bottom:1px solid #30363d; display:block; }}
  .card .body {{ padding:14px; display:flex; flex-direction:column; gap:8px; flex:1; }}
  .card .head {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
  .card .name {{ font-weight:600; font-size:15px; }}
  .card .cat {{ font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--c); border:1px solid var(--c); border-radius:999px; padding:1px 8px; }}
  .card .why {{ color:#9da7b3; font-size:13px; }}
  .card .meta {{ color:#6e7681; font-size:12px; }}
  .card .url {{ color:#58a6ff; font-size:12px; text-decoration:none; word-break:break-all; }}
</style></head><body>
<h1>design-scope design library</h1>
<div class="sub">{len(items)} reference cards · last run {esc(stats.get('last_run',''))}</div>
<div class="grid">{''.join(rows)}</div>
</body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"gallery written: {OUT} ({len(items)} cards)")

if __name__ == "__main__":
    build()
