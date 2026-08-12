# Behavior report

- **URL:** https://www.adyen.com
- **Captured:** 2026-08-10T12:23:19+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 120,
  "tabs": 0,
  "accordions": 5,
  "carousels": 0,
  "observers": 3,
  "scrollSnap": 19,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `nav.group`
  - sel: nav.group → div.pointer-events-auto
  - position: static → sticky
- `div.pointer-events-auto`
  - sel: div.pointer-events-auto → div.sticky
- `div.sticky`
  - sel: div.sticky → div.relative
- `div.relative`
  - sel: div.relative → div.md:sticky
- `div.md:sticky`
  - sel: div.md:sticky → div.lg:sticky
- `div.lg:sticky`
  - sel: div.lg:sticky → div.sticky

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - textDecoration: `1px` → `None`
- `button` (hover-before-02.png → hover-after-02.png)
  - opacity: `1` → `0.572`
- `button` (hover-before-03.png → hover-after-03.png)
  - opacity: `1` → `0.572`
- `button` (hover-before-04.png → hover-after-04.png)
  - opacity: `1` → `0.572`

## State inventory
- no tabs/pills/accordions detected