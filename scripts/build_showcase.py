#!/usr/bin/env python3
"""design-scope showcase builder — injects the measured facts into the sheet.

Reads stats (computed fresh from the library), the latest verdict record
(showcase/verdict.json), and the ledger (showcase/verdicts.json), then
writes showcase/index.html from showcase/index.template.html.

Flow:
  python scripts/build_showcase.py            # build with current data
  python scripts/verdict.py showcase/index.html --label "R1 baseline" \
      --ledger showcase/verdicts.json --json showcase/verdict.json
  python scripts/build_showcase.py            # rebuild: rubric + ledger rows real

RUN WITH THE LIBRARY ENV'S PYTHON (same venv as capture.py / stats.py).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from stats import compute, LIBRARY  # noqa: E402

TEMPLATE = ROOT / "showcase" / "index.template.html"
OUT = ROOT / "showcase" / "index.html"
VERDICT_JSON = ROOT / "showcase" / "verdict.json"
LEDGER_JSON = ROOT / "showcase" / "verdicts.json"
MARKER = "/*__DATA__*/"


def main():
    stats = compute(LIBRARY)
    verdict = None
    if VERDICT_JSON.exists():
        verdict = json.loads(VERDICT_JSON.read_text(encoding="utf-8"))
    ledger = []
    if LEDGER_JSON.exists():
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))

    payload = {"stats": stats, "verdict": verdict, "ledger": ledger}
    blob = "window.SHOWCASE = " + json.dumps(payload, ensure_ascii=False) + ";"

    html = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in html:
        print(f"marker {MARKER} not found in {TEMPLATE}", file=sys.stderr)
        sys.exit(2)
    html = html.replace(MARKER, blob)
    OUT.write_text(html, encoding="utf-8")

    print(f"showcase -> {OUT}")
    print(f"  corpus: {stats['corpus']['captured']} captured · "
          f"{stats['corpus']['annotated']} annotated · "
          f"{stats['corpus']['style_indexed']} indexed")
    print(f"  verdict: {verdict['summary']['score'] if verdict else 'PENDING (run scripts/verdict.py)'}")
    print(f"  ledger: {len(ledger)} row(s)")


if __name__ == "__main__":
    main()
