# Lama Lama Branding

- **URL:** https://lamalama.com/services/branding/
- **Category:** misc
- **Captured:** 2026-08-12T18:09:04+00:00
- **Slug:** `lama-lama-branding`

## Why it's in the library

Warm-minimal branding studio page that pairs a cream canvas (#f9f4eb) with near-black #010101 type and pure-white invert surfaces. Typography is compressed and huge — SuisseBPIntl 700 uppercase at 106px with line-height 0.80 and negative tracking, bracketed mono eyebrows ("[ NOT JUST SEEN. FELT. ]"), Sometype mono micro-labels everywhere. Everything is tweened by JS: Lenis smooth scroll inside a custom scroll container, 196 IntersectionObservers driving `.ll-text-reveal` opacity reveals, SWUP page transitions with a full-screen cream overlay, and 39 images rendered through WebGL shaders with parallax.

## What to borrow from it

- **Two-layer invert button**: every button is a stack — a `js-backdrop` (solid black) + `js-backdrop-hover` (white, opacity 0 → 1 on hover) + two text layers (`js-text` base, `js-text-hover` absolute + opacity-0, crossfades in). Hover = background color swap AND text color crossfade simultaneously. No scale, no shadow — pure color exchange, feels instant and premium.
- **Text reveal system**: `.ll-text-reveal` elements start `opacity-0`, each with its own IntersectionObserver (196 of them) toggling visibility — per-element, per-type delays create a cascade (title → description → text). Uses classes per type: `js-text-reveal-title / -description / -text`.
- **Mono text-reveal labels** (`js-mono-text-reveal`): bracketed mono eyebrows that reveal independently — the "[ ... ]" framing is the studio's signature voice.
- **Triple-icon nav hover**: each nav item carries `js-icon-alt`, `js-icon-mid`, `js-icon-mid-second` — three stacked icons crossfading/rotating through on hover, plus a 1px underline that scales from 0. Icon morph + underline grow in one interaction.
- **Page transition**: SWUP + `js-page-transition` full-screen overlay (`bg-bgPrimary`, i.e. the cream color, not black) + `data-swup-morph` hints — content morphs between pages rather than hard-replacing.
- **WebGL image treatment**: `ll-part--webgl-image` with `data-parallax` — images drawn through shader canvases for parallax displacement (3 canvases, 39 images). The "expensive" layer that separates studio sites from templates.
- **Fluid spacing tokens**: every spacing token is `max(rem floor, vw value)` — e.g. `--spacing-md: max(calc(16/16*1rem), calc(24/1440*100vw))`; section rhythm tokens `--section-xs..2xl`. The grid: 12 cols desktop / 6 mobile, margin 2.5rem desktop / 1rem mobile.
- **Radii discipline**: 2.67px badges, ~5.33px buttons — barely-rounded, keeps the type-forward voice sharp.
- **Lenis + custom scroller**: `ll-scroller js-scroller lenis` with `js-scroll-content` — smooth-scroll inertia that makes every scroll-driven reveal feel weighty.
- **Large body type**: body copy at 29–32px, lh 1.2 — a confident editorial voice, not 16px SaaS default.

## Fingerprint summary

- Palette: 4 raw colors, 4 semantic
- Fonts: Sometype, SuisseBPIntl
- Type sizes: 106.667px (6.67rem), 13.3333px (0.83rem), 18.6666px (1.17rem), 21.3333px (1.33rem), 21.352px (1.33rem), 24.0586px (1.50rem), 26.6666px (1.67rem), 26.72px (1.67rem)
- Spacing scale: 2px, 2.66666px, 5.33333px, 7.99999px, 10.6667px, 14.6667px, 16px, 17.3333px, 21.3333px, 26.6666px
- Radii: 2.66666px, 5.33333px, 9999px
- Components detected: 4
- Motion: {"durations": [{"value": "0.001s", "ms": 1, "count": 2144}], "easings": [{"value": "ease", "type": "ease", "count": 2144}], "animations": [], "contexts": {"hero": {"count": 4, "durations": ["0.001s"],

## Files

- `screenshot-desktop.png` — full-page, 1440px
- `screenshot-mobile.png` — full-page, 390px
- `fingerprint.json` — raw Dembrandt tokens
- `source.md` — capture metadata
- `motion/card-motion.webm` — recorded session: entrance anims, scroll-reveals, hover states, micro-interactions
- `motion/hover-NN.png` + `motion/hover-inventory.json` — hover-state captures per interactive element
