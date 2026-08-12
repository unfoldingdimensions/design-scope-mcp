# Behavior report

- **URL:** https://proton.me
- **Captured:** 2026-08-10T11:58:44+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 310,
  "tabs": 10,
  "accordions": 0,
  "carousels": 24,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `div.top-0`
  - sel: div.top-0 → header.container
  - position: sticky → static
  - background: rgb(255, 255, 255) → rgba(0, 0, 0, 0)
- `header.container`
  - sel: header.container → nav.
- `nav.`
  - sel: nav. → div.pointer-events-none
  - position: static → fixed
  - background: rgba(0, 0, 0, 0) → rgba(55, 37, 128, 0.6)
- `div.pointer-events-none`
  - sel: div.pointer-events-none → div.fixed
  - boxShadow: none → rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(74, 45, 197, 0.1) 0px 4px 8px 0px
  - background: rgba(55, 37, 128, 0.6) → rgb(255, 255, 255)
- `div.fixed`
  - sel: div.fixed → span.header-mobile-menu-toggle-icon
  - position: fixed → relative
  - boxShadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(74, 45, 197, 0.1) 0px 4px 8px 0px → none
  - background: rgb(255, 255, 255) → rgba(0, 0, 0, 0)
- `span.header-mobile-menu-toggle-icon`
  - sel: span.header-mobile-menu-toggle-icon → nav.col-span-full
  - position: relative → static

## Hover diffs (before → after)
- `button` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(55, 37, 128)` → `rgb(109, 74, 255)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(109, 74, 255, 0.1)`
- `button` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(55, 37, 128)` → `rgb(109, 74, 255)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(109, 74, 255, 0.1)`
- `button` (hover-before-03.png → hover-after-03.png)
  - color: `rgb(55, 37, 128)` → `rgb(109, 74, 255)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(109, 74, 255, 0.1)`
- `button` (hover-before-04.png → hover-after-04.png)
  - color: `rgb(55, 37, 128)` → `rgb(109, 74, 255)`
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(109, 74, 255, 0.1)`

## State inventory
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Mail' selected=true expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton VPN' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Drive' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Pass' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Lumo AI' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Calendar' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Meet' selected=false expanded=None
- `button.w-fit rounded-full px-4 py-2 text-start font-semibold text-sm outline-none ring-` text='Proton Authenticator' selected=false expanded=None