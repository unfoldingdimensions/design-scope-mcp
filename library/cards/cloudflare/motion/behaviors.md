# Behavior report

- **URL:** https://www.cloudflare.com
- **Captured:** 2026-08-10T06:35:31+00:00
- **Interaction model:** scroll-driven

## Interaction model
- {
  "clickables": 107,
  "tabs": 12,
  "accordions": 0,
  "carousels": 0,
  "observers": 232,
  "scrollSnap": 8,
  "smoothScroll": null,
  "marquees": 0
}

## Scroll-triggered changes
- none detected (header/nav unchanged on scroll)

## Hover diffs (before → after)
- `a[href]` (hover-before-01.png → hover-after-01.png)
  - opacity: `1` → `0.8`
- `button` (hover-before-02.png → hover-after-02.png)
  - color: `oklab(0.268617 0.000012286 0.00000536442 / 0.4)` → `oklab(0.268617 0.000012286 0.00000536442 / 0.7)`
  - opacity: `0` → `1`

## State inventory
- `button.relative z-10 flex h-10 cursor-pointer items-center gap-2 rounded-full px-3.5 py` text='Network & CDN' selected=true expanded=None
- `button.relative z-10 flex h-10 cursor-pointer items-center gap-2 rounded-full px-3.5 py` text='SASE / Zero Trust' selected=false expanded=None
- `button.relative z-10 flex h-10 cursor-pointer items-center gap-2 rounded-full px-3.5 py` text='Compute & Storage' selected=false expanded=None
- `button.shrink-0 snap-start text-sm transition-colors font-medium rounded-sm focus:outli` text='Workers' selected=true expanded=None
- `button.shrink-0 snap-start text-sm transition-colors font-medium rounded-sm focus:outli` text='Durable Objects' selected=false expanded=None
- `button.shrink-0 snap-start text-sm transition-colors font-medium rounded-sm focus:outli` text='Workers KV' selected=false expanded=None
- `button.shrink-0 snap-start text-sm transition-colors font-medium rounded-sm focus:outli` text='Workers' selected=true expanded=None
- `button.shrink-0 snap-start text-sm transition-colors font-medium rounded-sm focus:outli` text='Durable Objects' selected=false expanded=None