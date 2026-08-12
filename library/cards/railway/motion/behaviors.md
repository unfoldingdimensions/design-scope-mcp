# Behavior report

- **URL:** https://railway.com
- **Captured:** 2026-08-10T07:11:16+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 70,
  "tabs": 6,
  "accordions": 0,
  "carousels": 0,
  "observers": 8,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(220, 220, 224)` → `rgb(242, 241, 243)`
  - outline: `rgb(220, 220, 224) none 3px` → `rgb(242, 241, 243) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(255, 255, 255, 0.05)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(28, 26, 40)`

## State inventory
- `button.relative overflow-hidden rounded-lg min-w-fit focus:outline-none focus-visible:r` text='Deploy' selected=true expanded=None
- `button.relative overflow-hidden rounded-lg min-w-fit focus:outline-none focus-visible:r` text='Network' selected=false expanded=None
- `button.relative overflow-hidden rounded-lg min-w-fit focus:outline-none focus-visible:r` text='Scale' selected=false expanded=None
- `button.relative overflow-hidden rounded-lg min-w-fit focus:outline-none focus-visible:r` text='Monitor' selected=false expanded=None
- `button.relative overflow-hidden rounded-lg min-w-fit focus:outline-none focus-visible:r` text='Evolve' selected=false expanded=None