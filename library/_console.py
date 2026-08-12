"""UTF-8 console output for the CLIs.

Every CLI in this package prints characters outside cp1252 — "→" in the search
results, "✓"/"✗" in the capture progress lines. On a Windows console (cp1252 by
default) writing one of those raises UnicodeEncodeError and kills the process
mid-run, so `python library/style_search.py "funky"` — the first command in the
README — died on the platform the README claims support for.

Call utf8_stdout() at the top of main(). errors="replace" keeps output flowing
even on a stream that still cannot represent a character.
"""
import sys


def utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):  # py3.7+, and not a plain file object
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001 - never let logging setup kill a run
                pass
