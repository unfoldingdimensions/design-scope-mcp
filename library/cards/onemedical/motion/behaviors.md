# Behavior report

- **URL:** https://www.onemedical.com
- **Captured:** 2026-08-10T15:52:54+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 139,
  "tabs": 20,
  "accordions": 0,
  "carousels": 0,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `nav.navigation`
  - position: absolute → fixed
  - boxShadow: none → rgba(0, 0, 0, 0.16) 0px 0px 8px 0px

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - outline: `rgb(6, 132, 102) none 3px` → `rgb(6, 132, 102) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - outline: `rgb(0, 0, 238) none 3px` → `rgb(0, 0, 238) none 0px`
- `button` (hover-before-03.png → hover-after-03.png)
  - color: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - borderColor: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - outline: `rgb(0, 77, 73) none 3px` → `rgb(6, 132, 102) none 3px`
- `button` (hover-before-04.png → hover-after-04.png)
  - color: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - borderColor: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - outline: `rgb(0, 77, 73) none 3px` → `rgb(6, 132, 102) none 3px`
- `button` (hover-before-05.png → hover-after-05.png)
  - color: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - borderColor: `rgb(0, 77, 73)` → `rgb(6, 132, 102)`
  - outline: `rgb(0, 77, 73) none 3px` → `rgb(6, 132, 102) none 3px`
- `button` (hover-before-06.png → hover-after-06.png)
  - color: `rgb(0, 84, 80)` → `rgb(6, 132, 102)`
  - borderColor: `rgb(0, 84, 80)` → `rgb(6, 132, 102)`
  - outline: `rgb(0, 84, 80) none 3px` → `rgb(6, 132, 102) none 3px`

## State inventory
- `a.cta-base -btn-pill--link-arrow` text='Learn more\n            \n\n            \n                \n    \n' selected=None expanded=None
- `a.-btn-pill navigation__btn-pill navigation__anchor js-header-item` text='Sign up' selected=None expanded=None
- `a.cta-base -btn-pill--primary` text='Get Started\n                                \n               ' selected=None expanded=None
- `p.cta-base -btn-pill--link-arrow` text='Learn more\n                            \n                    ' selected=None expanded=None
- `p.cta-base -btn-pill--link-arrow` text='Learn more\n                            \n                    ' selected=None expanded=None
- `p.cta-base -btn-pill--link-arrow` text='Learn more\n                            \n                    ' selected=None expanded=None
- `a.cta-base -btn-pill--link-arrow` text='See all our services\n            \n\n            \n            ' selected=None expanded=None
- `a.cta-base -btn-pill--link` text="See if we're in network with your insurance\n            \n\n  " selected=None expanded=None