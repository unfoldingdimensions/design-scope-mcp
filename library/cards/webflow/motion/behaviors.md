# Behavior report

- **URL:** https://webflow.com
- **Captured:** 2026-08-09T16:48:19+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 322,
  "tabs": 62,
  "accordions": 201,
  "carousels": 37,
  "observers": 6,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 2
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - boxShadow: `rgba(0, 0, 0, 0) 0px 0px 0px 100px inset` → `rgba(0, 0, 0, 0.15) 0px 0px 0px 100px inset`
  - outline: `rgb(255, 255, 255) none 3px` → `rgb(255, 255, 255) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - outline: `rgb(8, 8, 8) none 3px` → `rgb(8, 8, 8) none 0px`
- `button` (hover-before-03.png → hover-after-03.png)
  - color: `rgb(8, 8, 8)` → `color(srgb 0.0745341 0.399346 0.886564)`
  - borderColor: `rgb(8, 8, 8) rgb(8, 8, 8) rgba(0, 0, 0, 0)` → `color(srgb 0.0745341 0.399346 0.886564) color(srgb 0.0745341 0.399346 0.886564) rgba(0, 0, 0, 0)`
  - outline: `rgb(8, 8, 8) none 3px` → `color(srgb 0.0745341 0.399346 0.886564) none 3px`
- `[role=button]` (hover-before-04.png → hover-after-04.png)
  - color: `rgb(8, 8, 8)` → `color(srgb 0.0745341 0.399346 0.886564)`
  - borderColor: `rgb(8, 8, 8) rgb(8, 8, 8) rgba(0, 0, 0, 0)` → `color(srgb 0.0745341 0.399346 0.886564) color(srgb 0.0745341 0.399346 0.886564) rgba(0, 0, 0, 0)`
  - outline: `rgb(8, 8, 8) none 3px` → `color(srgb 0.0745341 0.399346 0.886564) none 3px`

## State inventory
- `img.g-modal-image-img cc-tablet` text='' selected=None expanded=None
- `div.pill cc-category` text='New' selected=None expanded=None
- `div.pill cc-category` text='2.0' selected=None expanded=None
- `div.pill cc-category` text='2.0' selected=None expanded=None
- `summary.mm-summary` text='“@audienceType”: “Marketer”' selected=None expanded=None
- `p.machine-mode-text cc-tab-1` text='"name": "Build",“description”: “Bring team members and AI ag' selected=None expanded=None
- `p.machine-mode-text cc-tab-1` text='"name": "Publish",“description”: “Create and manage content ' selected=None expanded=None
- `p.machine-mode-text cc-tab-1` text='"name": "Optimize",“description”: “Turn every page into a re' selected=None expanded=None