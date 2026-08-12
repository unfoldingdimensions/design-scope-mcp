# Behavior report

- **URL:** https://tauri.app
- **Captured:** 2026-08-10T07:48:05+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 185,
  "tabs": 20,
  "accordions": 0,
  "carousels": 0,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `oklch(0.5 0.15 253)` → `rgb(85, 89, 98)`
  - borderColor: `oklch(0.5 0.15 253)` → `rgb(85, 89, 98)`
  - outline: `oklch(0.5 0.15 253) none 3px` → `rgb(85, 89, 98) none 3px`
- `a[href]` (hover-before-02.png → hover-after-02.png)
  - color: `rgb(23, 24, 28)` → `rgb(85, 89, 98)`
  - borderColor: `rgb(23, 24, 28)` → `rgb(85, 89, 98)`
  - outline: `rgb(23, 24, 28) none 3px` → `rgb(85, 89, 98) none 3px`
- `a[href]` (hover-before-03.png → hover-after-03.png)
  - color: `rgb(23, 24, 28)` → `rgb(85, 89, 98)`
  - borderColor: `rgb(23, 24, 28)` → `rgb(85, 89, 98)`
  - outline: `rgb(23, 24, 28) none 3px` → `rgb(85, 89, 98) none 3px`
- `button` (hover-before-04.png → hover-after-04.png)
  - color: `rgb(35, 38, 47)` → `rgb(23, 24, 28)`
  - borderColor: `rgb(213, 215, 221)` → `rgb(35, 38, 47)`
  - outline: `rgb(35, 38, 47) none 3px` → `rgb(23, 24, 28) none 3px`

## State inventory
- `div.tablist-wrapper not-content astro-27ecw45w` text='BashPowerShellFishnpmYarnpnpmdenobunCargo' selected=None expanded=None
- `li.tab astro-27ecw45w` text='Bash' selected=None expanded=None
- `a.astro-27ecw45w` text='Bash' selected=true expanded=None
- `li.tab astro-27ecw45w` text='PowerShell' selected=None expanded=None
- `a.astro-27ecw45w` text='PowerShell' selected=false expanded=None
- `li.tab astro-27ecw45w` text='Fish' selected=None expanded=None
- `a.astro-27ecw45w` text='Fish' selected=false expanded=None
- `li.tab astro-27ecw45w` text='npm' selected=None expanded=None