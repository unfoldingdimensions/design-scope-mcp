#!/usr/bin/env python3
"""design-scope showcase builder — injects the measured facts into a sheet.

Variants:
  main      — showcase/index.html from showcase/index.template.html
              (the hand-built sheet; stats + verdict + ledger)
  one-shot  — showcase/one-shot/index.html from showcase/one-shot/index.template.html
              (decisions by the server: borrowed tokens, band contract, register)

Flow (one-shot):
  python scripts/one_shot.py prepare --brief "..."        # tools → register.json
  [compose the page — rendering is the agent's job]
  python scripts/one_shot.py grade --label "R1 one-shot"  # verdict + ledger + rebuild

RUN WITH THE LIBRARY ENV'S PYTHON (same venv as capture.py / stats.py).
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from stats import compute, LIBRARY  # noqa: E402

VARIANTS = {
    "main": {
        "template": ROOT / "showcase" / "index.template.html",
        "out": ROOT / "showcase" / "index.html",
        "verdict": ROOT / "showcase" / "verdict.json",
        "ledger": ROOT / "showcase" / "verdicts.json",
    },
    "one-shot": {
        "template": ROOT / "showcase" / "one-shot" / "index.template.html",
        "out": ROOT / "showcase" / "one-shot" / "index.html",
        "verdict": ROOT / "showcase" / "one-shot" / "verdict.json",
        "ledger": ROOT / "showcase" / "one-shot" / "verdicts.json",
        "tokens": ROOT / "showcase" / "one-shot" / "tokens.json",
        "register": ROOT / "showcase" / "one-shot" / "register.json",
    },
}

MARKER = "/*__DATA__*/"
TOKENS_LIGHT_MARKER = "/*__TOKENS_LIGHT__*/"
TOKENS_DARK_MARKER = "/*__TOKENS_DARK__*/"


def build_variant(variant: str = "main") -> Path:
    spec = VARIANTS[variant]
    template = spec["template"]
    if not template.exists():
        print(f"template not found: {template}", file=sys.stderr)
        sys.exit(2)

    stats = compute(LIBRARY)
    verdict = None
    if spec["verdict"].exists():
        verdict = json.loads(spec["verdict"].read_text(encoding="utf-8"))
    ledger = []
    if spec["ledger"].exists():
        ledger = json.loads(spec["ledger"].read_text(encoding="utf-8"))

    payload = {"stats": stats, "verdict": verdict, "ledger": ledger}

    html = template.read_text(encoding="utf-8")

    if variant == "one-shot":
        tokens = json.loads(spec["tokens"].read_text(encoding="utf-8"))
        register = json.loads(spec["register"].read_text(encoding="utf-8"))
        payload["oneShot"] = {"register": register["entries"],
                              "card": register.get("card", {}),
                              "derivations": register.get("derivations", []),
                              "brief": register.get("brief", ""),
                              "direction": register.get("direction", ""),
                              "credits": register.get("credits", "0")}
        light_css = "\n".join(f"  {k}: {v};" for k, v in tokens["light"].items())
        dark_css = "\n".join(f"  {k}: {v};" for k, v in tokens["dark"].items())
        html = html.replace(TOKENS_LIGHT_MARKER, light_css)
        html = html.replace(TOKENS_DARK_MARKER, dark_css)
        if TOKENS_LIGHT_MARKER in html or TOKENS_DARK_MARKER in html:
            print(f"token markers not fully replaced in {template}", file=sys.stderr)
            sys.exit(2)

    blob = "window.SHOWCASE = " + json.dumps(payload, ensure_ascii=False) + ";"
    if MARKER not in html:
        print(f"marker {MARKER} not found in {template}", file=sys.stderr)
        sys.exit(2)
    html = html.replace(MARKER, blob)
    spec["out"].write_text(html, encoding="utf-8")

    print(f"showcase[{variant}] -> {spec['out']}")
    print(f"  corpus: {stats['corpus']['captured']} captured · "
          f"{stats['corpus']['annotated']} annotated · "
          f"{stats['corpus']['style_indexed']} indexed")
    print(f"  verdict: {verdict['summary']['score'] if verdict else 'PENDING (run scripts/verdict.py)'}")
    print(f"  ledger: {len(ledger)} row(s)")
    return spec["out"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=list(VARIANTS), default="main")
    args = ap.parse_args()
    build_variant(args.variant)


if __name__ == "__main__":
    main()
