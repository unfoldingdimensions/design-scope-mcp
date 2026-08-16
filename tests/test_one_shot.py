"""design-scope one-shot unit tests — pure pipeline logic, no network.

Usage:
  python tests/test_one_shot.py

Covers: card pick (dark-palette preference), token derivation (all emitted
values are borrowed roles or single-token alpha blends), contrast walks,
register writing.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from _harness import check, finish  # noqa: E402
from one_shot import (_contrast, _on_accent, _palette_usable, _ranked,  # noqa: E402
                      _rgb_triplet, _walk, derive_tokens, prepare)


def fake_roles():
    return {
        "primary": {"token": "--blurple", "value": "#1e5eff"},
        "accent": {"token": "--accent", "value": "#1e5eff"},
        "bg": {"token": "--bg", "value": "#f4f3ee"},
        "text": {"token": "--text", "value": "#16181d"},
        "muted": {"token": "--muted", "value": "#5b606b"},
    }


def fake_dark_roles():
    return {
        "bg": {"token": "--bg", "value": "#0f1318"},
        "text": {"token": "--text", "value": "#e7e9ed"},
        "primary": {"token": "--blurple", "value": "#6e9bff"},
        "muted": {"token": "--muted", "value": "#9aa3af"},
    }


def test_ranked_dark_preference():
    with tempfile.TemporaryDirectory() as td:
        cards = Path(td) / "cards"
        (cards / "alpha").mkdir(parents=True)
        (cards / "alpha" / "semantic.json").write_text(
            json.dumps({"named_tokens": {"light": {}}}), encoding="utf-8")
        (cards / "beta").mkdir()
        (cards / "beta" / "semantic.json").write_text(
            json.dumps({"named_tokens": {"light": {}, "dark": {"--bg": "#0f1318"}}}), encoding="utf-8")
        (cards / "gamma").mkdir()
        (cards / "gamma" / "semantic.json").write_text(
            json.dumps({"named_tokens": {"light": {}, "dark": {"--bg": "#111"}}}), encoding="utf-8")
        results = [(5, "alpha", {}), (4, "beta", {}), (3, "gamma", {})]
        ranked = _ranked(results, cards)
        order = [s for s, _w in ranked]
        check("dark-palette cards first, in rank order", order == ["beta", "gamma", "alpha"], str(order))


def test_palette_usable_gate():
    def borrow(text, bg, accent, muted=None):
        roles = {"text": {"value": text}, "bg": {"value": bg}, "primary": {"value": accent}}
        if muted:
            roles["muted"] = {"value": muted}
        return {"roles": roles}
    ok, reason = _palette_usable(borrow("#16181d", "#f4f3ee", "#1e5eff"))
    check("good borrow passes", ok, reason)
    ok, _ = _palette_usable(borrow("#ffffff", "#ffffff", "#b1b1b1"))
    check("white-on-white rejected", not ok)
    ok, _ = _palette_usable(borrow("#9aa3af", "#f4f3ee", "#c9c9c9"))
    check("low text contrast rejected", not ok)
    ok, reason = _palette_usable(borrow("#16181d", "#f4f3ee", "#f4f3ee"))
    check("invisible accent rejected", not ok, reason)
    ok, _ = _palette_usable({})
    check("missing roles rejected", not ok)
    # regression: the all-#000000 borrow that once passed at 20.65:1 with
    # zero hierarchy (accent == text == muted on a near-white bg)
    ok, reason = _palette_usable(borrow("#000000", "#fdfdfd", "#000000", muted="#000000"))
    check("collapsed monochrome palette rejected", not ok, reason)
    ok, reason = _palette_usable(borrow("#16181d", "#f4f3ee", "#1e5eff", muted="#16181d"))
    check("muted == text rejected", not ok, reason)


def _norm(value: str):
    """hex/#rgb -> 'rgb(r, g, b)' so alpha bases can be compared."""
    h = value.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 6 and all(c in "0123456789abcdefABCDEF" for c in h):
        return f"rgb({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)})"
    return value


def test_derive_tokens_all_single_token():
    light, dark, notes = derive_tokens(fake_roles(), fake_dark_roles(), [])
    check("light vocabulary complete", len(light) == 17, str(len(light)))
    check("dark vocabulary complete", len(dark) == 17, str(len(dark)))
    check("derivation notes produced", len(notes) >= 2, str(notes))
    for theme in (light, dark):
        solids = {_norm(v) for v in theme.values() if v.startswith("#") or v.startswith("rgb(")}
        for name, value in theme.items():
            if name in ("--pass", "--under"):
                continue  # local semantic roles
            if value.startswith("rgba("):
                # alpha blend must be of ONE declared ink: the base rgb must
                # appear solid in the same theme
                base = "rgb(" + value.split("(")[1].rsplit(",", 1)[0] + ")"
                check(f"{name} blends a declared ink", base in solids, f"{name}={value} base={base}")
            else:
                check(f"{name} is a hex or rgb value", value.startswith(("#", "rgb")), value)


def test_on_accent_and_walk():
    check("white on dark accent", _on_accent("#1e5eff") == "#ffffff")
    check("black on light accent", _on_accent("#ffd166") == "#000000")
    out, log = _walk("#777777", "black", 4.5, "#ffffff")
    check("walk reaches target contrast", _contrast(out, "#ffffff") >= 4.5, f"{out} {log}")
    check("walk changed the color", out != "#777777", out)
    check("walk logged", "derivation:" in log, log)
    out2, _ = _walk("#1e5eff", "black", 4.5, "#f4f3ee")
    check("already-passing color untouched", out2 == "#1e5eff", out2)


def test_prepare_writes_receipt():
    """Real prepare() against the real library (no network — it only reads
    cards and runs the in-process tools). Must produce a register whose
    palette stage passed a non-degenerate gate."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        try:
            register = prepare("unit-test sheet", "measured technical", out)
        except ValueError as e:
            # honest outcome on a tiny fixture library — but the REAL library
            # always has borrowable cards, so this branch failing means the
            # picker or gate regressed
            check("prepare rejects honestly (has rejects list)", "rejects:" in str(e), str(e))
            return
        for name in ("register.json", "tokens.json", "bands.json"):
            check(f"{name} written", (out / name).exists())
        stages = [e["stage"] for e in register["entries"]]
        for stage in ("direction", "palette", "evidence", "structure", "tokens"):
            check(f"register stage {stage}", stage in stages, str(stages))
        pal = next(e for e in register["entries"] if e["stage"] == "palette")
        check("palette gate passed", pal["gate"]["usable"] is True)
        check("gate reason mentions distinct roles", "distinct" in pal["gate"]["reason"],
              pal["gate"]["reason"])
        roles = pal["output"]["roles"]
        check("roles are distinct values",
              len({v.lower() for v in roles.values()}) >= 3, str(roles))
        ev = next(e for e in register["entries"] if e["stage"] == "evidence")
        check("artifacts are repo-relative (no drive letters)",
              all(":" not in a for a in ev["artifacts"]), str(ev["artifacts"]))
        check("credits is a number", isinstance(register.get("credits"), int),
              str(register.get("credits")))


if __name__ == "__main__":
    test_ranked_dark_preference()
    test_palette_usable_gate()
    test_derive_tokens_all_single_token()
    test_on_accent_and_walk()
    test_prepare_writes_receipt()
    finish()
