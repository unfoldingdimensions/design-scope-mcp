#!/usr/bin/env python3
"""design-scope MCP server — exposes the 201-card design library as MCP tools.

stdio:   python library/mcp_server.py
HTTP:    uvicorn mcp_server:app --host 127.0.0.1 --port 8232  (from library/)

Never edits project source. Errors are returned as structured JSON
{"error": msg, "hint": fix} — MCP has no error types.
"""
import json
import os
import queue
import re
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright

LIB = Path(__file__).resolve().parent
if str(LIB) not in sys.path:  # once, at import — NOT per tool call
    sys.path.insert(0, str(LIB))
GLOBAL_LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
INDEX = GLOBAL_LIBRARY / "index.json"
STYLE_INDEX = GLOBAL_LIBRARY / "style-index.json"
# skill scripts (compare.py, theme.py) — resolution order:
# 1. DESIGN_SCOPE_SKILL_SCRIPTS env var (explicit override)
# 2. standard Hermes install locations (~/.hermes, $HERMES_HOME, %LOCALAPPDATA%/hermes)
# 3. vendored copies shipped with this repo (scripts/ — mirrors of the skill's)
# card_compare/theme_borrow return a structured error when none is found.
def _resolve_skill_scripts() -> Path:
    env = os.environ.get("DESIGN_SCOPE_SKILL_SCRIPTS")
    if env:
        return Path(env)
    candidates = [
        Path.home() / ".hermes" / "skills" / "creative" / "design-scope" / "scripts",
        Path(os.environ["HERMES_HOME"]) / "skills" / "creative" / "design-scope" / "scripts"
        if os.environ.get("HERMES_HOME") else None,
        Path(os.environ["LOCALAPPDATA"]) / "hermes" / "skills" / "creative" / "design-scope" / "scripts"
        if os.environ.get("LOCALAPPDATA") else None,
        Path(__file__).resolve().parent.parent / "scripts",
    ]
    for c in candidates:
        if c is not None and c.is_dir():
            return c
    return candidates[0]


SKILL_SCRIPTS = _resolve_skill_scripts()

mcp = FastMCP("design-scope")

# single-worker capture queue
_job_queue: queue.Queue = queue.Queue()
_jobs: dict[str, dict] = {}


def _validate() -> list[str]:
    problems = []
    if not INDEX.exists():
        problems.append(f"library index missing: {INDEX} — run capture to build it")
    if not STYLE_INDEX.exists():
        problems.append(f"style index missing: {STYLE_INDEX} — run: python library/style_index.py")
    return problems


def _err(msg: str, hint: str = "") -> str:
    return json.dumps({"error": msg, "hint": hint})


@mcp.tool()
def ping() -> str:
    """Health check — returns library stats or startup problems."""
    problems = _validate()
    if problems:
        return json.dumps({"ok": False, "problems": problems})
    cards = json.loads(INDEX.read_text(encoding="utf-8"))["cards"]
    return json.dumps({"ok": True, "cards": len(cards)})


@mcp.tool()
def style_search(query: str, top_n: int = 8) -> str:
    """Natural-language style search over the library (e.g. 'funky',
    'editorial but not brutalist', 'dark minimal serif')."""
    if not query or len(query) > 200:
        return _err("query must be 1-200 chars")
    top_n = max(1, min(50, top_n))
    if not STYLE_INDEX.exists():
        return _err("style index missing", "run: python library/style_index.py")
    import style_search as ss
    index = json.loads(STYLE_INDEX.read_text(encoding="utf-8"))
    if not ss.parse_query(query)[0]:
        return _err("no meaningful query terms", "try: funky / editorial / dark minimal serif")
    results = []
    for sc, slug, c in ss.search(index, query, top_n):
        results.append({"slug": slug, "score": sc, "archetypes": c["archetypes"],
                        "vector": c["vector"], "palette": c["palette"][:4],
                        "why": c["why"][:200],
                        "screenshot": str(GLOBAL_LIBRARY / c["paths"]["screenshot"])})
    return json.dumps({"query": query, "count": len(results), "results": results},
                      ensure_ascii=False)


@mcp.tool()
def style_filter(hue_family: str = "", brightness: str = "", saturation: str = "",
                 corners: str = "", flatness: str = "", type_mood: str = "",
                 archetype: str = "", max_results: int = 20) -> str:
    """Structured filter over style-index.json vectors (all args optional)."""
    if not STYLE_INDEX.exists():
        return _err("style index missing", "run: python library/style_index.py")
    index = json.loads(STYLE_INDEX.read_text(encoding="utf-8"))
    want = {k: v for k, v in {"hue_family": hue_family, "brightness": brightness,
                              "saturation": saturation, "corners": corners,
                              "flatness": flatness, "type_mood": type_mood}.items() if v}
    out = []
    for slug, c in index["cards"].items():
        v = c["vector"]
        if all(v.get(k) == val for k, val in want.items()) and \
           (not archetype or archetype in c["archetypes"]):
            out.append({"slug": slug, "vector": v, "archetypes": c["archetypes"]})
    return json.dumps({"count": len(out), "results": out[:max_results]}, ensure_ascii=False)


@mcp.tool()
def card_get(slug: str) -> str:
    """Full card: fingerprint + semantic + behaviors + absolute asset paths."""
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        return _err("slug must match ^[a-z0-9-]+$")
    card = GLOBAL_LIBRARY / "cards" / slug
    if not (card / "card.md").exists():
        return _err(f"card '{slug}' not found", "see style_search for valid slugs")

    def _read(name):
        p = card / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    return json.dumps({
        "slug": slug,
        "card_md": (card / "card.md").read_text(encoding="utf-8", errors="replace")[:2000],
        "fingerprint": _read("fingerprint.json"),
        "semantic": _read("semantic.json"),
        "annotation": _read("annotation.json"),
        "behaviors": _read("motion/behaviors.json"),
        "screenshot_desktop": str(card / "screenshot-desktop.png"),
        "screenshot_mobile": str(card / "screenshot-mobile.png"),
        "motion_video": str(card / "motion/card-motion.webm"),
    }, ensure_ascii=False, default=str)


@mcp.tool()
def card_compare(slug: str, project_dir: str) -> str:
    """Concrete borrow candidates: card fingerprint vs project fingerprint."""
    if not Path(project_dir).is_dir():
        return _err(f"project dir not found: {project_dir}")
    if not SKILL_SCRIPTS.is_dir():
        return _err("skill scripts not found",
                    "set DESIGN_SCOPE_SKILL_SCRIPTS; repo scripts/ (compare.py, theme.py) is missing")
    if str(SKILL_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SKILL_SCRIPTS))
    import compare as cmp
    try:
        return json.dumps(cmp.compare_card(slug, project_dir), ensure_ascii=False, default=str)
    except Exception as e:  # noqa: BLE001
        return _err(f"compare failed: {e}")


@mcp.tool()
def theme_borrow(slug: str, target_dir: str = ".") -> str:
    """Borrow a card's palette: token remap + contrast-guarded CSS."""
    if not Path(target_dir).is_dir():
        return _err(f"target dir not found: {target_dir}")
    if not SKILL_SCRIPTS.is_dir():
        return _err("skill scripts not found",
                    "set DESIGN_SCOPE_SKILL_SCRIPTS; repo scripts/ (compare.py, theme.py) is missing")
    if str(SKILL_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SKILL_SCRIPTS))
    import theme as th
    try:
        return json.dumps(th.borrow_theme(slug, target_dir), ensure_ascii=False, default=str)
    except Exception as e:  # noqa: BLE001
        return _err(f"theme borrow failed: {e}")


# ── capture job queue (single worker; capture() never blocks) ──────────────

_TERMINAL = ("done", "failed")


def _prune_jobs(max_keep: int = 100) -> None:
    """Bounded job registry: finished jobs are kept for polling, then dropped
    (insertion order = queue order, so trimming the front keeps the newest).

    Only TERMINAL jobs are evictable. Pruning by position alone could delete a
    still-queued job; the worker then does _jobs[job_id] outside its try block,
    raising KeyError, exiting `while True`, and killing the daemon thread — so
    capture would silently stop working for the life of the process.
    """
    if len(_jobs) <= max_keep:
        return
    evictable = [jid for jid, j in _jobs.items() if j.get("status") in _TERMINAL]
    for jid in evictable[: max(0, len(_jobs) - max_keep)]:
        del _jobs[jid]


def _capture_worker():
    while True:
        job_id, kwargs = _job_queue.get()
        job = _jobs.get(job_id)
        if job is None:  # evicted while queued — never index blindly here
            _job_queue.task_done()
            continue
        job["status"] = "running"
        try:
            from capture import (capture_one, card_exists, load_index,
                                 save_index, slugify, build_index_entry)
            slug = slugify(kwargs["name"]) if not kwargs.get("slug") else kwargs["slug"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                raise ValueError("slug must match ^[a-z0-9]+(-[a-z0-9]+)*$")
            index = load_index()
            # same completion rule as the CLI (capture.card_exists): a bare
            # card dir from a failed attempt must not block the retry
            if slug in index["cards"] or card_exists(slug):
                job.update({"status": "failed",
                            "error": f"slug '{slug}' already exists in the library",
                            "hint": "pass a different slug or run capture.py --redo"})
                continue
            card_dir = GLOBAL_LIBRARY / "cards" / slug
            site = {"url": kwargs["url"], "name": kwargs["name"],
                    "category": kwargs.get("category", "misc"),
                    "why": kwargs.get("why", "")}
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                result = capture_one(site, slug, card_dir, browser,
                                     opts={"fast": kwargs.get("fast", True)})
                browser.close()
            if not result.get("ok"):
                raise RuntimeError(result.get("error") or "capture failed")
            index = load_index()
            index["cards"][slug] = build_index_entry(site, slug, result)
            index.setdefault("stats", {})["last_run"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            index.setdefault("stats", {})["total"] = len(index["cards"])
            save_index(index)
            _rebuild_style_index(card_dir)
            job.update({"status": "done", "slug": slug,
                        "captured_at": result.get("captured_at"),
                        "screenshots": list(result.get("screenshots", {}).keys())})
        except Exception as e:  # noqa: BLE001
            job.update({"status": "failed", "error": str(e)[:500]})
        finally:
            _job_queue.task_done()
            _prune_jobs()


def _rebuild_style_index(card_dir: Path) -> None:
    """New cards must be searchable immediately. Guarded: only rebuild when the
    capture actually wrote card files (the queue mock writes nothing, so tests
    never dirty the tracked style-index)."""
    if not (card_dir / "card.md").exists() and not (card_dir / "fingerprint.json").exists():
        return
    try:
        from style_index import build_vectors, write_summary
        si = build_vectors()
        (GLOBAL_LIBRARY / "style-index.json").write_text(
            json.dumps(si, indent=2, ensure_ascii=False), encoding="utf-8")
        write_summary(si)
    except Exception:  # noqa: BLE001
        pass  # capture must not fail because the index rebuild failed


threading.Thread(target=_capture_worker, daemon=True).start()


@mcp.tool()
def capture(url: str, name: str, category: str = "misc", slug: str = "",
            fast: bool = True, why: str = "") -> str:
    """Enqueue a capture of a website as a library card. Returns a job_id —
    poll capture_status(). fast=True skips motion+behavior (~60s); fast=False
    is the full pass (~4min). why = design rationale shown on the card.
    Never blocks."""
    if not url.startswith(("http://", "https://")):
        return _err("url must start with http(s)://")
    if not name or len(name) > 80:
        return _err("name must be 1-80 chars")
    if len(why) > 300:
        return _err("why must be ≤ 300 chars")
    if slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        return _err("slug must match ^[a-z0-9]+(-[a-z0-9]+)*$")
    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {"status": "queued", "url": url, "name": name}
    _job_queue.put((job_id, {"url": url, "name": name, "category": category,
                             "slug": slug, "fast": fast, "why": why}))
    return json.dumps({"job_id": job_id, "status": "queued"})


@mcp.tool()
def capture_status(job_id: str) -> str:
    """Poll a capture job (queued / running / done / failed)."""
    job = _jobs.get(job_id)
    if not job:
        return _err(f"no job '{job_id}'", "start one with capture()")
    return json.dumps(job, ensure_ascii=False, default=str)


@mcp.tool()
def recommend_history(project_dir: str) -> str:
    """The design-scope iteration chain for a project (manifest.json)."""
    p = Path(project_dir) / ".hermes" / "design" / "manifest.json"
    if not p.exists():
        return _err(f"no manifest at {p}", "run design-scope start on the project first")
    m = json.loads(p.read_text(encoding="utf-8"))
    return json.dumps({
        "name": m.get("name"), "current_iteration": m.get("current_iteration"),
        "adopted_recs": m.get("adopted_recs"), "pending_recs": m.get("pending_recs"),
        "iterations": m.get("iterations"),
    }, ensure_ascii=False)


# Validate at import, not under __main__: `uvicorn mcp_server:app` never runs
# the __main__ block, so the HTTP server used to start happily with a missing
# index and fail per-request instead of loudly at boot.
_problems = _validate()
if _problems:
    raise SystemExit("design-scope MCP: " + "; ".join(_problems))

app = mcp.streamable_http_app()  # uvicorn mcp_server:app

if __name__ == "__main__":
    mcp.run()  # stdio
