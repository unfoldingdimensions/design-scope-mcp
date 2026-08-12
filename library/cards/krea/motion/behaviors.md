# Behavior report

- **URL:** https://www.krea.ai
- **Captured:** 2026-08-10T08:20:30+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 202,
  "tabs": 3,
  "accordions": 0,
  "carousels": 11,
  "observers": 6,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 9
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `oklch(0.579 0.2497 257.07)` → `oklch(0.5515 0.2497 257.07)`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.999994 0.0000455678 0.0000200868 / 0.1)`
- `a[href]` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.999994 0.0000455678 0.0000200868 / 0.1)`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.999994 0.0000455678 0.0000200868 / 0.1)`
- `button` (hover-before-05.png → hover-after-05.png)
  - backgroundColor: `rgb(255, 255, 255)` → `rgb(245, 245, 245)`
- `button` (hover-before-06.png → hover-after-06.png)
  - backgroundColor: `rgb(38, 38, 38)` → `rgb(32, 32, 32)`

## State inventory
- `button.relative flex items-center gap-2 px-6 py-2 font-sans text-base leading-[120%] fo` text='Monthly' selected=true expanded=None
- `button.relative flex items-center gap-2 px-6 py-2 font-sans text-base leading-[120%] fo` text='Yearly -40% off' selected=false expanded=None