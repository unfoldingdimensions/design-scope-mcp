# Behavior report

- **URL:** https://www.netflix.com
- **Captured:** 2026-08-10T05:02:59+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 66,
  "tabs": 9,
  "accordions": 0,
  "carousels": 0,
  "observers": 2,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgb(229, 9, 20)` → `rgb(193, 17, 25)`
  - borderColor: `rgb(255, 255, 255)` → `rgb(0, 0, 0)`
  - outline: `rgb(255, 255, 255) none 3px` → `rgb(255, 255, 255) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - outline: `rgba(255, 255, 255, 0.7) none 3px` → `rgba(255, 255, 255, 0.7) none 0px`
- `a[href]` (hover-before-03.png → hover-after-03.png)
  - outline: `rgba(255, 255, 255, 0.7) none 3px` → `rgba(255, 255, 255, 0.7) none 0px`
- `a[href]` (hover-before-04.png → hover-after-04.png)
  - outline: `rgba(255, 255, 255, 0.7) none 3px` → `rgba(255, 255, 255, 0.7) none 0px`
- `button` (hover-before-05.png → hover-after-05.png)
  - backgroundColor: `rgb(229, 9, 20)` → `rgb(193, 17, 25)`
  - borderColor: `rgb(255, 255, 255)` → `rgb(0, 0, 0)`

## State inventory
- `div.ot-sdk-four ot-sdk-columns ot-tab-list` text='Privacy Preference CenterGeneral DescriptionEssential Cookie' selected=None expanded=None
- `li.ot-abt-tab` text='General Description' selected=None expanded=None
- `div.ot-active-menu category-menu-switch-handler` text='General Description' selected=true expanded=None
- `div.category-menu-switch-handler` text='Essential Cookies' selected=false expanded=None
- `div.category-menu-switch-handler` text='First Party Performance and Functionality Cookies' selected=false expanded=None
- `div.category-menu-switch-handler` text='Third Party Performance and Functionality Cookies' selected=false expanded=None
- `div.category-menu-switch-handler` text='Advertising Cookies' selected=false expanded=None
- `div.ot-tab-desc ot-sdk-eight ot-sdk-columns` text='General DescriptionThis cookie tool will help you understand' selected=None expanded=None