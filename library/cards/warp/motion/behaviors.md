# Behavior report

- **URL:** https://www.warp.dev
- **Captured:** 2026-08-10T07:49:19+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 175,
  "tabs": 9,
  "accordions": 8,
  "carousels": 4,
  "observers": 19,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 4
}

## Scroll-triggered changes
- `div.fixed`
  - sel: div.fixed → nav.hidden
  - position: fixed → sticky
- `nav.hidden`
  - sel: nav.hidden → nav.grid
  - position: sticky → static

## Hover diffs (before → after)
- `button` (hover-before-01.png → hover-after-01.png)
  - color: `lab(66.9891 -2.04185 -1.96892)` → `lab(96.5815 -2.55355 -2.46191)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.969998 -0.00766945 -0.006405 / 0.05)`
  - borderColor: `lab(66.9891 -2.04185 -1.96892)` → `lab(96.5815 -2.55355 -2.46191)`
  - outline: `lab(66.9891 -2.04185 -1.96892) none 3px` → `lab(96.5815 -2.55355 -2.46191) none 3px`
- `button` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.07 -0.00536231 -0.00449951 / 0.05)`
- `button` (hover-before-03.png → hover-after-03.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.07 -0.00536231 -0.00449951 / 0.05)`
- `button` (hover-before-04.png → hover-after-04.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `oklab(0.07 -0.00536231 -0.00449951 / 0.05)`

## State inventory
- `span.tabular-nums` text='64k' selected=None expanded=None
- `span.text-[14px] leading-5 tabular-nums` text='4' selected=None expanded=None
- `span.text-[14px] leading-5 tabular-nums` text='1' selected=None expanded=None
- `span.text-[14px] leading-5 tabular-nums` text='3' selected=None expanded=None
- `span.text-[14px] leading-5 tabular-nums` text='2' selected=None expanded=None
- `span.text-[14px] leading-5 tabular-nums` text='4' selected=None expanded=None
- `p.shrink-0 tabular-nums text-[var(--color-muted)]` text='1 / 3' selected=None expanded=None
- `p.shrink-0 tabular-nums text-[var(--color-muted)]` text='2 / 3' selected=None expanded=None