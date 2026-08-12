# Behavior report

- **URL:** https://world.org
- **Captured:** 2026-08-10T12:56:02+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 96,
  "tabs": 2,
  "accordions": 0,
  "carousels": 2,
  "observers": 2,
  "scrollSnap": 1,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `header.print:hidden`
  - background: rgba(0, 0, 0, 0) → rgb(249, 249, 248)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - borderColor: `rgb(225, 223, 218)` → `rgb(157, 155, 150)`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgb(24, 24, 24)` → `rgb(66, 65, 64)`
- `button` (hover-before-03.png → hover-after-03.png)
  - borderColor: `rgb(225, 223, 218)` → `rgb(157, 155, 150)`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgb(24, 24, 24)` → `rgb(66, 65, 64)`
- `[role=button]` (hover-before-05.png → hover-after-05.png)
  - opacity: `1` → `0.9`
- `[role=button]` (hover-before-06.png → hover-after-06.png)
  - opacity: `1` → `0.9`

## State inventory
- `div.rly-editable-field-container-no-hover ` text='Cookie Preferences' selected=None expanded=None
- `div.rly-editable-field-container-no-hover rly-editable-description-container ` text='We use cookies to enhance site navigation, analyze site usag' selected=None expanded=None