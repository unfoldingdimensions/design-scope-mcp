"""Resolver tests for skill scripts (compare.py/theme.py).

Guards the resolution contract: DESIGN_SCOPE_SKILL_SCRIPTS env wins, then
installed skill locations, then the repo's vendored scripts/ (which always
exists in a checkout — so card_compare/theme_borrow work out of the box).
"""
import importlib
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))
import mcp_server  # noqa: E402

REPO_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _mask_hermes_locations(tmp_home: Path, monkeypatch=None):
    """Neutralize env so only the repo scripts/ fallback can resolve."""
    old = {
        "DESIGN_SCOPE_SKILL_SCRIPTS": os.environ.pop("DESIGN_SCOPE_SKILL_SCRIPTS", None),
        "HERMES_HOME": os.environ.pop("HERMES_HOME", None),
        "LOCALAPPDATA": os.environ.pop("LOCALAPPDATA", None),
        "USERPROFILE": os.environ.get("USERPROFILE"),
        "HOME": os.environ.get("HOME"),
    }
    os.environ["USERPROFILE"] = str(tmp_home)
    os.environ["HOME"] = str(tmp_home)
    if monkeypatch is not None:
        monkeypatch.setattr(mcp_server.Path, "home", staticmethod(lambda: tmp_home))
    return old


def _restore(old: dict):
    for k, v in old.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_env_override_wins():
    with tempfile.TemporaryDirectory() as td:
        old = _mask_hermes_locations(Path(td))
        try:
            os.environ["DESIGN_SCOPE_SKILL_SCRIPTS"] = td
            assert str(mcp_server._resolve_skill_scripts()) == td
        finally:
            _restore(old)


def test_falls_back_to_repo_scripts(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        old = _mask_hermes_locations(Path(td), monkeypatch)
        try:
            resolved = mcp_server._resolve_skill_scripts()
            assert resolved == REPO_SCRIPTS, f"got {resolved}"
            assert resolved.is_dir()
            assert (resolved / "compare.py").is_file()
            assert (resolved / "theme.py").is_file()
        finally:
            _restore(old)


def test_default_resolution_always_exists():
    # On any machine (skill installed or not) the resolver must land on
    # something real — the repo ships scripts/.
    resolved = mcp_server._resolve_skill_scripts()
    assert resolved.is_dir(), f"no scripts found: {resolved}"


def test_vendored_copies_are_runnable():
    import runpy
    import subprocess

    for name in ("compare.py", "theme.py"):
        p = REPO_SCRIPTS / name
        r = subprocess.run(
            [sys.executable, str(p), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{name} --help failed: {r.stderr[:200]}"
    runpy.run_path(str(REPO_SCRIPTS / "compare.py"))
    runpy.run_path(str(REPO_SCRIPTS / "theme.py"))


def test_imports_are_stdlib_only():
    import ast

    for name in ("compare.py", "theme.py"):
        tree = ast.parse((REPO_SCRIPTS / name).read_text(encoding="utf-8"))
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert imports <= {"argparse", "json", "os", "sys", "pathlib", "re",
                           "datetime", "colorsys"}, f"{name} imports non-stdlib: {imports}"


def test_theme_hex_of_parses_all_token_forms():
    """Regression: 8-digit hex (#000000e6) from real token dumps used to fall
    through to the 'any token' fallback and collapse whole palettes."""
    sys.path.insert(0, str(REPO_SCRIPTS))
    import theme

    assert theme._hex_of("#fff") == "#ffffff"
    assert theme._hex_of("#FDFDFD") == "#fdfdfd"
    assert theme._hex_of("#000000e6") == "#000000"  # alpha stripped
    assert theme._hex_of("rgb(1, 2, 3)") == "#010203"
    assert theme._hex_of("var(--x)") is None
    assert theme._hex_of("") is None


def test_theme_library_default_is_portable():
    """The default must resolve to a real library on any checkout (regression:
    both scripts hardcoded E:\\...\\library and broke every other machine)."""
    sys.path.insert(0, str(REPO_SCRIPTS))
    import compare
    import theme

    for mod in (compare, theme):
        assert (mod.GLOBAL_LIBRARY / "index.json").exists(), \
            f"{mod.__name__}: library default resolves to nothing: {mod.GLOBAL_LIBRARY}"
    assert theme._default_library() == (REPO_SCRIPTS.parent / "library").resolve() or \
           "DESIGN_SCOPE_LIBRARY" in os.environ


def test_theme_dark_roles_not_dropped():
    """Regression: dark roles were skipped unless the light vocabulary's token
    also existed in the dark one — cards shipped with dark_roles = {bg}."""
    sys.path.insert(0, str(REPO_SCRIPTS))
    import theme

    # a card whose dark vocabulary uses different token names than light
    sem = {
        "semantic_colors": {
            "light": {"--bg": "#fdfdfd", "--text": "#16181d", "--primary": "#1e5eff"},
            "dark": {"--bg": "#0f1015", "--foreground": "#e7e9ed", "--brand": "#6e9bff"},
        }
    }
    import json as _json
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        card = Path(td) / "cards" / "fixture"
        card.mkdir(parents=True)
        (card / "semantic.json").write_text(_json.dumps(sem), encoding="utf-8")
        old = theme.GLOBAL_LIBRARY
        theme.GLOBAL_LIBRARY = Path(td)
        try:
            out = theme.borrow_theme("fixture", td)
            dr = out["dark_roles"]
            assert "bg" in dr and "text" in dr and "primary" in dr, f"dark roles dropped: {dr}"
            assert dr["text"]["value"] == "#e7e9ed"
            assert dr["primary"]["value"] == "#6e9bff"
        finally:
            theme.GLOBAL_LIBRARY = old
