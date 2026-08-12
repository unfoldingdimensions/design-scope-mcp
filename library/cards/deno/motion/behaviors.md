# Behavior report

- **URL:** https://deno.com
- **Captured:** 2026-08-10T07:37:48+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 228,
  "tabs": 31,
  "accordions": 0,
  "carousels": 0,
  "observers": 100,
  "scrollSnap": 4,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(23, 39, 35)` → `rgb(112, 255, 175)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(23, 39, 35)`
  - outline: `rgb(23, 39, 35) none 3px` → `rgb(112, 255, 175) none 3px`
- `button` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(225, 236, 242)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(225, 236, 242)`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(225, 236, 242)`

## State inventory
- `button.first:border-r border-gray-200 border-b grow px-4 py-1.5 font-mono text-xs curso` text='MacOS/Linux' selected=false expanded=None
- `button.first:border-r border-gray-200 border-b grow px-4 py-1.5 font-mono text-xs curso` text='Windows(Currently selected)' selected=true expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno task' selected=true expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno serve' selected=false expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno fmt' selected=false expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno lint' selected=false expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno test' selected=false expanded=None
- `button.font-mono whitespace-nowrap text-sm px-3 py-3 transition-colors cursor-pointer t` text='deno bench' selected=false expanded=None