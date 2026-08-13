"""design-scope MCP smoke test — real stdio transport via the mcp SDK.

Usage:
  python tests/client_smoke.py           # full smoke (all tools + errors)
  python tests/client_smoke.py --queue   # in-process queue mock only (no server)

Exits 0 on success, 1 on any failed check.
"""
import asyncio
import json
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from _harness import FAILS, check, finish  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SERVER = [sys.executable, str(REPO / "library" / "mcp_server.py")]
DOGFOOD = str(REPO / "docs" / "dogfood-app")


async def call(s, tool, **kwargs):
    res = await s.call_tool(tool, kwargs)
    return json.loads(res.content[0].text)


async def smoke_transport():
    async with stdio_client(StdioServerParameters(command=SERVER[0], args=SERVER[1:])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            names = [t.name for t in tools.tools]
            check("10 tools registered", len(names) == 10 and "get_page_structure" in names, str(names))

            # read tools
            r1 = await call(s, "style_search", query="funky", top_n=3)
            check("style_search funky returns results", r1["count"] > 0 and r1["results"][0]["slug"])
            r2 = await call(s, "style_search", query="editorial but not brutalist", top_n=3)
            check("style_search exclusion works", r2["count"] > 0)
            r3 = await call(s, "style_filter", saturation="vibrant", max_results=3)
            check("style_filter structured", r3["count"] > 0)
            r4 = await call(s, "card_get", slug="stripe")
            check("card_get full card", r4["slug"] == "stripe" and r4["fingerprint"]
                  and r4["screenshot_desktop"].endswith(".png"))
            check("card_get annotation layer", r4.get("annotation")
                  and r4["annotation"].get("design_intent"))

            # analysis tools — compare.py/theme.py ship with the design-scope
            # skill, NOT with this repo, so on a clean clone these two tools
            # correctly return a structured error. Assert that contract instead
            # of failing the whole smoke run for a dependency we don't ship.
            r5 = await call(s, "card_compare", slug="stripe", project_dir=DOGFOOD)
            if "error" in r5 and "skill scripts not found" in r5["error"]:
                print("SKIP  card_compare — skill scripts absent (set DESIGN_SCOPE_SKILL_SCRIPTS)")
                check("card_compare degrades with a hint", bool(r5.get("hint")))
            else:
                check("card_compare borrow list", "colors_lacking" in r5)
            r6 = await call(s, "theme_borrow", slug="anthropic", target_dir=DOGFOOD)
            if "error" in r6 and "skill scripts not found" in r6["error"]:
                print("SKIP  theme_borrow — skill scripts absent (set DESIGN_SCOPE_SKILL_SCRIPTS)")
                check("theme_borrow degrades with a hint", bool(r6.get("hint")))
            else:
                check("theme_borrow remap+guard", r6["roles"].get("bg") and r6["notes"])

            # history
            r7 = await call(s, "recommend_history", project_dir=DOGFOOD)
            check("recommend_history chain", r7.get("current_iteration") is not None
                  and r7.get("name") == "Pulse (dogfood)", str(r7.get("name")))

            # capture error paths (no real capture in smoke)
            r8 = await call(s, "capture", url="not-a-url", name="x")
            check("capture bad url rejected", "error" in r8)
            r9 = await call(s, "capture_status", job_id="nope")
            check("capture_status unknown job", "error" in r9)

            # security paths
            r10 = await call(s, "card_get", slug="../../etc/passwd")
            check("path traversal rejected", "error" in r10)
            r11 = await call(s, "card_get", slug="doesnotexist")
            check("missing card error", "error" in r11)
            r12 = await call(s, "recommend_history", project_dir=r"C:\nonexistent")
            check("missing manifest error", "error" in r12)


def queue_mock():
    """In-process queue mechanics with a fake capture (no network).

    IMPORTANT: never writes into the real library — the fake capture_one
    returns ok WITHOUT creating files, and the index is a temp dict. (The
    first version wrote cards/test-site into the real library; that bug is
    why this mock creates nothing.)
    """
    sys.path.insert(0, str(REPO / "library"))
    import mcp_server as ms
    import capture as cap

    captured_sites = []

    def fake_capture_one(site, slug, card_dir, browser, opts):
        # deliberately NO filesystem writes — mocks must not touch the library
        captured_sites.append(site)
        return {"ok": True, "slug": slug, "captured_at": "2026-08-11T00:00:00Z",
                "screenshots": {"desktop": "screenshot-desktop.png"}}

    cap.capture_one = fake_capture_one
    cap.slugify = lambda n: n.lower().replace(" ", "-")
    fake_index = {"cards": {}}
    cap.load_index = lambda: fake_index
    cap.save_index = lambda ix: None

    def wait(job_id, want, timeout=15.0):
        # poll instead of fixed sleep — a cold playwright import can exceed 1.5s
        t0 = time.time()
        st = {}
        while time.time() - t0 < timeout:
            st = json.loads(ms.capture_status(job_id))
            if st["status"] in (want, "failed"):
                return st
            time.sleep(0.2)
        return st

    r = json.loads(ms.capture(url="https://example.com", name="Test Site"))
    st = wait(r["job_id"], "done")
    check("queue: job transitions to done", st["status"] == "done", st["status"])
    check("queue: slug derived", st.get("slug") == "test-site", str(st.get("slug")))
    entry = fake_index["cards"].get("test-site", {})
    check("queue: full index entry shape",
          entry.get("files", {}).get("desktop") == "cards/test-site/screenshot-desktop.png"
          and "fingerprint_summary" in entry, json.dumps(entry)[:120])
    check("queue: category+why reach card writer",
          captured_sites and captured_sites[0].get("category") == "misc"
          and "why" in captured_sites[0], str(captured_sites[:1]))

    r2 = json.loads(ms.capture(url="https://example.com", name="Test Site"))
    st2 = wait(r2["job_id"], "failed")
    check("queue: duplicate slug fails", st2["status"] == "failed"
          and "already exists" in st2.get("error", ""), st2.get("status"))

    r3 = json.loads(ms.capture(url="https://example.com", name="Bad", slug="---"))
    check("queue: dangling-dash slug rejected", "error" in r3, str(r3))


if __name__ == "__main__":
    if "--queue" in sys.argv:
        queue_mock()
    else:
        asyncio.run(smoke_transport())
    finish()
