# Theme: anthropic (borrowed palette)

Generated 2026-08-11T11:56:15+00:00 from
`library/cards/anthropic/semantic.json`.

## Token remap

| Role | Current (your fingerprint) | Borrowed |
|---|---|---|
| `primary` | — | `--swatch--accent` → `#b45839` |
| `accent` | — | `--swatch--accent` → `#b45839` |
| `bg` | — | `--swatch--ivory-light` → `#faf9f5` |
| `text` | — | `--swatch--brand-text` → `#141413` |
| `muted` | — | `--swatch--kraft` → `#937058` |


## CSS (light)

```css
:root {
  --primary: #b45839;
  --accent: #b45839;
  --bg: #faf9f5;
  --text: #141413;
  --muted: #937058;
}
```



## Contrast guard

contrast guard: #c6613f 3.85:1 → #b45839 4.53:1 on #faf9f5
contrast guard: #c6613f 3.85:1 → #b45839 4.53:1 on #faf9f5
contrast guard: #d4a27f 2.15:1 → #937058 4.24:1 on #faf9f5

## Wire-in

1. Map `--primary`/`--accent`/`--bg`/`--text`/`--muted` onto your app's tokens
   (shadcn: primary/ring/destructive; Tailwind: theme colors).
2. Keep your existing font/spacing/radius tokens — this is a COLOR theme only.
3. Re-run `scripts/qa.py` on the next iteration — contrast is checked there.
