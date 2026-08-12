# Behavior report

- **URL:** https://n8n.io
- **Captured:** 2026-08-10T10:00:37+00:00
- **Interaction model:** click-driven

## Interaction model
- {
  "clickables": 127,
  "tabs": 19,
  "accordions": 0,
  "carousels": 7,
  "observers": 0,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 6
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `[role=button]` (hover-before-01.png → hover-after-01.png)
  - backgroundColor: `rgb(238, 79, 39)` → `rgb(240, 94, 57)`
- `[role=button]` (hover-before-02.png → hover-after-02.png)
  - backgroundColor: `rgba(255, 255, 255, 0.106)` → `rgba(235, 235, 235, 0.106)`

## State inventory
- `section.w-full px-section-gap-x md:px-section-gap-x-md lg:px-section-gap-x-lg py-section` text='IT Ops can\nOn-board new employeesSec Ops can\nEnrich security' selected=None expanded=None
- `div.features-tabs-items flex flex-row gap-10 opacity-0` text='IT Ops can\nOn-board new employeesSec Ops can\nEnrich security' selected=None expanded=None
- `div.feature-tabs-items-nav-scroll custom-scroll custom-scroll-vertical max-h-[600px]` text='IT Ops can\nOn-board new employeesSec Ops can\nEnrich security' selected=None expanded=None
- `div.tab-trigger-indicator absolute left-0 z-[1] h-(--reka-tabs-indicator-size) w-ful` text='' selected=None expanded=None
- `button.tab-trigger relative z-10 flex w-full flex-1 shrink-0 cursor-pointer flex-col it` text='IT Ops can\nOn-board new employees' selected=true expanded=None
- `button.tab-trigger relative z-10 flex w-full flex-1 shrink-0 cursor-pointer flex-col it` text='Sec Ops can\nEnrich security incident tickets' selected=false expanded=None
- `button.tab-trigger relative z-10 flex w-full flex-1 shrink-0 cursor-pointer flex-col it` text='Dev Ops can\nConvert natural language into API calls' selected=false expanded=None
- `button.tab-trigger relative z-10 flex w-full flex-1 shrink-0 cursor-pointer flex-col it` text='Sales can\nGenerate customer insights from reviews' selected=false expanded=None