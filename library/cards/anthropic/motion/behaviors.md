# Behavior report

- **URL:** https://www.anthropic.com
- **Captured:** 2026-08-10T04:18:06+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 200,
  "tabs": 2,
  "accordions": 0,
  "carousels": 3,
  "observers": 19,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(20, 20, 19)` → `rgb(94, 93, 89)`
  - borderColor: `rgb(20, 20, 19)` → `rgb(94, 93, 89)`
  - outline: `rgb(20, 20, 19) none 2px` → `rgb(94, 93, 89) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - outline: `rgb(20, 20, 19) none 2px` → `rgb(20, 20, 19) none 0px`
  - textDecoration: `underline rgba(0, 0, 0, 0)` → `underline rgb(20, 20, 19)`
- `[role=button]` (hover-before-03.png → hover-after-03.png)
  - textDecoration: `underline rgba(0, 0, 0, 0)` → `underline rgb(20, 20, 19)`
- `[role=button]` (hover-before-04.png → hover-after-04.png)
  - textDecoration: `underline rgba(0, 0, 0, 0)` → `underline rgb(20, 20, 19)`
- `[role=button]` (hover-before-05.png → hover-after-05.png)
  - textDecoration: `underline rgba(0, 0, 0, 0)` → `underline rgb(20, 20, 19)`

## State inventory
- `div.home_hero_grid u-grid-tablet` text='AI research and products that put safety at the frontierAI r' selected=None expanded=None
- `div.footer_bottom_contain cc-tablet` text='© 2026 Anthropic PBC' selected=None expanded=None