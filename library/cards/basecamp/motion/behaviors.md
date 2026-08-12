# Behavior report

- **URL:** https://basecamp.com
- **Captured:** 2026-08-10T09:37:10+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 94,
  "tabs": 3,
  "accordions": 0,
  "carousels": 0,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklch(0.3209 0.0204 233.83 / 0.08)`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `oklch(0.5687 0.1602 254.08)` → `oklch(0.5087 0.1602 254.08)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `oklch(0.5687 0.1602 254.08)` → `oklch(0.5087 0.1602 254.08)`

## State inventory
- `button.project__tool project__tool--card-table` text='' selected=None expanded=None
- `figure.project__view project__view--card-table` text='' selected=None expanded=None
- `figure.project__page project__page--card-table` text='' selected=None expanded=None