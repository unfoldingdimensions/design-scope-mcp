# Behavior report

- **URL:** https://astro.build
- **Captured:** 2026-08-10T07:24:10+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 151,
  "tabs": 13,
  "accordions": 12,
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
  - color: `rgb(191, 193, 201)` → `rgb(255, 255, 255)`
  - outline: `rgb(191, 193, 201) none 3px` → `rgb(255, 255, 255) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(191, 193, 201)` → `rgb(255, 255, 255)`
  - outline: `rgb(191, 193, 201) none 3px` → `rgb(255, 255, 255) none 3px`
- `button` (hover-before-03.png → hover-after-03.png)
  - color: `rgb(191, 193, 201)` → `rgb(242, 246, 250)`
  - outline: `rgb(191, 193, 201) none 3px` → `rgb(242, 246, 250) none 3px`

## State inventory
- `button.integration-tab group relative flex flex-col items-center gap-3 whitespace-nowra` text='React' selected=true expanded=None
- `button.integration-tab group relative flex flex-col items-center gap-3 whitespace-nowra` text='Vue' selected=false expanded=None
- `button.integration-tab group relative flex flex-col items-center gap-3 whitespace-nowra` text='Preact' selected=false expanded=None
- `button.integration-tab group relative flex flex-col items-center gap-3 whitespace-nowra` text='Svelte' selected=false expanded=None
- `button.integration-tab group relative flex flex-col items-center gap-3 whitespace-nowra` text='Solid' selected=false expanded=None
- `button.ecosystem-tab px-6 py-2 group size-fit inline-flex items-center rounded-full bg-` text='Trending' selected=true expanded=None
- `button.ecosystem-tab px-6 py-2 group size-fit inline-flex items-center rounded-full bg-` text='E-Commerce' selected=false expanded=None
- `button.ecosystem-tab px-6 py-2 group size-fit inline-flex items-center rounded-full bg-` text='Blogs' selected=false expanded=None