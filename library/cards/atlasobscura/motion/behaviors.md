# Behavior report

- **URL:** https://www.atlasobscura.com
- **Captured:** 2026-08-10T15:23:29+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 410,
  "tabs": 6,
  "accordions": 5,
  "carousels": 10,
  "observers": 91,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `button` (hover-before-01.png → hover-after-01.png)
  - borderColor: `rgb(215, 212, 208)` → `rgb(215, 212, 208) rgb(215, 212, 208) rgba(0, 0, 0, 0)`
- `button` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(0, 0, 0)` → `rgb(161, 106, 58)`
  - outline: `rgb(0, 0, 0) none 3px` → `rgb(161, 106, 58) none 3px`
- `[role=button]` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgb(255, 255, 255)` → `rgb(245, 244, 244)`
- `[role=button]` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgb(255, 255, 255)` → `rgb(245, 244, 244)`
- `[role=button]` (hover-before-05.png → hover-after-05.png)
  - backgroundColor: `rgb(255, 255, 255)` → `rgb(245, 244, 244)`
- `[role=button]` (hover-before-06.png → hover-after-06.png)
  - backgroundColor: `rgb(255, 255, 255)` → `rgb(245, 244, 244)`

## State inventory
- `sl-tab-group.aon-sl-filter-tab-group` text='Featured\n      \n      \n        Most Recent\n      \n      \n   ' selected=None expanded=None
- `sl-tab.aon-sl-filter-tab` text='Featured' selected=true expanded=None
- `sl-tab.aon-sl-filter-tab` text='Most Recent' selected=false expanded=None
- `button.splide__arrow splide__arrow--prev lg:top-20 xl:top-24 2xl:top-28 lg:left-6 xl:le` text='' selected=None expanded=None
- `button.splide__arrow splide__arrow--next lg:top-20 xl:top-24 2xl:top-28 lg:right-6 xl:r` text='' selected=None expanded=None
- `button.aon-toggle-button activity-button btn-aon has-done inactive` text='Been Here?' selected=None expanded=None
- `button.aon-toggle-button activity-button btn-aon wants-to inactive` text='Want to Visit?' selected=None expanded=None
- `button.aon-toggle-button activity-button list-button btn-aon in-list inactive` text='Add to List' selected=None expanded=None