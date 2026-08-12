#!/usr/bin/env python3
"""design-scope annotate — LLM design-intelligence pass over library cards.

Writes `library/cards/<slug>/annotation.json` — the TRACKED intelligence
layer (ships in OSS; media stays out of git). Makes style_search find cards
by design quality, not just vector math.

Provider: NVIDIA NIM (OpenAI-compatible). Model:
  nvidia/nemotron-3-nano-omni-30b-a3b-reasoning (vision-capable, verified)
Key: NVIDIA_API_KEY from the environment or a HERMES_ENV .env file (never
  hardcoded, never printed).
Rate: 40 RPM limit → 2s spacing between calls.

Resumable: cards with an existing annotation.json are skipped. Honest
fallback: if vision fails after retries, annotate from fingerprint +
semantic text only (vision.status = "fallback") — never fabricate.

Usage:
  python annotate.py                      # all cards, skip done
  python annotate.py --only stripe,discord
  python annotate.py --limit 5
  python annotate.py --sleep 2.0          # pacing override
"""
import argparse
import base64
import io
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image

LIB = Path(__file__).resolve().parent
LIBRARY = Path(os.environ.get("DESIGN_SCOPE_LIBRARY", str(LIB))).resolve()
CARDS = LIBRARY / "cards"

MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MAX_TOKENS = 2048
REASONING_BUDGET = 1024
CROP_H = 1800   # full-page PNGs are too tall for the API — keep hero screenful
CROP_W = 1200

REQUIRED_FIELDS = ["design_intent", "what_works", "search_terms"]
LIST_FIELDS = ["what_works", "search_terms"]
INTENT_FIELDS = ["vibe", "mood", "personality", "keywords"]


def load_key() -> str:
    key = os.environ.get("NVIDIA_API_KEY", "")
    if not key:
        # optional .env fallback — HERMES_ENV may point at any .env file
        env_path = Path(os.environ["HERMES_ENV"]) if os.environ.get("HERMES_ENV") else None
        if env_path and env_path.exists():
            m = re.search(r"NVIDIA_API_KEY=(\S+)", env_path.read_text(encoding="utf-8"))
            key = m.group(1) if m else ""
    if not key:
        raise SystemExit("NVIDIA_API_KEY not found — set it in the environment "
                         "(or HERMES_ENV pointing at a .env file)")
    return key


def crop_screenshot(card_dir: Path) -> Image.Image | None:
    """Crop the desktop screenshot to a vision-safe size. None if missing."""
    png = card_dir / "screenshot-desktop.png"
    if not png.exists():
        return None
    img = Image.open(png)
    w, h = img.size
    if h > CROP_H:
        img = img.crop((0, 0, w, CROP_H))
    if w > CROP_W:
        img = img.resize((CROP_W, round(CROP_W * img.height / img.width)))
    return img


def fingerprint_summary(card_dir: Path) -> str:
    """Compact text evidence from fingerprint + semantic + behaviors."""
    parts = []
    fp = json.loads((card_dir / "fingerprint.json").read_text(encoding="utf-8")) \
        if (card_dir / "fingerprint.json").exists() else {}
    c = (fp.get("colors") or {}).get("semantic", {}) or {}
    if c:
        parts.append("colors: " + ", ".join(f"{k} {v}" for k, v in list(c.items())[:6]))
    fonts = sorted({s.get("family") for s in ((fp.get("typography") or {}).get("styles") or [])
                    if s.get("family")})[:4]
    if fonts:
        parts.append("fonts: " + ", ".join(fonts))
    sp = (fp.get("spacing") or {}).get("commonValues") or []
    if sp:
        parts.append("spacing: " + ", ".join(str(s.get("px")) for s in sp[:4]))
    radii = (fp.get("borderRadius") or {}).get("values") or []
    if radii:
        dom = max(radii, key=lambda r: r.get("count", 0))
        parts.append(f"dominant radius: {dom.get('value')}")

    sem = json.loads((card_dir / "semantic.json").read_text(encoding="utf-8")) \
        if (card_dir / "semantic.json").exists() else {}
    di = sem.get("design_intent", {})
    if di.get("vibe"):
        parts.append("measured vibe: " + ", ".join(di["vibe"]))
    if di.get("type_mood"):
        parts.append("type mood: " + ", ".join(di["type_mood"]))
    if di.get("flat") is not None:
        parts.append("flat: " + ("yes" if di["flat"] else "no"))

    beh = json.loads((card_dir / "motion" / "behaviors.json").read_text(encoding="utf-8")) \
        if (card_dir / "motion" / "behaviors.json").exists() else {}
    if beh.get("interaction_model"):
        parts.append(f"interaction model: {beh['interaction_model']}")

    return "; ".join(parts) or "no fingerprint data"


def build_prompt(summary: str) -> str:
    return f"""You are a design critic annotating a reference card for a design library.
Describe the DESIGN only — never mention the company or brand name.

Measured data for this site:
{summary}

Look at the screenshot and respond with STRICT JSON:
{{
  "design_intent": {{"vibe": "2-3 words", "mood": "2-3 words", "personality": "short phrase", "keywords": ["4-8 design words"]}},
  "what_works": ["3-5 specific design observations from the screenshot"],
  "search_terms": ["8-12 adjectives/nouns a designer would search by — NO brand names"],
  "confidence": "high|medium|low"
}}"""


def call_nvidia(key: str, prompt: str, img: Image.Image | None,
                timeout_s: int = 180) -> dict:
    """One annotated call. Returns the parsed JSON dict. Raises on HTTP/JSON failure."""
    content = [{"type": "text", "text": prompt}]
    if img is not None:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        content.append({"type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"}})
    r = requests.post(
        ENDPOINT,
        headers={"Authorization": f"Bearer {key}", "Accept": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": MAX_TOKENS,
            "reasoning_budget": REASONING_BUDGET,
            "stream": False,
            "temperature": 0.3,
        },
        timeout=timeout_s,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    text = r.json()["choices"][0]["message"]["content"]
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    return json.loads(text)


def validate(data: dict) -> bool:
    """Schema check: required fields present, list fields are lists."""
    if not isinstance(data, dict):
        return False
    if not all(k in data for k in REQUIRED_FIELDS):
        return False
    if not all(isinstance(data.get(k), list) for k in LIST_FIELDS):
        return False
    di = data.get("design_intent")
    if not isinstance(di, dict) or not all(k in di for k in INTENT_FIELDS):
        return False
    return True


def fallback_annotation(card_dir: Path) -> dict:
    """Honest text-only annotation from measured data (vision unavailable)."""
    sem = json.loads((card_dir / "semantic.json").read_text(encoding="utf-8")) \
        if (card_dir / "semantic.json").exists() else {}
    di = sem.get("design_intent", {})
    keywords = [str(k).lower() for k in (di.get("vibe") or [])]
    keywords += [str(k).lower() for k in (di.get("type_mood") or [])]
    keywords += [str(k).lower() for k in (di.get("corner_style") or [])] \
        if isinstance(di.get("corner_style"), list) else []
    keywords = list(dict.fromkeys([k for k in keywords if k])) or ["unannotated"]
    fp = json.loads((card_dir / "fingerprint.json").read_text(encoding="utf-8")) \
        if (card_dir / "fingerprint.json").exists() else {}
    fonts = [f for f in sorted({s.get("family") for s in ((fp.get("typography") or {}).get("styles") or [])
                                if s.get("family")})][:2]
    return {
        "design_intent": {"vibe": "unannotated", "mood": "unannotated",
                          "personality": "vision unavailable; annotated from measured data",
                          "keywords": keywords},
        "what_works": [],
        "search_terms": keywords + [f.lower() for f in fonts],
        "confidence": "low",
        "vision": {"status": "fallback",
                   "note": "vision call failed after retries; annotated from fingerprint/semantic text"},
    }


def annotate_card(key: str, card_dir: Path, sleep_s: float) -> dict:
    """Annotate one card. Returns the annotation dict (vision or fallback)."""
    img = crop_screenshot(card_dir)
    summary = fingerprint_summary(card_dir)
    prompt = build_prompt(summary)
    last_err = None
    for attempt, backoff in enumerate((2, 4, 8)):
        try:
            data = call_nvidia(key, prompt, img)
            if not validate(data):
                raise ValueError("schema-invalid response")
            data.setdefault("vision", {"status": "ok"})
            return data
        except Exception as e:  # noqa: BLE001
            last_err = str(e)[:200]
            if attempt < 2:
                time.sleep(backoff)
    # vision failed — honest fallback (never fabricate)
    ann = fallback_annotation(card_dir)
    ann["vision"]["note"] = f"{ann['vision']['note']}; {last_err}"
    return ann


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma-separated slugs to annotate")
    ap.add_argument("--limit", type=int, default=0, help="max cards this run (0 = all)")
    ap.add_argument("--sleep", type=float, default=2.0, help="pacing between calls (40 RPM → 2.0)")
    args = ap.parse_args()

    key = load_key()
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    slugs = sorted(p.name for p in CARDS.iterdir() if p.is_dir())
    if only:
        slugs = [s for s in slugs if s in only]

    done = skipped = failed = 0
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report = {"started": started, "model": MODEL}

    for i, slug in enumerate(slugs, 1):
        card_dir = CARDS / slug
        out = card_dir / "annotation.json"
        if out.exists():
            skipped += 1
            continue
        if args.limit and done >= args.limit:
            break
        print(f"[{i}/{len(slugs)}] {slug} …", flush=True)
        t0 = time.time()
        try:
            ann = annotate_card(key, card_dir, args.sleep)
            ann["slug"] = slug
            ann["annotated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            ann["model"] = MODEL
            out.write_text(json.dumps(ann, indent=2, ensure_ascii=False), encoding="utf-8")
            status = ann.get("vision", {}).get("status", "?")
            print(f"      ✓ {status} in {time.time() - t0:.1f}s — "
                  f"terms={len(ann.get('search_terms', []))} conf={ann.get('confidence')}")
            done += 1
        except Exception as e:  # noqa: BLE001
            print(f"      ✗ failed: {str(e)[:120]}")
            failed += 1
        if i < len(slugs):
            time.sleep(args.sleep)

    report.update({"annotated": done, "skipped": skipped, "failed": failed})
    print(f"\n=== annotate done: {done} annotated, {skipped} skipped, {failed} failed ===")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
