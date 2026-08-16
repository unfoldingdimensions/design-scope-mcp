# United Carriers

- **URL:** https://unitedcarriers.com
- **Category:** misc
- **Captured:** 2026-08-12T18:04:29+00:00
- **Slug:** `united-carriers`

## Why it's in the library

Industrial B2B logistics site that proves "corporate" doesn't mean boring. Dark dot-matrix world map hero (animated dots via `world-wide-dot` keyframes, blue glow) over a white body — a data-viz global-reach statement instead of a stock photo. Type is the brand: BT Steinhart 700 uppercase at up to 177px, with 12px BT Steinhart Mono micro-labels for nav ("TALK WITH US", "OUR SERVICES"). Primary accent is a Klein-style blue #0016cb used sparingly on hover and highlights.

## What to borrow from it

- **Dot-matrix map hero**: stylized world map built from dots (`world-wide-dot` keyframes on 22 elements) — a themed data-viz hero that reads "global + precise + tech". Pairs with a blue radial glow at the hero base.
- **Letter-shuffle nav links** (`data-link-random` + `data-shuffle-initialized`): Webflow-style scramble animation on hover — text scrambles to random chars then settles on the target word. The most memorable microinteraction on the page; zero layout shift since it's text-content animation.
- **Sticky panel stack for services** (`home-service-stick first-screen/second-screen`, `home-service-speed`, `home-service-new-truck-stick`): several 100vh pinned panels slide over each other as you scroll — 12,000px section that feels like a film strip. The standard, reliable Webflow pinned-scroll pattern.
- **Scroll-scrub image zoom**: hero imagery scales to 1.4× as you scroll (transform driven), adding parallax depth.
- **Invert-on-hover buttons**: buttons flip borderColor + color #111 → #fff (dark pill on white flips to white pill with dark border/text). Simple, loud, zero ambiguity.
- **Header state change**: transparent header over dark hero → solid white with dark text after scroll — a scroll-triggered state that makes the nav "earn" its background.
- **Typography as hierarchy**: 177px display → 106px h2 → 80px hero h1, all uppercase, line-height 1.05, tight; mono 12px labels create the technical voice. No pill CTAs in the header — everything is a typographic link (mono labels).
- **Motion tokens**: signature ease is cubic-bezier(0.22, 1, 0.36, 1) (easeOutQuint — fast start, long settle) and cubic-bezier(0.445, 0.05, 0.55, 0.95); marquee loops at 6 instances for partner logos.
- **Restraint lesson**: white sections between dark ones; 66 partner logos rendered monochrome in CMS rows (no color noise, no animated clutter).

## Fingerprint summary

- Palette: 6 raw colors, 3 semantic
- Fonts: BT Steinhart, BT Steinhart Mono, Helvetica Neue
- Type sizes: 106.667px (6.67rem), 10px (0.63rem), 11.1111px (0.69rem), 13.3333px (0.83rem), 17.7778px (1.11rem), 177.778px (11.11rem), 22.2222px (1.39rem), 24px (1.50rem)
- Spacing scale: 2.22222px, 6.66667px, 8.88889px, 10px, 11.1111px, 13.3333px, 15.5556px, 16.6667px, 17.7778px, 18.8889px
- Radii: 1920px, 50%, 99%
- Components detected: 4
- Motion: {"durations": [{"value": "0.001s", "ms": 1, "count": 2263}], "easings": [{"value": "ease", "type": "ease", "count": 2171}, {"value": "cubic-bezier(0.445, 0.05, 0.55, 0.95)", "type": "custom", "count":

## Files

- `screenshot-desktop.png` — full-page, 1440px
- `screenshot-mobile.png` — full-page, 390px
- `fingerprint.json` — raw Dembrandt tokens
- `source.md` — capture metadata
- `motion/card-motion.webm` — recorded session: entrance anims, scroll-reveals, hover states, micro-interactions
- `motion/hover-NN.png` + `motion/hover-inventory.json` — hover-state captures per interactive element
