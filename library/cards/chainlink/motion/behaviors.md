# Behavior report

- **URL:** https://chain.link
- **Captured:** 2026-08-10T13:28:55+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 178,
  "tabs": 15,
  "accordions": 0,
  "carousels": 83,
  "observers": 22,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 149
}

## Scroll-triggered changes
- `div.chainlink-system--navigation`
  - boxShadow: rgba(209, 224, 250, 0.18) 0px -1px 0px 0px inset → rgba(217, 226, 242, 0.13) 0px -1px 0px 0px inset
  - background: rgb(8, 71, 247) → rgb(14, 17, 25)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(245, 247, 250)` → `rgb(33, 39, 50)`
  - borderColor: `rgb(245, 247, 250)` → `rgb(33, 39, 50)`
  - outline: `rgb(245, 247, 250) none 3px` → `rgb(33, 39, 50) none 0px`
- `[role=button]` (hover-before-02.png → hover-after-02.png)
  - color: `rgba(22, 37, 65, 0.35)` → `rgba(217, 226, 242, 0.8)`
  - borderColor: `rgba(22, 37, 65, 0.35)` → `rgba(217, 226, 242, 0.8)`
  - opacity: `0.5` → `1`
  - outline: `rgba(22, 37, 65, 0.35) none 3px` → `rgba(217, 226, 242, 0.8) none 3px`
- `[role=button]` (hover-before-03.png → hover-after-03.png)
  - color: `rgba(217, 226, 242, 0.4)` → `rgba(22, 37, 65, 0.95)`
  - borderColor: `rgba(217, 226, 242, 0.4)` → `rgba(22, 37, 65, 0.95)`
  - opacity: `0.5` → `1`
  - outline: `rgba(217, 226, 242, 0.4) none 3px` → `rgba(22, 37, 65, 0.95) none 3px`
- `[role=button]` (hover-before-04.png → hover-after-04.png)
  - color: `rgba(209, 224, 250, 0.5)` → `rgba(209, 224, 250, 0.9)`
  - borderColor: `rgba(209, 224, 250, 0.5)` → `rgba(209, 224, 250, 0.9)`
  - opacity: `0.5` → `1`
  - outline: `rgba(209, 224, 250, 0.5) none 3px` → `rgba(209, 224, 250, 0.9) none 3px`
- `[role=button]` (hover-before-05.png → hover-after-05.png)
  - color: `rgba(209, 224, 250, 0.5)` → `rgba(209, 224, 250, 0.9)`
  - borderColor: `rgba(209, 224, 250, 0.5)` → `rgba(209, 224, 250, 0.9)`
  - opacity: `0.5` → `1`
  - outline: `rgba(209, 224, 250, 0.5) none 3px` → `rgba(209, 224, 250, 0.9) none 3px`

## State inventory
- `div.tabs u-pl-0-5 u-pr-0-5 w-tabs` text='Tokenized fundsstablecoinsPayments & SettlementsOnChain Data' selected=None expanded=None
- `div.tab-group u-pb-0-5 w-tab-menu` text='Tokenized fundsstablecoinsPayments & SettlementsOnChain Data' selected=None expanded=None
- `a.tab-label w-inline-block w-tab-link w--current` text='Tokenized funds' selected=true expanded=None
- `a.tab-label w-inline-block w-tab-link` text='stablecoins' selected=false expanded=None
- `a.tab-label w-inline-block w-tab-link` text='Payments & Settlements' selected=false expanded=None
- `a.tab-label w-inline-block w-tab-link` text='OnChain Data Delivery' selected=false expanded=None
- `a.tab-label w-inline-block w-tab-link` text='Lending & Borrowing' selected=false expanded=None
- `a.tab-label w-inline-block w-tab-link` text='Derivatives' selected=false expanded=None