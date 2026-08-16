# Produx Design

- **URL:** https://www.produx.design
- **Category:** misc
- **Captured:** 2026-08-12T18:01:09+00:00
- **Slug:** `produx-design`

## Why it's in the library

Dark "brutalist-lite" agency site where typography IS the imagery. No photos in the hero — just a 151px At Aero wordmark, a split-word masked headline ("You feel the brand before it speaks®"), and a `[SCROLL DOWN]` mono hint. The page alternates near-black (#0e0e0e) full-bleed sections with solid sage blocks (#545e54 "Hoki") — color blocks as section transitions, not gradients or images.

## What to borrow from it

- **Split-word hero reveal**: each word sits in an `overflow-hidden` span, starts `translate-y-full opacity-10`, eases up to `translate(0,0) opacity 1` (inline transform written by JS tween). Cheap, universal, high-impact entrance.
- **Sticky-hero stacking**: hero is `position:sticky; top:0` with `-mb-[17.5vh]` so the next section scrolls over it — section-to-section transition without any JS.
- **Roll-up word-swap nav**: two stacked copies of the label; hover translates the stack up (visible copy slides out, duplicate slides in) — pure CSS transform, works with any font.
- **Blur-in menu links**: nav links enter with `opacity-0 blur-md -rotate-2 translate-y-1/2` → settle. Blur + slight rotate = tactile, not cheesy.
- **Page transition**: full-screen overlay (`bg-Hoki`, z-9999999) that scales+rotates in like a curtain wipe while the next route loads (Next.js); brand-colored, not black.
- **Cursor follower**: fixed `pointer-events-none` element (84×28px) trailing the mouse — repurposed as a project-name label on work cards.
- **Type system**: At Aero (serif-led display, weights 400/500) + DM Mono for micro-labels; giant 98–151px display sizes, tight line-height 1.0; sharp corners, flat (no shadows).
- **Playful microinteractions**: floating cookie image in the corner (brand easter egg), text-based cookie consent ("I'LL PASS. THANKS"), `[SCROLL DOWN]` affordance.
- **Warning**: ships a lil-gui debug panel in production (`lil-root`) — a "don't do this" detail; also the tiny 1ms "ease" transitions detected by the fingerprint suggest most motion is JS-driven (tweens), not CSS.

## Fingerprint summary

- Palette: 6 raw colors, 2 semantic
- Fonts: -apple-system, At Aero, At Aero Medium, At Aero Regular
- Type sizes: 11px (0.69rem), 13.248px (0.83rem), 13.44px (0.84rem), 14px (0.88rem), 15.936px (1.00rem), 151.68px (9.48rem), 16.128px (1.01rem), 16px (1.00rem)
- Spacing scale: 4px, 4.212px, 7.872px, 10.752px, 11.904px, 12.636px, 13.248px, 14.592px, 15.936px, 16.2px
- Radii: 2px, 4px, 3.35544e+07px
- Components detected: 4
- Motion: {"durations": [{"value": "0.001s", "ms": 1, "count": 2294}], "easings": [{"value": "ease", "type": "ease", "count": 2282}, {"value": "cubic-bezier(0.4, 0, 0.2, 1)", "type": "custom", "count": 12}], "a

## Files

- `screenshot-desktop.png` — full-page, 1440px
- `screenshot-mobile.png` — full-page, 390px
- `fingerprint.json` — raw Dembrandt tokens
- `source.md` — capture metadata
- `motion/card-motion.webm` — recorded session: entrance anims, scroll-reveals, hover states, micro-interactions
- `motion/hover-NN.png` + `motion/hover-inventory.json` — hover-state captures per interactive element
