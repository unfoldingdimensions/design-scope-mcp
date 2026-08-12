"""
design-scope capture script — batch capture of design reference cards.

For each site in a seed JSON:
  1. Full-page screenshot (desktop 1440x900 + mobile 390x844)
  2. Dembrandt design-token extraction (colors, type, spacing, motion, components)
  3. Assemble reference card in library/cards/<slug>/:
       card.md, fingerprint.json, screenshot-desktop.png, screenshot-mobile.png, source.md

Usage:
  python capture.py <seed.json> [--limit N] [--only slug1,slug2] [--skip slug3]
  python capture.py --url https://example.com [--name X] [--category Y] [--slug z]
  python capture.py seed-batch-1.json --limit 5

Single-URL mode (--url) captures one site without a seed file; the card lands
in the global library and index.json is updated. --why sets the rationale
(agent fills via vision annotation if omitted).

Exit code 0 if all requested captures produced a complete card.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from _console import utf8_stdout

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(ROOT / "library"))).resolve()
CARDS = LIBRARY / "cards"
INDEX = LIBRARY / "index.json"

DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 390, "height": 844}
NAV_TIMEOUT_MS = 45000
SCREENSHOT_WAIT_S = 3.0  # let fonts/animations settle
# shared UA literals — single source of truth (behavior_pass/semantic_pass import)
CHROME_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
IPHONE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
             "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "site"


def load_seed(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("sites", data if isinstance(data, list) else [])


def card_exists(slug: str) -> bool:
    """True only when the card was actually written.

    capture_one() creates card_dir (via card_dir/"tmp") before it can fail, so
    a bare directory means the LAST ATTEMPT FAILED. Treating directory presence
    as "already captured" turned every failure into a permanent skip that then
    reported ok=True. card.md is written last, so it is the completion marker.
    Shared with the MCP capture worker so both paths dedupe identically.
    """
    return (CARDS / slug / "card.md").exists()


def load_index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"version": 1, "cards": {}}


def save_index(index: dict):
    INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_url(url: str) -> str:
    return url if url.startswith("http") else f"https://{url}"


def full_page_screenshot(page, out_path: Path, wait_s: float = SCREENSHOT_WAIT_S):
    page.wait_for_timeout(wait_s * 1000)
    page.screenshot(path=str(out_path), full_page=True)
    if out_path.exists() and out_path.stat().st_size > 5000:
        return True
    # Too small to be a real page. Remove it — leaving the file behind recorded
    # files.desktop = null in index.json while screenshot-desktop.png existed on
    # disk, and regenerate_media keys off that filename, so the card was stuck
    # with a broken thumbnail that no rebuild would ever replace.
    out_path.unlink(missing_ok=True)
    return False


def dembrandt_tokens(url: str, slug: str, workdir: Path, timeout_s: int = 240) -> Path | None:
    """Run dembrandt CLI, save JSON output to workdir. Returns JSON path or None."""
    out_json = workdir / f"{slug}.dembrandt.json"
    # Windows: npx is npx.cmd — subprocess list form can't resolve .cmd without shell
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [npx_cmd, "-y", "dembrandt", safe_url(url), "--save-output", "--mobile"]
    try:
        res = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_s, cwd=str(workdir)
        )
        # dembrandt --save-output writes to <cwd>/output/<domain>/<timestamp>.json
        outdir = workdir / "output"
        if outdir.exists():
            jsons = sorted(outdir.rglob("*.json"))
            if jsons:
                latest = jsons[-1]
                shutil.move(str(latest), str(out_json))
                shutil.rmtree(str(outdir), ignore_errors=True)
                return out_json
        # fallback: capture stdout if it happens to be JSON
        text = res.stdout.strip()
        if text.startswith("{"):
            out_json.write_text(text, encoding="utf-8")
            return out_json
        if res.returncode != 0:
            print(f"      dembrandt rc={res.returncode}: {res.stderr[-300:]}")
    except subprocess.TimeoutExpired:
        print("      dembrandt timed out")
    except Exception as e:  # noqa: BLE001
        print(f"      dembrandt error: {e}")
    return None


def fingerprint_from_tokens(tokens: dict | None, slug: str) -> dict:
    """Normalize dembrandt output into a compact fingerprint for the engine."""
    fp = {"slug": slug, "extracted": bool(tokens)}
    if not tokens:
        return fp
    colors = tokens.get("colors") or {}
    fp["palette"] = {
        "semantic": colors.get("semantic") or [],
        "raw": colors.get("palette") or [],
        "css_variables": colors.get("cssVariables") or [],
    }
    typo = tokens.get("typography") or {}
    styles = typo.get("styles") or []
    fp["typography"] = {
        "styles": styles,
        "sources": typo.get("sources") or [],
        "fonts": sorted({s.get("family", "") for s in styles if s.get("family")}),
        "sizes": sorted({s.get("size", "") for s in styles if s.get("size")}),
    }
    spacing = tokens.get("spacing") or {}
    common = spacing.get("commonValues") or []
    fp["spacing"] = {
        "scale_type": spacing.get("scaleType") or "unknown",
        "common_values": common,
        "scale": [v.get("px") for v in common if v.get("px")],
    }
    borders = tokens.get("borders") or {}
    radii = tokens.get("borderRadius") or {}
    fp["borders"] = {
        "radius": [r.get("value") for r in (radii.get("values") or [])],
        "widths": borders.get("widths") or [],
    }
    fp["shadows"] = tokens.get("shadows") or []
    fp["motion"] = tokens.get("motion") or {}
    fp["components"] = tokens.get("components") or []
    fp["breakpoints"] = tokens.get("breakpoints") or []
    return fp


def write_card(site: dict, slug: str, card_dir: Path, captured_at: str,
               screenshots: dict, fp: dict, tokens_path: Path | None):
    card_md = f"""# {site['name']}

- **URL:** {site['url']}
- **Category:** {site.get('category', 'misc')}
- **Captured:** {captured_at}
- **Slug:** `{slug}`

## Why it's in the library

{site.get('why', '')}

## What to borrow from it

(annotation pass — filled in when this card is cited by a recommendation)

## Fingerprint summary

- Palette: {len(fp.get('palette', {}).get('raw', []))} raw colors, {len(fp.get('palette', {}).get('semantic', []))} semantic
- Fonts: {', '.join(fp.get('typography', {}).get('fonts', [])[:4]) or 'n/a'}
- Type sizes: {', '.join(str(s) for s in fp.get('typography', {}).get('sizes', [])[:8]) or 'n/a'}
- Spacing scale: {', '.join(str(s) for s in fp.get('spacing', {}).get('scale', [])[:10]) or 'n/a'}
- Radii: {', '.join(str(r) for r in fp.get('borders', {}).get('radius', [])[:6]) or 'n/a'}
- Components detected: {len(fp.get('components', []))}
- Motion: {json.dumps(fp.get('motion', {}))[:200] or 'n/a'}

## Files

- `screenshot-desktop.png` — full-page, 1440px
- `screenshot-mobile.png` — full-page, 390px
- `fingerprint.json` — raw Dembrandt tokens
- `source.md` — capture metadata
- `motion/card-motion.webm` — recorded session: entrance anims, scroll-reveals, hover states, micro-interactions
- `motion/hover-NN.png` + `motion/hover-inventory.json` — hover-state captures per interactive element
"""
    (card_dir / "card.md").write_text(card_md, encoding="utf-8")
    (card_dir / "source.md").write_text(
        f"# Source\n\n- URL: {site['url']}\n- Captured: {captured_at}\n"
        f"- Screenshots: desktop {DESKTOP_VIEWPORT['width']}x{DESKTOP_VIEWPORT['height']}, "
        f"mobile {MOBILE_VIEWPORT['width']}x{MOBILE_VIEWPORT['height']}\n"
        f"- Tooling: playwright {DESKTOP_VIEWPORT} + dembrandt CLI\n",
        encoding="utf-8",
    )


def finalize_video(motion_dir: Path) -> str | None:
    """Move the recorded webm out of the timestamped subdir. MUST run after
    context.close() (the recording is finalized on close)."""
    video_dir = motion_dir / "video"
    vids = sorted(video_dir.rglob("*.webm")) if video_dir.exists() else []
    if vids:
        dest = motion_dir / "card-motion.webm"
        shutil.move(str(vids[-1]), str(dest))
        shutil.rmtree(video_dir, ignore_errors=True)
        return "card-motion.webm"
    shutil.rmtree(video_dir, ignore_errors=True)
    return None


def motion_pass(card_dir: Path, url: str, browser, timeout_s: int = 120) -> dict:
    """Thin wrapper around interaction_probe WITH video recording — kept for
    backfill's selective per-pass runs. Never raises.

    Returns the motion-shaped summary: {video, hovers, clicks, error}.
    """
    motion_dir = card_dir / "motion"
    video_dir = motion_dir / "video"
    video_dir.mkdir(parents=True, exist_ok=True)
    out = {"video": None, "hovers": 0, "clicks": 0, "error": None}
    ctx = None
    try:
        ctx = browser.new_context(
            viewport=DESKTOP_VIEWPORT, user_agent=CHROME_UA,
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 800},
        )
        page = ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)
        resp = page.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
        status = resp.status if resp else "?"
        if status and status >= 400:
            raise RuntimeError(f"HTTP {status}")
        page.wait_for_timeout(2000)  # entrance animations play
        from behavior_pass import interaction_probe
        res = interaction_probe(page, card_dir, url)
        out.update({"hovers": res.get("hovers", 0), "clicks": res.get("clicks", 0),
                    "error": res.get("error")})
    except Exception as e:  # noqa: BLE001
        out["error"] = str(e)[:200]
    finally:
        if ctx:
            try:
                ctx.close()  # finalizes the recording
            except Exception:  # noqa: BLE001
                pass
    out["video"] = finalize_video(motion_dir)
    return out


def _opt(opts, name: str, default=None):
    """Read an option from a dict OR an argparse Namespace (both callers)."""
    if isinstance(opts, dict):
        return opts.get(name, default)
    return getattr(opts, name, default)


def capture_one(site: dict, slug: str, card_dir: Path, browser, opts) -> dict:
    url = safe_url(site["url"])
    captured_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    workdir = card_dir / "tmp"
    workdir.mkdir(parents=True, exist_ok=True)
    result = {"id": site.get("id", slug), "slug": slug, "url": url, "ok": False,
              "error": None, "screenshots": {}, "fingerprint": None, "captured_at": captured_at}

    try:
        fast = _opt(opts, "fast", False)
        # ONE desktop context for semantic + screenshot + merged interaction
        # probe (6 loads → 3). Video recording is context-creation-only, so it
        # is decided up front; the video spans the whole session (deliberate).
        video_dir = card_dir / "motion" / "video"
        ctx = browser.new_context(
            viewport=DESKTOP_VIEWPORT, user_agent=CHROME_UA,
            **({} if fast else {"record_video_dir": str(video_dir),
                                "record_video_size": {"width": 1280, "height": 800}}))
        page = ctx.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)
        resp = page.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
        status = resp.status if resp else "?"
        if status and status >= 400:
            raise RuntimeError(f"HTTP {status}")
        page.wait_for_timeout(2000)  # let client JS settle

        # 1. semantic — read-only; a failure must not skip the rest (per-core
        #    failure isolation: each step below is individually guarded)
        try:
            from semantic_pass import semantic_probe
            semantic = semantic_probe(page, card_dir, url)
            result["semantic"] = semantic
            if semantic.get("ok"):
                print(f"      semantic: tokens={semantic.get('named_tokens')} "
                      f"z={semantic.get('z_index')} responsive={semantic.get('responsive_rules')}")
            elif semantic.get("error"):
                print(f"      semantic: skipped ({semantic['error'][:80]})")
        except Exception as e:  # noqa: BLE001
            result["semantic"] = {"ok": False, "error": str(e)[:200]}
            print(f"      semantic: skipped (import/run error: {str(e)[:80]})")

        # 2. reference screenshot BEFORE any hover (a hover state must never
        #    bleed into the screenshot every card in the library shows)
        desktop_png = card_dir / "screenshot-desktop.png"
        if full_page_screenshot(page, desktop_png):
            result["screenshots"]["desktop"] = "screenshot-desktop.png"

        # 3. merged motion+behavior probe — scroll sweep, hover diffs, video
        #    content; ends with click + go_back, the last state change
        if not fast:
            try:
                page.evaluate("window.scrollTo(0, 0)")  # full-page shot scrolls internally
                from behavior_pass import interaction_probe
                motion = interaction_probe(page, card_dir, url)
                result["motion"] = motion
                result["behavior"] = {k: motion.get(k) for k in
                                      ("ok", "hover_diffs", "scroll_triggers",
                                       "interaction_model", "error", "behaviors_file")}
                if motion.get("ok"):
                    print(f"      behavior: model={motion.get('interaction_model')} "
                          f"hovers={motion.get('hover_diffs')} scroll={motion.get('scroll_triggers')}")
                elif motion.get("error"):
                    print(f"      behavior: skipped ({motion['error'][:80]})")
            except Exception as e:  # noqa: BLE001
                result["motion"] = {"ok": False, "error": str(e)[:200]}
                result["behavior"] = {"ok": False, "error": str(e)[:200]}
                print(f"      behavior: skipped (import/run error: {str(e)[:80]})")
        else:
            result["motion"] = {"video": None, "skipped": "fast mode (opts.fast)"}
            print("      motion: skipped (fast mode)")

        ctx.close()  # finalizes the recording
        if not fast:
            vid = finalize_video(card_dir / "motion")
            if vid:
                result["motion"]["video"] = vid
                print(f"      motion: video={vid} hovers={result['motion'].get('hovers')} "
                      f"clicks={result['motion'].get('clicks')}")

        # mobile pass — separate context: iPhone UA is context-creation-only
        mctx = browser.new_context(viewport=MOBILE_VIEWPORT, user_agent=IPHONE_UA)
        mpage = mctx.new_page()
        mpage.set_default_timeout(NAV_TIMEOUT_MS)
        try:
            mpage.goto(url, wait_until="load", timeout=NAV_TIMEOUT_MS)
            mpage.wait_for_timeout(2000)
            mobile_png = card_dir / "screenshot-mobile.png"
            if full_page_screenshot(mpage, mobile_png, wait_s=1.5):
                result["screenshots"]["mobile"] = "screenshot-mobile.png"
        except Exception as e:  # noqa: BLE001
            print(f"      mobile screenshot failed: {e}")
        mpage.close()
        mctx.close()

        tokens_path = dembrandt_tokens(url, slug, workdir)
        tokens = None
        if tokens_path and tokens_path.exists():
            try:
                tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                tokens = None
            fp_path = card_dir / "fingerprint.json"
            fp_path.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
        fp = fingerprint_from_tokens(tokens, slug)
        result["fingerprint"] = fp

        if not result["screenshots"] and fp.get("extracted") is False:
            raise RuntimeError("no screenshots and no tokens extracted")

        write_card(site, slug, card_dir, captured_at, result["screenshots"], fp, tokens_path)
        result["ok"] = True
    except Exception as e:  # noqa: BLE001
        result["error"] = str(e)[:300]
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return result


def build_index_entry(site: dict, slug: str, res: dict) -> dict:
    """The canonical index.json entry shape — shared by the CLI, the MCP
    worker, and regenerate_media so all three write identical cards."""
    fp = res.get("fingerprint") or {}
    return {
        "id": site.get("id", slug),
        "name": site["name"],
        "url": site["url"],
        "category": site.get("category"),
        "why": site.get("why"),
        "slug": slug,
        "captured_at": res["captured_at"],
        "files": {
            "card": f"cards/{slug}/card.md",
            "desktop": f"cards/{slug}/screenshot-desktop.png" if "desktop" in res.get("screenshots", {}) else None,
            "mobile": f"cards/{slug}/screenshot-mobile.png" if "mobile" in res.get("screenshots", {}) else None,
            "fingerprint": f"cards/{slug}/fingerprint.json" if fp.get("extracted") else None,
        },
        "fingerprint_summary": {
            "colors": len(fp.get("palette", {}).get("raw", [])) if fp else 0,
            "fonts": fp.get("typography", {}).get("fonts", [])[:4] if fp else [],
            "components": len(fp.get("components", [])) if fp else 0,
        },
    }


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", nargs="?", default=None, help="seed JSON path (omit with --url)")
    ap.add_argument("--url", default=None, help="single-URL capture mode")
    ap.add_argument("--name", default=None, help="site name (single-URL mode)")
    ap.add_argument("--category", default="other", help="category (single-URL mode)")
    ap.add_argument("--slug", default=None, help="explicit slug (single-URL mode; default from hostname)")
    ap.add_argument("--why", default="", help="rationale (single-URL mode)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--only", default="", help="comma-separated slugs")
    ap.add_argument("--skip", default="", help="comma-separated slugs")
    ap.add_argument("--redo", action="store_true", help="recapture even if card exists")
    args = ap.parse_args()

    seed_path = Path(args.seed) if args.seed else None
    if seed_path and not seed_path.is_absolute():
        seed_path = LIBRARY / seed_path

    if args.url:
        # single-URL mode: synthesize one seed entry, no seed file needed
        from urllib.parse import urlparse
        host = urlparse(safe_url(args.url)).netloc.replace("www.", "").split(":")[0]
        slug = args.slug or slugify(args.name or host)
        sites = [{
            "id": slug,
            "name": args.name or host,
            "url": safe_url(args.url),
            "category": args.category or "other",
            "why": args.why,
        }]
    else:
        if not seed_path:
            ap.error("provide a seed JSON or --url")
        sites = load_seed(seed_path)

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    if only:
        sites = [s for s in sites if slugify(s.get("id", s["name"])) in only or s.get("id") in only]
    if skip:
        sites = [s for s in sites if slugify(s.get("id", s["name"])) not in skip and s.get("id") not in skip]
    if args.limit:
        sites = sites[: args.limit]

    index = load_index()
    results = []
    failures = []
    print(f"[capture] {len(sites)} sites → {CARDS}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for i, site in enumerate(sites, 1):
            slug = slugify(site.get("id", site["name"]))
            card_dir = CARDS / slug
            if card_exists(slug) and not args.redo:
                print(f"[{i}/{len(sites)}] {slug} — already captured, skipping (--redo to recapture)")
                results.append({"slug": slug, "ok": True, "skipped": True})
                continue
            if card_dir.exists():
                print(f"[{i}/{len(sites)}] {slug} — previous attempt left no card.md, retrying")
            print(f"[{i}/{len(sites)}] {slug} ({site['url']}) …", flush=True)
            t0 = time.time()
            res = capture_one(site, slug, card_dir, browser, args)
            res["seconds"] = round(time.time() - t0, 1)
            results.append(res)
            if res["ok"]:
                print(f"      ✓ ok in {res['seconds']}s — screenshots: {list(res['screenshots'].keys())}, "
                      f"tokens: {'yes' if res['fingerprint'] and res['fingerprint'].get('extracted') else 'no'}")
            else:
                failures.append(res)
                print(f"      ✗ FAILED: {res['error']}")

            if res["ok"]:
                index.setdefault("cards", {})[slug] = build_index_entry(site, slug, res)
                index.setdefault("stats", {})["last_run"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                index.setdefault("stats", {})["total"] = len(index["cards"])
                save_index(index)

    print(f"\n=== done: {len(results) - len(failures)}/{len(results)} ok, {len(failures)} failed ===")
    if failures:
        print("Failures:")
        for f in failures:
            print(f"  - {f['slug']}: {f['error']}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
