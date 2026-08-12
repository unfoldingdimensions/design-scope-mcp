"""Shared test harness — the check/report plumbing every suite duplicated.

Also forces UTF-8 on stdout. Without it the suites die mid-run on a Windows
console (cp1252) the moment a check name contains a character outside the
codepage, e.g. the "→" in "radius 4px → soft": UnicodeEncodeError aborts the
process before the remaining checks run, and the suite exits 1 with no
indication that it was an encoding problem rather than a real failure.

Usage:
    from _harness import check, finish
    check("name", condition, "optional detail")
    finish()      # prints the summary and exits 0/1
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

from _console import utf8_stdout  # noqa: E402 - one implementation, shared with the CLIs

utf8_stdout()

FAILS: list[str] = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  [{detail}]" if detail else ""))
    if not ok:
        FAILS.append(name)
    return bool(ok)


def finish():
    """Print the summary and exit — 1 if anything failed, else 0."""
    print()
    if FAILS:
        print(f"FAILED: {len(FAILS)} check(s): {FAILS}")
        sys.exit(1)
    print("ALL PASS")
    sys.exit(0)
