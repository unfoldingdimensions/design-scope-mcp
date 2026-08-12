# Behavior report

- **URL:** https://www.squarespace.com
- **Captured:** 2026-08-10T05:05:01+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 556,
  "tabs": 160,
  "accordions": 101,
  "carousels": 299,
  "observers": 1,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `div.global-navigation__header`
  - background: rgba(0, 0, 0, 0) → rgb(0, 0, 0)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - outline: `rgb(0, 0, 0) none 3px` → `rgb(0, 0, 0) none 0px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - outline: `rgb(0, 0, 0) none 3px` → `rgb(0, 0, 0) none 0px`

## State inventory
- `ul.global-navigation__solutions-submenu-pills` text='PhotographersGraphic DesignersArtistsInterior DesignersArchi' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Photographers' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Graphic Designers' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Artists' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Interior Designers' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Architects' selected=None expanded=None
- `a.cta cta--inline cta--light global-navigation__solutions-submenu-pill` text='Fashion & Apparel' selected=None expanded=None
- `ul.global-navigation__solutions-submenu-pills` text='ConsultantsProfessional CoachesReal Estate AgentsLegal Servi' selected=None expanded=None