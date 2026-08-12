# Behavior report

- **URL:** https://www.ledger.com
- **Captured:** 2026-08-10T13:19:26+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 350,
  "tabs": 24,
  "accordions": 0,
  "carousels": 0,
  "observers": 2,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `header.`
  - sel: header. → header.transparent-white-font
  - background: rgba(0, 0, 0, 0) → rgb(255, 255, 255)
  - backdropFilter: blur(40px) brightness(0.9) contrast(1.1) opacity(0.8) → none

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - filter: `invert(1)` → `invert(0)`

## State inventory
- `div.navigation__tabs` text='Products\n                    \n                            \n ' selected=None expanded=None
- `button.navigation__tabs__trigger navigation-button active` text='Products' selected=None expanded=None
- `button.navigation__tabs__trigger navigation-button` text='Ledger Wallet' selected=None expanded=None
- `button.navigation__tabs__trigger navigation-button` text='Learn' selected=None expanded=None
- `button.navigation__tabs__trigger navigation-button` text='For Business' selected=None expanded=None
- `a.navigation__tabs__link navigation-button` text='For Developers' selected=None expanded=None
- `a.navigation__tabs__link navigation-button` text='Support' selected=None expanded=None
- `div.navigation__tabs__content active` text='Discover our devices\n\n            \n        \n        \n       ' selected=None expanded=None