# Behavior report

- **URL:** https://mercury.com
- **Captured:** 2026-08-09T17:03:05+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 207,
  "tabs": 25,
  "accordions": 28,
  "carousels": 0,
  "observers": 35,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `nav.center`
  - boxShadow: none → rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(86, 86, 118, 0.1) 0px 0px 6px 0px
  - background: rgba(0, 0, 0, 0) → rgb(23, 23, 33)
  - backdropFilter: none → blur(10px)
- `div.relative`
  - background: color(srgb 0.0901961 0.0901961 0.129412 / 0.01) → rgb(23, 23, 33)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(237, 237, 243)` → `rgb(195, 195, 204)`
  - borderColor: `rgb(237, 237, 243)` → `rgb(195, 195, 204)`
  - outline: `rgb(237, 237, 243) none 3px` → `rgb(195, 195, 204) none 3px`
- `button` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(156, 180, 232, 0.28)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(156, 180, 232, 0.28)`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(156, 180, 232, 0.28)`

## State inventory
- `div.group/content col-span-full col-start-1 row-start-1 data-[state=inactive]:pointe` text='SaaSUnlike most financial institutions, Mercury is built on ' selected=None expanded=None
- `div.col-span-full col-start-1 row-start-1 -m-gap-lg transition-transform duration-0 ` text='' selected=None expanded=None
- `div.pointer-events-none col-start-1 row-start-1 flex flex-col gap-stack-gap-lg relat` text='SaaSUnlike most financial institutions, Mercury is built on ' selected=None expanded=None
- `div.group/content col-span-full col-start-1 row-start-1 data-[state=inactive]:pointe` text='EcommerceBuilding an ecommerce brand with millions of custom' selected=None expanded=None
- `div.col-span-full col-start-1 row-start-1 -m-gap-lg transition-transform duration-0 ` text='' selected=None expanded=None
- `div.pointer-events-none col-start-1 row-start-1 flex flex-col gap-stack-gap-lg relat` text='EcommerceBuilding an ecommerce brand with millions of custom' selected=None expanded=None
- `div.group/content col-span-full col-start-1 row-start-1 data-[state=inactive]:pointe` text='AgencyWe love Mercury’s interface. Built-in permissions mean' selected=None expanded=None
- `div.col-span-full col-start-1 row-start-1 -m-gap-lg transition-transform duration-0 ` text='' selected=None expanded=None