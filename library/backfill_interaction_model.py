#!/usr/bin/env python3
"""design-scope backfill-interaction-model — persist the classified
interaction_model string in every card's behaviors.json.

The pre-2026-08-13 probe persisted the raw counter dict as
interaction_model and threw the classified string away (it only reached
behaviors.md). This walks the library and rewrites each card's
motion/behaviors.json:

  interaction_model   → "scroll-driven" | "click-driven" | "static"
  interaction_signals → the raw counter dict (former interaction_model)

Idempotent and resumable: entries whose interaction_model is already a
string are skipped. No network, no browser.

Usage:
  python library/backfill_interaction_model.py
  python library/backfill_interaction_model.py --only stripe,discord
"""
import argparse
import json
import os
import sys
from pathlib import Path

from _console import utf8_stdout
from behavior_pass import classify_interaction_model

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
CARDS = LIBRARY / "cards"


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated slugs")
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()}

    converted = skipped = failed = 0
    for slug in sorted(p.name for p in CARDS.iterdir() if p.is_dir()):
        if only and slug not in only:
            continue
        p = CARDS / slug / "motion" / "behaviors.json"
        if not p.exists():
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            raw = d.get("interaction_model")
            if isinstance(raw, str):
                skipped += 1
                continue
            signals = raw if isinstance(raw, dict) else {}
            d["interaction_signals"] = signals
            d["interaction_model"] = classify_interaction_model(signals)
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  {slug}: {d['interaction_model']}")
            converted += 1
        except Exception as e:  # noqa: BLE001
            print(f"  {slug}: FAILED {str(e)[:100]}")
            failed += 1

    print(f"\n=== done: {converted} converted, {skipped} skipped, {failed} failed ===")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
