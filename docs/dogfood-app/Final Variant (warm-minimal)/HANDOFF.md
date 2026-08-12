# HANDOFF — Final Variant (warm-minimal)

Handoff package for the consuming agent. Everything needed to integrate this
design into a real app is in this folder. **No source files of the target
project are modified by this package.**

## What this is

The finalized UI variant of **Pulse (dogfood)**, produced by
design-scope. Built from iteration `002` (rec2-color),
adopting recommendations: R2.

## Package structure

```
Final Variant (warm-minimal)/
├── index.html            ← the winning screen, fully interactive (both themes)
├── assets/
│   ├── tokens.css        ← ALL design tokens (CSS variables) — start here
│   └── theme.js          ← theme toggle (light/dark), persisted
└── components/
    ├── index.html        ← component gallery (browse this first)
    ├── button.html       ← primary/ghost/danger × 6 states
    ├── input.html        ← default/focus/error/disabled
    ├── card.html         ← surface + hover lift
    ├── nav.html          ← logo + links + theme toggle
    ├── badge.html        ← neutral/success/warning/error
    ├── toast.html        ← success/error with recovery action
    ├── empty-state.html  ← meaningful empty state
    ├── stat.html         ← number + label
    └── form.html         ← labeled + validated form
```

## Design tokens

| Token | Value |
|---|---|
| `--bg` | `#FAFAF9` |
| `--surface` | `#F5F5F4` |
| `--border` | `#E7E5E4` |
| `--text` | `#1C1917` |
| `--text-muted` | `#78716C` |
| `--accent` | `#0D9488` |
| `--accent-ink` | `#FFFFFF` |
| `--radius` | `10px` |
| `--ease` | `cubic-bezier(0.22, 1, 0.36, 1)` |

## Components (each self-contained, copy-paste ready)

| File | Contents |
|---|---|
| `components/button.html` | Button — all states |
| `components/input.html` | Input — all states |
| `components/card.html` | Card — all states |
| `components/nav.html` | Nav — all states |
| `components/badge.html` | Badge — all states |
| `components/toast.html` | Toast — all states |
| `components/empty-state.html` | Empty state — all states |
| `components/stat.html` | Stat — all states |
| `components/form.html` | Form — all states |

## Integration notes

1. **Tokens first**: copy `assets/tokens.css` values into your app's global
   CSS/token file (CSS variables, Tailwind theme, or shadcn tokens — map by
   role: `--bg` → background, `--text` → foreground, `--accent` → primary, …).
2. **Dark theme**: if the variant has `[data-theme="dark"]`, wire `theme.js`
   (or your own toggle) to set `data-theme` on `<html>`.
3. **Components**: each `components/*.html` is self-contained — copy the
   markup + styles into your framework's component. States are already wired
   (hover/active/focus-visible/disabled/loading/error).
4. **Motion**: easing and durations use the finalized tokens (`--ease` /
   `--ease-snap`); `prefers-reduced-motion` is handled globally in tokens.css.
5. **Empty/error states**: use them — they are part of the design, not
   afterthoughts.

## Provenance

- Source target: `<project>/docs/dogfood-app`
- Finalized: 2026-08-09T16:07:29+00:00
- Winning iteration: `002-rec2-color`
- Adopted recs: R2
- Reference cards cited: anthropic, monzo
