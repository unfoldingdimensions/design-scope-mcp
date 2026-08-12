#!/usr/bin/env python3
"""design-scope regenerate-media — rebuild screenshots/motion for library
cards from the tracked index.json. THE OSS REBUILD COMMAND.

The shipped repo contains only the intelligence layer (index.json, card
metadata, fingerprints, annotations — ~9MB). Media (screenshots, motion
videos) is regenerable: this script walks index.json and captures any
card missing its media (or --all to redo everything).

Usage:
  python regenerate_media.py                # capture cards missing media
  python regenerate_media.py --all          # recapture everything (--redo)
  python regenerate_media.py --only stripe  # specific cards
  python regenerate_media.py --fast         # skip motion+behavior (~60s/card)

Timing: full pass ≈ 4-6 min/card (motion+behavior+semantic); --fast ≈
60s/card. 201 cards full ≈ 14-20h background; --fast ≈ 3-4h.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from _console import utf8_stdout

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
CARDS = LIBRARY / "cards"
INDEX = LIBRARY / "index.json"

MEDIA_MARKER = "screenshot-desktop.png"  # present → media layer exists


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="recapture even cards with media (--redo)")
    ap.add_argument("--only", default="", help="comma-separated slugs")
    ap.add_argument("--fast", action="store_true", help="skip motion+behavior passes (~60s/card)")
    args = ap.parse_args()

    if not INDEX.exists():
        raise SystemExit(f"index.json missing: {INDEX} — this is the intelligence layer; nothing to rebuild from")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    entries = index["cards"]

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    if only:
        missing = only - set(entries)
        if missing:
            raise SystemExit(f"unknown slugs (not in index.json): {sorted(missing)}")
        slugs = sorted(only)
    else:
        slugs = sorted(entries)

    # playwright import must happen inside (heavy); reuse capture.batch machinery
    sys.path.insert(0, str(LIB))
    from capture import capture_one, slugify, build_index_entry, save_index
    from playwright.sync_api import sync_playwright

    results = []
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for i, slug in enumerate(slugs, 1):
                entry = entries[slug]
                card_dir = CARDS / slug
                has_media = (card_dir / MEDIA_MARKER).exists()
                if has_media and not args.all:
                    print(f"[{i}/{len(slugs)}] {slug} — media exists, skipping (--all to redo)")
                    results.append({"slug": slug, "ok": True, "skipped": True})
                    continue
                url = entry.get("url")
                if not url:
                    print(f"[{i}/{len(slugs)}] {slug} — no url in index, skipping")
                    results.append({"slug": slug, "ok": False, "error": "no url"})
                    continue
                name = entry.get("name", slug)
                print(f"[{i}/{len(slugs)}] {slug} ({url}) …", flush=True)
                t0 = time.time()
                try:
                    site = {"id": slug, "name": name, "url": url,
                            "category": entry.get("category", "misc"),
                            "why": entry.get("why")}
                    res = capture_one(site, slugify(slug), card_dir, browser,
                                      opts={"fast": args.fast})
                    res["seconds"] = round(time.time() - t0, 1)
                    results.append(res)
                    if res.get("ok"):
                        # keep the index entry in sync with what was captured
                        index["cards"][slug] = build_index_entry(site, slug, res)
                        index.setdefault("stats", {})["last_run"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                        save_index(index)
                        print(f"      ✓ ok in {res['seconds']}s — {list(res.get('screenshots', {}).keys())}")
                    else:
                        print(f"      ✗ failed: {str(res.get('error', 'unknown'))[:120]}")
                except Exception as e:  # noqa: BLE001
                    print(f"      ✗ failed: {str(e)[:120]}")
                    results.append({"slug": slug, "ok": False, "error": str(e)[:200]})
        finally:
            browser.close()

    # recaptured cards carry fresh semantic.json — the style vectors are built
    # from it, so rebuild the index the search tools read (the MCP capture path
    # already does this; regenerating media left the index stale).
    if any(r.get("ok") and not r.get("skipped") for r in results):
        try:
            from style_index import build_vectors, write_summary
            si = build_vectors()
            (LIBRARY / "style-index.json").write_text(
                json.dumps(si, indent=2, ensure_ascii=False), encoding="utf-8")
            write_summary(si)
            print(f"style-index rebuilt: {len(si['cards'])} cards")
        except Exception as e:  # noqa: BLE001
            print(f"style-index rebuild skipped: {str(e)[:120]}")

    ok = sum(1 for r in results if r.get("ok"))
    skipped = sum(1 for r in results if r.get("skipped"))
    failed = [r["slug"] for r in results if not r.get("ok") and not r.get("skipped")]
    print(f"\n=== regenerate-media done: {ok} ok, {skipped} skipped, {len(failed)} failed ===")
    if failed:
        print("failed:", ", ".join(failed))
    report = {"started": started, "ok": ok, "skipped": skipped, "failed": failed}
    (LIB / "regenerate-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("report → library/regenerate-report.json")


if __name__ == "__main__":
    main()
