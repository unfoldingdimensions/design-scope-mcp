"""design-scope behavior_pass diff tests — pure function, no browser.

The regression guard for the dropped-hover-effect bug: the probe omits 'none'
values, so hover effects that ADD a property (box-shadow, transform — the two
most common on the web) appear only in the `after` snapshot. Diffing over
`before` alone made them invisible; across the 201-card library that showed up
as boxShadow 12 and transform 9 against color 246.

Usage:
  python tests/test_behavior_pass.py

Exits 0 on success, 1 on any failed check.
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "library"))

from _harness import check, finish  # noqa: E402
from behavior_pass import (HOVER_PROBE_JS, classify_interaction_model,  # noqa: E402
                           diff_states, interaction_probe)


def test_added_property_is_caught():
    """THE regression: a property absent before hover, present after."""
    d = diff_states({"color": "rgb(0,0,0)"},
                    {"color": "rgb(0,0,0)", "boxShadow": "rgba(0,0,0,.2) 0 2px 8px"})
    check("hover-added boxShadow is reported", "boxShadow" in d, str(d))
    check("added property records before=None",
          d.get("boxShadow", {}).get("before") is None, str(d.get("boxShadow")))
    d2 = diff_states({}, {"transform": "matrix(1.05, 0, 0, 1.05, 0, 0)"})
    check("hover-added transform is reported", "transform" in d2, str(d2))


def test_removed_property_is_caught():
    d = diff_states({"textDecoration": "underline"}, {})
    check("hover-removed property is reported", "textDecoration" in d, str(d))
    check("removed property records after=None",
          d["textDecoration"]["after"] is None, str(d))


def test_changed_and_unchanged():
    d = diff_states({"color": "rgb(0,0,0)"}, {"color": "rgb(255,0,0)"})
    check("changed property reported", d == {"color": {"before": "rgb(0,0,0)",
                                                       "after": "rgb(255,0,0)"}}, str(d))
    check("identical snapshots diff empty",
          diff_states({"color": "red"}, {"color": "red"}) == {})
    check("both empty diffs empty", diff_states({}, {}) == {})


def test_outline_not_probed():
    """outline's computed value embeds currentColor, so it mirrors any color
    change — it was the most-reported 'behavior' in the library (252) and is
    pure noise. It must stay out of the probed property list."""
    check("outline is not a probed property", "'outline'" not in HOVER_PROBE_JS)
    for p in ("boxShadow", "transform", "backgroundColor"):
        check(f"{p} is still probed", f"'{p}'" in HOVER_PROBE_JS)


def test_probe_does_not_scroll():
    """scrollIntoView in the probe moved the element out from under the mouse
    before the 'after' screenshot was taken."""
    check("probe does not scroll the page", "scrollIntoView" not in HOVER_PROBE_JS)


def test_classify_interaction_model():
    check("scrollSnap → scroll-driven",
          classify_interaction_model({"scrollSnap": 2}) == "scroll-driven")
    check("observers → scroll-driven",
          classify_interaction_model({"observers": 1}) == "scroll-driven")
    check("smoothScroll → scroll-driven",
          classify_interaction_model({"smoothScroll": "smooth-scroll-lib"}) == "scroll-driven")
    check("tabs → click-driven",
          classify_interaction_model({"tabs": 3}) == "click-driven")
    check("clickables > 30 → click-driven",
          classify_interaction_model({"clickables": 31}) == "click-driven")
    check("clickables = 30 is NOT click-driven",
          classify_interaction_model({"clickables": 30}) == "static")
    check("empty → static", classify_interaction_model({}) == "static")


class FakeElement:
    def __init__(self, x=10, y=10, w=100, h=40):
        self._box = {"x": x, "y": y, "width": w, "height": h}
        self.hovered = False
        self.screenshots = []
        self.clicked = False

    def bounding_box(self):
        return self._box

    def hover(self):
        self.hovered = True

    def screenshot(self, path=None):
        self.screenshots.append(str(path))
        if path:
            Path(path).touch()  # the probe unlinks no-diff pngs — observable

    def click(self):
        self.clicked = True


class FakeMouse:
    def __init__(self, page):
        self.page = page

    def wheel(self, dx, dy):
        self.page.events.append(("wheel", dx, dy))


class FakePage:
    """Records the call sequence; canned probe responses. Hover snapshots are
    consumed per call: el1 before='{}' after=boxShadow-snap (DIFF), el2
    before='{}' after='{}' (no diff → pngs dropped)."""

    def __init__(self, elements=None, hover_snapshots=None):
        self.elements = elements or [FakeElement(), FakeElement()]
        self.events = []
        self.mouse = FakeMouse(self)
        self.hover_calls = 0
        self.hover_snapshots = list(hover_snapshots) if hover_snapshots else [
            "{}",
            '{"color":"rgb(0,0,0)","boxShadow":"rgba(0,0,0,.2) 0 2px 8px"}',
            "{}", "{}",
        ]

    def evaluate(self, script, arg=None):
        self.events.append(("evaluate", script[:40]))
        if "clickables" in script:  # INTERACTION_PROBE_JS
            return json.dumps({"clickables": 8, "tabs": 2, "accordions": 0,
                               "carousels": 0, "observers": 0, "scrollSnap": 0,
                               "smoothScroll": None, "marquees": 0})
        if "getBoundingClientRect" in script:  # SCROLL_PROBE_JS (identical twice)
            snap = [{"sel": "header.nav", "top": 0, "position": "sticky",
                     "boxShadow": "none", "background": "rgb(255,255,255)",
                     "backdropFilter": "none"}]
            return json.dumps(snap)
        if "ariaSelected" in script:  # STATES_PROBE_JS
            return json.dumps([{"idx": 0, "tag": "button", "classes": "tab",
                                "text": "Home", "ariaSelected": "true",
                                "ariaExpanded": None}])
        if arg is not None:  # HOVER_PROBE_JS
            snap = self.hover_snapshots[min(self.hover_calls, len(self.hover_snapshots) - 1)]
            self.hover_calls += 1
            return snap
        if "scrollTo" in script:
            return None
        return "{}"

    def query_selector_all(self, sel):
        return self.elements if sel in ("a[href]", "button") else []

    def query_selector(self, sel):
        return self.elements[0] if self.elements else None

    def wait_for_timeout(self, ms):
        self.events.append(("wait", ms))

    def go_back(self, wait_until="load"):
        self.events.append(("go_back", wait_until))


def test_interaction_probe_writes_reports():
    with tempfile.TemporaryDirectory() as tmp:
        card_dir = Path(tmp)
        page = FakePage()
        out = interaction_probe(page, card_dir, "https://example.com")

        check("probe ok", out.get("ok") is True, str(out.get("error")))
        check("classified string persisted",
              out.get("interaction_model") == "click-driven", str(out.get("interaction_model")))
        beh = json.loads((card_dir / "motion" / "behaviors.json").read_text(encoding="utf-8"))
        check("behaviors.json has classified string",
              beh["interaction_model"] == "click-driven" and beh["interaction_signals"]["clickables"] == 8)
        check("hover diff with ADDED property (before=None)",
              out.get("hover_diffs", 0) >= 1 and any(
                  "boxShadow" in h["diffs"] and h["diffs"]["boxShadow"]["before"] is None
                  for h in beh["hover_diffs"]), str(beh["hover_diffs"][:1]))
        check("hover-inventory.json written",
              (card_dir / "motion" / "hover-inventory.json").exists())
        pngs = sorted(p.name for p in (card_dir / "motion").glob("hover-*.png"))
        check("no-diff element pngs dropped", len(pngs) == 2, str(pngs))
        gb = page.events.index(("go_back", "load"))
        check("go_back is the last interaction (only waits after it)",
              all(e[0] == "wait" for e in page.events[gb + 1:]), str(page.events[gb:]))


def test_interaction_probe_never_raises():
    class Boom:
        def evaluate(self, *a, **k):
            raise RuntimeError("boom")

        def __getattr__(self, name):
            raise RuntimeError("boom")

    with tempfile.TemporaryDirectory() as tmp:
        out = interaction_probe(Boom(), Path(tmp), "https://example.com")
        check("raising page → ok:False", out.get("ok") is False and out.get("error"))
        check("raising page → no artifacts",
              not (Path(tmp) / "motion" / "behaviors.json").exists())


if __name__ == "__main__":
    test_added_property_is_caught()
    test_removed_property_is_caught()
    test_changed_and_unchanged()
    test_outline_not_probed()
    test_probe_does_not_scroll()
    test_classify_interaction_model()
    test_interaction_probe_writes_reports()
    test_interaction_probe_never_raises()
    finish()
