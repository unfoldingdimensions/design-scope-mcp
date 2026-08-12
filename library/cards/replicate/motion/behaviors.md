# Behavior report

- **URL:** https://replicate.com
- **Captured:** 2026-08-10T07:56:55+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 168,
  "tabs": 10,
  "accordions": 0,
  "carousels": 49,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 49
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - color: `rgb(100, 100, 100)` → `rgb(32, 32, 32)`
  - borderColor: `rgb(100, 100, 100)` → `rgb(32, 32, 32)`
  - outline: `rgb(100, 100, 100) none 3px` → `rgb(32, 32, 32) none 3px`
- `button` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(0, 0, 0, 0)` → `rgba(0, 0, 0, 0.06)`
- `button` (hover-before-03.png → hover-after-03.png)
  - borderColor: `rgba(0, 0, 0, 0) rgba(0, 0, 0, 0) rgb(32, 32, 32)` → `rgb(206, 206, 206) rgb(206, 206, 206) rgb(32, 32, 32)`
- `button` (hover-before-04.png → hover-after-04.png)
  - color: `rgb(100, 100, 100)` → `rgb(32, 32, 32)`
  - borderColor: `rgba(0, 0, 0, 0)` → `rgb(206, 206, 206)`
  - outline: `rgb(100, 100, 100) none 3px` → `rgb(32, 32, 32) none 3px`

## State inventory
- `div.r8-tabs r8-tabs--bordered r8-tabs--sm px-4` text='NodePythonHTTP' selected=None expanded=None
- `button.r8-tabs__tab` text='Node' selected=true expanded=None
- `span.r8-tabs__tab-text` text='Node' selected=None expanded=None
- `button.r8-tabs__tab` text='Python' selected=false expanded=None
- `span.r8-tabs__tab-text` text='Python' selected=None expanded=None
- `button.r8-tabs__tab` text='HTTP' selected=false expanded=None
- `span.r8-tabs__tab-text` text='HTTP' selected=None expanded=None
- `div.r8-tabs__content` text='import Replicate from "replicate";const replicate = new Repl' selected=None expanded=None