"""Resolver + vendored-script tests for compare.py / theme.py.

Usage:
  python tests/test_skill_scripts.py

Exits 0 on success, 1 on any failed check, like every other suite here. The
first version of this file was written pytest-style: running it as the README
documents imported the module, executed no assertion and exited 0, so the
coverage was imaginary (and it needed pytest, which requirements.txt does not
install). It now uses the shared _harness plumbing.

Contract under test: DESIGN_SCOPE_SKILL_SCRIPTS env wins, then an installed
skill location, then this repo's vendored scripts/ (which always exists in a
checkout — so card_compare/theme_borrow work out of the box).
"""
import ast
import contextlib
import importlib
import json
import os
import runpy
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "library"))

from _harness import check, finish  # noqa: E402
import mcp_server  # noqa: E402

REPO_SCRIPTS = REPO / "scripts"
STDLIB_ALLOWED = {"argparse", "json", "os", "sys", "pathlib", "re", "datetime", "colorsys"}
_MASKED_ENV = ("DESIGN_SCOPE_SKILL_SCRIPTS", "HERMES_HOME", "LOCALAPPDATA",
               "USERPROFILE", "HOME")


@contextlib.contextmanager
def isolated_home(tmp_home: Path):
    """Point HOME/USERPROFILE at tmp_home so only the repo fallback can resolve.

    Path.home() reads USERPROFILE on Windows and HOME elsewhere, so masking the
    environment is enough — no global monkeypatching of pathlib, no pytest.
    """
    saved = {k: os.environ.pop(k, None) for k in _MASKED_ENV}
    os.environ["USERPROFILE"] = str(tmp_home)
    os.environ["HOME"] = str(tmp_home)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_env_override_wins():
    with tempfile.TemporaryDirectory() as td, isolated_home(Path(td)):
        os.environ["DESIGN_SCOPE_SKILL_SCRIPTS"] = td
        resolved = mcp_server._resolve_skill_scripts()
        check("env override wins", str(resolved) == td, str(resolved))


def test_falls_back_to_repo_scripts():
    with tempfile.TemporaryDirectory() as td, isolated_home(Path(td)):
        resolved = mcp_server._resolve_skill_scripts()
        check("resolver falls back to the repo scripts/", resolved == REPO_SCRIPTS, str(resolved))
        check("repo fallback holds compare.py and theme.py",
              (resolved / "compare.py").is_file() and (resolved / "theme.py").is_file())


def test_default_resolution_always_exists():
    resolved = mcp_server._resolve_skill_scripts()
    check("default resolution lands on a real directory", resolved.is_dir(), str(resolved))


def test_vendored_copies_are_runnable():
    for name in ("compare.py", "theme.py"):
        # encoding: argparse output is ASCII today, but a --help that ever
        # printed a non-cp1252 character must not crash the suite on Windows
        r = subprocess.run([sys.executable, str(REPO_SCRIPTS / name), "--help"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=60)
        check(f"{name} --help exits 0", r.returncode == 0, r.stderr[:200])
    for name in ("compare.py", "theme.py"):
        try:
            runpy.run_path(str(REPO_SCRIPTS / name))
            check(f"{name} executes cleanly as a module", True)
        except SystemExit:
            check(f"{name} executes cleanly as a module", True, "argparse exited")
        except Exception as e:  # noqa: BLE001
            check(f"{name} executes cleanly as a module", False, f"{type(e).__name__}: {e}")


def test_default_library_is_portable():
    """Both scripts must resolve a real library on any checkout.

    Regression: both hardcoded E:\\...\\library and broke every other machine.
    """
    sys.path.insert(0, str(REPO_SCRIPTS))
    for mod_name in ("compare", "theme"):
        mod = importlib.import_module(mod_name)
        if os.environ.get("DESIGN_SCOPE_LIBRARY"):
            check(f"{mod_name}: library default is the env override",
                  str(mod.GLOBAL_LIBRARY) == str(Path(os.environ["DESIGN_SCOPE_LIBRARY"]).resolve()),
                  str(mod.GLOBAL_LIBRARY))
        else:
            check(f"{mod_name}: library default resolves to a real library",
                  (mod.GLOBAL_LIBRARY / "index.json").exists(), str(mod.GLOBAL_LIBRARY))


def test_imports_are_stdlib_only():
    for name in ("compare.py", "theme.py"):
        tree = ast.parse((REPO_SCRIPTS / name).read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        extra = sorted(imports - STDLIB_ALLOWED)
        check(f"{name} imports stdlib only", not extra, str(extra))


def theme_module():
    sys.path.insert(0, str(REPO_SCRIPTS))
    return importlib.import_module("theme")


def test_hex_of_parses_all_token_forms():
    """Regression: 8-digit hex (#000000e6) from real token dumps used to fall
    through to the 'any token' fallback and collapse whole palettes."""
    th = theme_module()
    for raw, want in (("#fff", "#ffffff"), ("#FDFDFD", "#fdfdfd"),
                      ("#000000e6", "#000000"), ("rgb(1, 2, 3)", "#010203"),
                      ("var(--x)", None), ("", None)):
        got = th._hex_of(raw)
        check(f"_hex_of({raw!r}) == {want!r}", got == want, str(got))


def _write_card(root: Path, slug: str, sem: dict) -> None:
    card = root / "cards" / slug
    card.mkdir(parents=True, exist_ok=True)
    (card / "semantic.json").write_text(json.dumps(sem), encoding="utf-8")


def test_dark_roles_not_dropped():
    """Regression: dark roles were skipped unless the light vocabulary's token
    also existed in the dark one — cards shipped with dark_roles = {bg}."""
    th = theme_module()
    sem = {"semantic_colors": {
        "light": {"--bg": "#fdfdfd", "--text": "#16181d", "--primary": "#1e5eff"},
        "dark": {"--bg": "#0f1015", "--foreground": "#e7e9ed", "--brand": "#6e9bff"},
    }}
    with tempfile.TemporaryDirectory() as td:
        _write_card(Path(td), "fixture", sem)
        old = th.GLOBAL_LIBRARY
        th.GLOBAL_LIBRARY = Path(td)
        try:
            dr = th.borrow_theme("fixture", td)["dark_roles"]
            check("dark role: bg/text/primary all survive",
                  {"bg", "text", "primary"} <= set(dr), str(sorted(dr)))
            check("dark text comes from the dark vocabulary",
                  dr.get("text", {}).get("value") == "#e7e9ed", str(dr.get("text")))
            check("dark primary comes from the dark vocabulary",
                  dr.get("primary", {}).get("value") == "#6e9bff", str(dr.get("primary")))
        finally:
            th.GLOBAL_LIBRARY = old


def test_vendor_tokens_are_not_borrowed():
    """Regression: cards/linear/semantic.json holds X's --tweet-* embed tokens,
    so borrowing "linear" returned the tweet palette as Linear's."""
    th = theme_module()
    vendor_only = {"semantic_colors": {"light": {
        "--tweet-bg-color": "#ffffff", "--tweet-color-blue-primary": "#1d9bf0"}}}
    mixed = {"semantic_colors": {"light": {
        "--tweet-bg-color": "#ffffff", "--tweet-color-blue-primary": "#1d9bf0",
        "--bg": "#101014", "--text": "#f5f5f5", "--accent": "#00d0a0"}}}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _write_card(root, "vendor-only", vendor_only)
        _write_card(root, "mixed", mixed)
        old = th.GLOBAL_LIBRARY
        th.GLOBAL_LIBRARY = root
        try:
            try:
                th.borrow_theme("vendor-only", td)
                check("a vendor-only card refuses to borrow instead of borrowing X's palette",
                      False, "returned a theme")
            except ValueError:
                check("a vendor-only card refuses to borrow instead of borrowing X's palette",
                      True)
            picked = [r["token"] for r in th.borrow_theme("mixed", td)["roles"].values()]
            check("no borrowed token comes from a vendor namespace",
                  not any(t.startswith("--tweet-") for t in picked), str(picked))
            check("the site's own tokens are still borrowed",
                  {"--bg", "--text", "--accent"} <= set(picked), str(picked))
        finally:
            th.GLOBAL_LIBRARY = old


def test_card_fingerprint_rescues_a_digit_named_palette():
    """Regression: 81 of 204 cards could not borrow at all.

    A page whose custom properties are all digit-named (--brand-500,
    --hds-space-core-200) yields an empty curated palette from semantic_pass,
    so theme_borrow raised "no color tokens usable for a theme". The card's own
    fingerprint.json already carries Dembrandt's measured semantic colors, so
    those cards now borrow with no recapture.
    """
    th = theme_module()
    # the real shape of the 74 cards: every custom property is digit-named, so
    # the curated no-digit palette is empty and the tokens sit in named_tokens
    sem = {"semantic_colors": {"light": {}, "dark": {}},
           "named_tokens": {"light": {"--brand-500": "#1e5eff"}, "dark": {}}}
    fp = {"colors": {"semantic": {"background": "rgb(255, 255, 255)",
                                  "text": "rgb(17, 17, 17)",
                                  "primary": "rgb(30, 94, 255)",
                                  "accent": "rgb(220, 5, 59)"}}}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        card = root / "cards" / "digit-named"
        card.mkdir(parents=True)
        (card / "semantic.json").write_text(json.dumps(sem), encoding="utf-8")
        (card / "fingerprint.json").write_text(json.dumps(fp), encoding="utf-8")
        old = th.GLOBAL_LIBRARY
        th.GLOBAL_LIBRARY = root
        try:
            picked = {k: v["token"] for k, v in th.borrow_theme("digit-named", td)["roles"].items()}
            check("digit-named palette borrows from the card's own fingerprint",
                  picked.get("bg") == "(card fingerprint bg)", str(picked))
            check("measured text/primary/accent are used",
                  picked.get("text") == "(card fingerprint text)"
                  and picked.get("primary") == "(card fingerprint primary)"
                  and picked.get("accent") == "(card fingerprint accent)", str(picked))
        finally:
            th.GLOBAL_LIBRARY = old


def test_named_tokens_still_win_over_the_card_fingerprint():
    """The fingerprint source is a last resort, not a preference.

    Preferring measured colors over named tokens changed the borrow output of
    116 of 204 cards (107 of them from a plausible-but-wrong pick such as a
    hyperlink colour standing in for the page background). Keeping it last
    fixed the 81 failures with zero change to the 123 that already worked.
    """
    th = theme_module()
    sem = {"semantic_colors": {"light": {"--bg": "#0f1015", "--text": "#f5f5f5",
                                        "--accent": "#00d0a0"}}}
    fp = {"colors": {"semantic": {"background": "rgb(255, 255, 255)",
                                  "text": "rgb(0, 0, 0)", "accent": "rgb(1, 2, 3)"}}}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        card = root / "cards" / "named"
        card.mkdir(parents=True)
        (card / "semantic.json").write_text(json.dumps(sem), encoding="utf-8")
        (card / "fingerprint.json").write_text(json.dumps(fp), encoding="utf-8")
        old = th.GLOBAL_LIBRARY
        th.GLOBAL_LIBRARY = root
        try:
            picked = {k: v["token"] for k, v in th.borrow_theme("named", td)["roles"].items()}
            check("named tokens still win over the card fingerprint",
                  picked.get("bg") == "--bg" and picked.get("text") == "--text"
                  and picked.get("accent") == "--accent", str(picked))
        finally:
            th.GLOBAL_LIBRARY = old


if __name__ == "__main__":
    test_env_override_wins()
    test_falls_back_to_repo_scripts()
    test_default_resolution_always_exists()
    test_vendored_copies_are_runnable()
    test_default_library_is_portable()
    test_imports_are_stdlib_only()
    test_hex_of_parses_all_token_forms()
    test_dark_roles_not_dropped()
    test_vendor_tokens_are_not_borrowed()
    test_card_fingerprint_rescues_a_digit_named_palette()
    test_named_tokens_still_win_over_the_card_fingerprint()
    finish()
