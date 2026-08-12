# Behavior report

- **URL:** https://brilliant.org
- **Captured:** 2026-08-10T16:38:20+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 83,
  "tabs": 5,
  "accordions": 4,
  "carousels": 0,
  "observers": 2,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `nav.panda-ai_center`
  - boxShadow: none → rgba(0, 0, 0, 0.1) 0px 0px 15px 0px

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - borderColor: `rgb(255, 255, 255) rgb(255, 255, 255) rgba(0, 0, 0, 0)` → `rgb(69, 109, 255)`
- `button` (hover-before-02.png → hover-after-02.png)
  - borderColor: `rgba(0, 0, 0, 0.1)` → `rgba(0, 0, 0, 0.3)`
- `button` (hover-before-03.png → hover-after-03.png)
  - opacity: `1` → `0.78`

## State inventory
- `button.panda-ai_center panda-bg_bg.primary panda-bd_none panda-bdr_full panda-c_text.te` text='MathMath' selected=true expanded=None
- `button.panda-ai_center panda-bg_bg.primary panda-bd_none panda-bdr_full panda-c_text.te` text='Computer ScienceCS' selected=false expanded=None
- `button.panda-ai_center panda-bg_bg.primary panda-bd_none panda-bdr_full panda-c_text.te` text='ScienceScience' selected=false expanded=None
- `button.panda-ai_center panda-bg_bg.primary panda-bd_none panda-bdr_full panda-c_text.te` text='Data AnalysisData' selected=false expanded=None