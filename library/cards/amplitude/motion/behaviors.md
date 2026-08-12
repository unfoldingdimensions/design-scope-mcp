# Behavior report

- **URL:** https://amplitude.com
- **Captured:** 2026-08-10T10:32:41+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 275,
  "tabs": 14,
  "accordions": 0,
  "carousels": 1,
  "observers": 19,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 1
}

## Scroll-triggered changes
- `nav.relative`
  - background: rgba(0, 0, 0, 0) → rgba(245, 247, 249, 0.9)
  - backdropFilter: none → blur(30px)
- `nav.relative`
  - background: rgba(0, 0, 0, 0) → rgba(245, 247, 249, 0.9)
  - backdropFilter: none → blur(30px)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgb(243, 243, 243)`
- `button` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgb(30, 97, 240)` → `rgb(23, 9, 233)`

## State inventory
- `button.ccc-notify-button ccc-link ccc-tabbable ccc-accept-button` text='Accept' selected=None expanded=None
- `button.ccc-notify-button ccc-link ccc-tabbable ccc-reject-button` text='Reject' selected=None expanded=None
- `button.ccc-notify-button ccc-link ccc-tabbable ccc-notify-link` text='Settings' selected=None expanded=None
- `button.relative h-12 px-3 text-[15px] md:text-[16px] font-semibold leading-[22px] text-` text='Agent Analytics' selected=true expanded=None
- `button.relative h-12 px-3 text-[15px] md:text-[16px] font-semibold leading-[22px] text-` text='Global Chat' selected=false expanded=None
- `button.relative h-12 px-3 text-[15px] md:text-[16px] font-semibold leading-[22px] text-` text='AI-powered Replays' selected=false expanded=None
- `button.relative h-12 px-3 text-[15px] md:text-[16px] font-semibold leading-[22px] text-` text='AI Data Governance' selected=false expanded=None
- `button.h-10 rounded-full px-4 text-[16px] font-semibold leading-[22px] transition-color` text='MCP' selected=true expanded=None