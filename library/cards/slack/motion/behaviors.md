# Behavior report

- **URL:** https://slack.com
- **Captured:** 2026-08-10T06:06:36+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 345,
  "tabs": 5,
  "accordions": 124,
  "carousels": 167,
  "observers": 2,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `nav.c-nav`
  - position: absolute → fixed
- `div.c-nav__row`
  - boxShadow: none → rgba(0, 0, 0, 0.08) 0px 4px 40px 0px
  - background: rgba(0, 0, 0, 0) → rgb(255, 255, 255)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - outline: `rgb(18, 100, 163) none 3px` → `rgb(18, 100, 163) none 0px`

## State inventory
- `div.c-button__nav-primary-tablet mobile-y-search-container` text='Get started' selected=None expanded=None
- `a.c-button v--primary v--left c-button__nav-primary-tablet` text='Get started' selected=None expanded=None
- `button.c-video-control c-video-control--light` text='Pause animationPlay animation' selected=None expanded=None
- `div.o-content-container c-switcher-desktop o-two-columns v--tablet u-hide-on-mobile ` text='Update deals just by asking SlackbotNEWSummarise a conversat' selected=None expanded=None
- `button.c-switcher-nav-item__heading-row` text='Update deals just by asking SlackbotNEW' selected=None expanded=None
- `button.c-switcher-nav-item__heading-row` text='Summarise a conversation you missed' selected=None expanded=None
- `button.c-switcher-nav-item__heading-row` text='Get fast answers with ClaudeNEW' selected=None expanded=None
- `button.c-switcher-nav-item__heading-row` text='Turn on AI note-taking in huddles' selected=None expanded=None