# Behavior report

- **URL:** https://react.dev
- **Captured:** 2026-08-10T07:33:39+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 135,
  "tabs": 0,
  "accordions": 0,
  "carousels": 2,
  "observers": 18,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 2
}

## Scroll-triggered changes
- `nav.duration-300`
  - boxShadow: none → rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 16px 32px -16px, rgba(0, 0, 0, 0.1) 0px 0px 0px 1px

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(94, 104, 126)` → `rgb(8, 126, 164)`
  - outline: `rgb(94, 104, 126) none 3px` → `rgb(8, 126, 164) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(35, 39, 47, 0.05)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(35, 39, 47, 0.05)`

## State inventory
- no tabs/pills/accordions detected