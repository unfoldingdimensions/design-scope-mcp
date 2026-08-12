# Behavior report

- **URL:** https://www.riotgames.com
- **Captured:** 2026-08-10T16:35:40+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 83,
  "tabs": 3,
  "accordions": 0,
  "carousels": 9,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(240, 240, 240)` → `rgb(220, 220, 220)`
  - borderColor: `rgb(240, 240, 240)` → `rgb(220, 220, 220)`
  - outline: `rgb(240, 240, 240) none 3px` → `rgb(220, 220, 220) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(209, 54, 58)` → `rgb(43, 42, 41)`
  - borderColor: `rgb(209, 54, 58)` → `rgb(43, 42, 41)`
  - outline: `rgb(209, 54, 58) none 3px` → `rgb(43, 42, 41) none 0px`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgb(240, 240, 240)` → `rgb(220, 220, 220)`

## State inventory
- `div.widget__wrapper widget__wrapper--homepageheronew js-widget js-widget--desktop vi` text=':root {\n              --color-bg-gradient: rgba(163, 38, 41,' selected=None expanded=None
- `div.widget__wrapper widget__wrapper--whatshappening js-widget js-widget--desktop vis` text="What's happening?See moreWhat would a “League Classic Viego”" selected=None expanded=None
- `button.content-showcase__carousel__button content-showcase__carousel__button--disabled` text='' selected=None expanded=None
- `button.content-showcase__carousel__button content-showcase__carousel__button--next` text='' selected=None expanded=None
- `div.widget__wrapper widget__wrapper--careers js-widget js-widget--desktop visible--d` text='We’re hiring!Team up with Riot to forge your path and craft ' selected=None expanded=None