# Behavior report

- **URL:** https://akiflow.com
- **Captured:** 2026-08-10T11:38:16+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 92,
  "tabs": 5,
  "accordions": 0,
  "carousels": 4,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgba(255, 255, 255, 0)` → `rgb(255, 255, 255)`
  - backgroundImage: `linear-gradient(rgba(255, 255, 255, 0) 0%, rgba(255, 255, 255, 0) 100%)` → `linear-gradient(rgb(255, 255, 255) 0%, rgb(255, 255, 255) 100%)`

## State inventory
- `div.consent-banner-tabs` text='Consent\n                    Details' selected=None expanded=None
- `button.consent-banner-tab-btn active` text='Consent' selected=true expanded=None
- `button.consent-banner-tab-btn` text='Details' selected=false expanded=None
- `div.consent-banner-tab-content active` text='Necessary Required\n                        \n                ' selected=None expanded=None
- `div.consent-banner-tab-content` text='Your Rights\n                        \n                       ' selected=None expanded=None