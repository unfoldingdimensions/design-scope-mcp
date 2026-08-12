#!/usr/bin/env python3
"""design-scope backfill — runs the motion + behavior passes on existing cards
that were captured before those passes existed (2026-08-09+).

Only runs motion_pass + behavior_pass per card — does NOT re-capture
screenshots or tokens (they're already good). Skips cards that already have
both. Resumable: safe to stop and re-run.

Usage:
  python backfill.py [--limit N] [--only slug1,slug2] [--skip slug1]
  python backfill.py --limit 3          # smoke test
  python backfill.py --only framer      # specific card

Output: library/backfill-report.json + printed progress.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

from behavior_pass import behavior_pass
from capture import motion_pass
from semantic_pass import semantic_pass

from _console import utf8_stdout

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
CARDS = LIBRARY / "cards"
INDEX = LIBRARY / "index.json"


def needs_backfill(slug: str) -> tuple[bool, bool, bool]:
    """Returns (missing_motion, missing_behavior, missing_semantic)."""
    motion_dir = CARDS / slug / "motion"
    has_motion = (motion_dir / "card-motion.webm").exists()
    has_behavior = (motion_dir / "behaviors.md").exists()
    has_semantic = (CARDS / slug / "semantic.json").exists()
    return (not has_motion), (not has_behavior), (not has_semantic)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--only", default="", help="comma-separated slugs")
    ap.add_argument("--skip", default="", help="comma-separated slugs")
    args = ap.parse_args()

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    cards = index.get("cards", {})

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    slugs = list(cards.keys())
    if only:
        slugs = [s for s in slugs if s in only]
    if skip:
        slugs = [s for s in slugs if s not in skip]

    report = {"started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "scanned": 0, "motion_added": 0, "behavior_added": 0, "semantic_added": 0,
              "already_done": 0, "failed": [], "cards": {}}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for i, slug in enumerate(slugs, 1):
            if args.limit and i > args.limit:
                break
            card = cards[slug]
            url = card["url"]
            card_dir = CARDS / slug
            missing_m, missing_b, missing_s = needs_backfill(slug)
            report["scanned"] += 1
            entry = {"url": url}

            if not missing_m and not missing_b and not missing_s:
                report["already_done"] += 1
                print(f"[{i}/{len(slugs)}] {slug} — already has motion+behavior+semantic, skipping")
                continue

            print(f"[{i}/{len(slugs)}] {slug} ({url}) …", flush=True)
            t0 = time.time()
            try:
                if missing_m:
                    m = motion_pass(card_dir, url, browser)
                    entry["motion"] = {"video": m.get("video"), "hovers": m.get("hovers"),
                                       "clicks": m.get("clicks"), "error": m.get("error")}
                    if m.get("video"):
                        report["motion_added"] += 1
                        print(f"      motion: video ✓ hovers={m.get('hovers')}")
                    elif m.get("error"):
                        print(f"      motion: skipped ({m['error'][:80]})")
                if missing_b:
                    b = behavior_pass(card_dir, url, browser)
                    entry["behavior"] = {"ok": b.get("ok"), "model": b.get("interaction_model"),
                                         "hovers": b.get("hover_diffs"), "scroll": b.get("scroll_triggers"),
                                         "error": b.get("error")}
                    if b.get("ok"):
                        report["behavior_added"] += 1
                        print(f"      behavior: model={b.get('interaction_model')} "
                              f"hovers={b.get('hover_diffs')} scroll={b.get('scroll_triggers')}")
                    elif b.get("error"):
                        print(f"      behavior: skipped ({b['error'][:80]})")
                if missing_s:
                    s = semantic_pass(card_dir, url, browser)
                    entry["semantic"] = {"ok": s.get("ok"), "tokens": s.get("named_tokens"),
                                         "z": s.get("z_index"), "responsive": s.get("responsive_rules"),
                                         "error": s.get("error")}
                    if s.get("ok"):
                        report["semantic_added"] += 1
                        print(f"      semantic: tokens={s.get('named_tokens')} "
                              f"z={s.get('z_index')} responsive={s.get('responsive_rules')}")
                    elif s.get("error"):
                        print(f"      semantic: skipped ({s['error'][:80]})")
                entry["seconds"] = round(time.time() - t0, 1)
            except Exception as e:  # noqa: BLE001
                entry["error"] = str(e)[:200]
                report["failed"].append({"slug": slug, "error": str(e)[:200]})
                print(f"      ✗ FAILED: {str(e)[:120]}")
            report["cards"][slug] = entry

        browser.close()

    report["finished"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report["total"] = len(report["cards"])
    (LIB / "backfill-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n=== backfill done: scanned={report['scanned']} "
          f"motion_added={report['motion_added']} behavior_added={report['behavior_added']} "
          f"semantic_added={report['semantic_added']} "
          f"already_done={report['already_done']} failed={len(report['failed'])} ===")
    if report["failed"]:
        print("Failures:")
        for f in report["failed"]:
            print(f"  - {f['slug']}: {f['error'][:100]}")
    print(f"report → {LIB / 'backfill-report.json'}")
    sys.exit(1 if report["failed"] else 0)


if __name__ == "__main__":
    main()
