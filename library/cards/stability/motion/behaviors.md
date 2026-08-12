# Behavior report

- **URL:** https://stability.ai
- **Captured:** 2026-08-10T08:33:05+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 204,
  "tabs": 4,
  "accordions": 3,
  "carousels": 53,
  "observers": 4,
  "scrollSnap": 0,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- `header.black-bold`
  - background: rgba(0, 0, 0, 0) → rgba(30, 30, 30, 0.9)
  - backdropFilter: none → blur(12px)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - outline: `rgb(255, 255, 255) none 3px` → `rgb(255, 255, 255) none 0px`
- `.card` (hover-before-02.png → hover-after-02.png)
  - outline: `rgb(31, 31, 31) none 3px` → `rgb(31, 31, 31) none 0px`
- `.card` (hover-before-03.png → hover-after-03.png)
  - outline: `rgb(31, 31, 31) none 3px` → `rgb(31, 31, 31) none 0px`
- `.card` (hover-before-04.png → hover-after-04.png)
  - outline: `rgb(31, 31, 31) none 3px` → `rgb(31, 31, 31) none 0px`
- `.card` (hover-before-05.png → hover-after-05.png)
  - outline: `rgb(31, 31, 31) none 3px` → `rgb(31, 31, 31) none 0px`

## State inventory
- `body.tweak-blog-alternating-side-by-side-width-full tweak-blog-alternating-side-by-si` text='#fhCloseToggleModal{width: 25px;height: 25px;background-colo' selected=None expanded=None
- `div.sai-sah-play-disc stab-glass gs-svg` text='' selected=None expanded=None
- `div.sai-sah-pane-closeup stab-glass gs-svg` text='' selected=None expanded=None
- `div.sai-sah-lens stab-glass gs-svg` text='' selected=None expanded=None
- `button.
    user-items-list-carousel__arrow-button
    user-items-list-carousel__arrow-` text='' selected=None expanded=None
- `button.
    user-items-list-carousel__arrow-button
    user-items-list-carousel__arrow-` text='' selected=None expanded=None
- `button.
    mobile-arrow-button
    mobile-arrow-button--left
  ` text='' selected=None expanded=None
- `button.
    mobile-arrow-button
    mobile-arrow-button--right
  ` text='' selected=None expanded=None