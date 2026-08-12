# Behavior report

- **URL:** https://postmarkapp.com
- **Captured:** 2026-08-10T10:26:56+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 229,
  "tabs": 26,
  "accordions": 4,
  "carousels": 2,
  "observers": 2,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(255, 255, 255, 0.2)`
  - boxShadow: `rgba(255, 255, 255, 0.2) 0px 0px 0px 1px inset` → `rgba(255, 255, 255, 0.4) 0px 0px 0px 1px inset`
  - outline: `rgb(255, 255, 255) none 3px` → `rgb(255, 255, 255) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(0, 123, 200)` → `rgb(0, 0, 0)`
  - borderColor: `rgb(0, 123, 200)` → `rgb(0, 0, 0)`
  - outline: `rgb(0, 123, 200) none 3px` → `rgb(0, 0, 0) none 0px`

## State inventory
- `nav.tabbed-nav tabbed-nav--libs home-snippets_nav` text='More' selected=None expanded=None
- `ul.tabbed-nav_list` text='More' selected=None expanded=None
- `li.tabbed-nav_item tabbed-nav_item--current` text='' selected=None expanded=None
- `a.tabbed-nav_link` text='' selected=None expanded=None
- `li.tabbed-nav_item` text='' selected=None expanded=None
- `a.tabbed-nav_link` text='' selected=None expanded=None
- `li.tabbed-nav_item` text='' selected=None expanded=None
- `a.tabbed-nav_link` text='' selected=None expanded=None