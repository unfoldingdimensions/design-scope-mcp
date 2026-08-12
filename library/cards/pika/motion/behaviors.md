# Behavior report

- **URL:** https://pika.art
- **Captured:** 2026-08-10T08:41:38+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 38,
  "tabs": 1,
  "accordions": 0,
  "carousels": 0,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `div.fixed`
  - background: rgba(0, 0, 0, 0) → rgba(252, 250, 247, 0.8)
  - backdropFilter: none → blur(16px)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7)` → `rgb(13, 13, 13)`
  - outline: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7) none 3px` → `rgb(13, 13, 13) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - color: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7)` → `rgb(13, 13, 13)`
  - outline: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7) none 3px` → `rgb(13, 13, 13) none 3px`
- `a[href]` (hover-before-03.png → hover-after-03.png)
  - color: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7)` → `rgb(13, 13, 13)`
  - outline: `oklab(0.159065 0.00000723451 0.00000317395 / 0.7) none 3px` → `rgb(13, 13, 13) none 3px`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgb(252, 250, 247)` → `rgb(255, 255, 255)`

## State inventory
- `div.absolute top-0 right-0 left-0 z-40 flex h-(--mobile-height) tablet:h-(--height)` text='CareersReferralContact UsPricingAPIExperimentsLoginSign UpCa' selected=None expanded=None