#!/usr/bin/env python3
"""design-scope sheet content — the agent's fill layer for the one-shot sheet.

The blueprint renders structure; this module holds the content the agent
writes per band type. Stable across re-scaffolds: scaffold() merges it into
the skeleton, so structure can be re-measured without losing copy.

Every string here uses the sheet's classes and tokens only — the verdict's
palette conformance check measures the rendered document.
"""

CONTENT = {
    "nav": {
        "links": """<a href="#s03">03 REGISTER</a>
      <a href="#s04">04 SCAN</a>
      <a href="#s05">05 BASIS</a>
      <a href="#s06">06 VERDICT</a>
      <a href="#s07">07 LEDGER</a>
      <a href="#s08">08 START</a>
      <a href="#s09">09 PRICING</a>""",
    },
    "hero": {
        "headline": "One-shotted.",
        "sub": ("Every decision on this sheet traces to a tool call — the palette was borrowed, "
                "the structure was measured off the scanned corpus, the grade was measured. "
                "The receipt is printed below."),
        "cta_primary": ("<a class=\"cta cta-primary\" href=\"#s06\">READ THE VERDICT</a>"),
        "cta_secondary": ("<a class=\"cta cta-ghost\" href=\"#s03\">READ THE REGISTER</a>"),
        "fig": """<svg class="fig-art" viewBox="0 0 420 264" role="img" aria-label="The build receipt: style_search, card_get, theme_borrow, get_page_structure, section_scan, verdict — 0 credits">
          <rect class="frame" x="30" y="18" width="360" height="120" rx="4"/>
          <path class="frame" d="M30 40h360"/>
          <rect class="bar bar-hot" x="44" y="52" width="150" height="10" rx="2"/>
          <path class="dim-accent" d="M204 57h146"/>
          <rect class="bar bar-hot" x="44" y="70" width="180" height="10" rx="2"/>
          <path class="dim-accent" d="M234 75h116"/>
          <rect class="bar bar-hot" x="44" y="88" width="120" height="10" rx="2"/>
          <path class="dim-accent" d="M174 93h176"/>
          <rect class="bar bar-hot" x="44" y="106" width="200" height="10" rx="2"/>
          <path class="dim-accent" d="M254 111h96"/>
          <text class="tick-label" x="44" y="164">style_search → theme_borrow → get_page_structure → section_scan</text>
          <text class="tick-label-accent" x="44" y="184">derive_tokens · verdict.py</text>
          <path class="dim" d="M30 196h360"/>
          <path class="dim-accent" d="M30 192v8M390 192v8"/>
          <text class="tick-label" x="44" y="222">6 DECISIONS · 1 GRADE · 0 CREDITS · LOCAL-FIRST</text>
          <text class="tick-label" x="44" y="244">STRUCTURE MEASURED OFF <tspan font-weight="700" fill="var(--accent-text)"><tspan data-stat="corpus.bands_scanned">—</tspan> SITES</tspan> · <tspan font-weight="700" fill="var(--accent-text)"><tspan data-stat="corpus.bands_measured">—</tspan> BANDS</tspan></text>
        </svg>""",
    },
    "how-it-works": {
        "title": "The register — the receipt is the proof",
        "intro": ("The actual calls that built this sheet, in order. Select a row to read what "
                  "went in and what came out. Machine-written — no row here was typed by hand."),
        "body": """<div class="steps">
      <div class="step-list" id="step-list"></div>
      <div class="step-detail">
        <div class="d-label" id="step-label">—</div>
        <p id="step-text">Loading the register…</p>
      </div>
    </div>
    <div class="register-note" id="register-note">SPENT 0 OF 0 CREDITS · LOCAL-FIRST · EVERY ROW MACHINE-WRITTEN</div>""",
    },
    "product-showcase": {
        "title": "The style index, divided the honest way",
        "intro": ("Every tag counted from style-index.json — not from an opinion about which "
                  "style matters. The band types above were measured off the scanned corpus."),
        "body": """<div class="scan-cols">
      <div class="scan-block">
        <h3>Archetypes — most tagged first</h3>
        <div id="arch-bars"></div>
      </div>
      <div>
        <div class="scan-block">
          <h3>Hue families</h3>
          <div id="hue-bars"></div>
        </div>
        <div class="scan-insight" id="scan-insight">Counting…</div>
      </div>
    </div>""",
    },
    "features-grid": {
        "title": "The corpus behind the sheet",
        "intro": ("<span data-stat=\"corpus.captured\">—</span> pages measured. Every one fingerprinted, "
                  "motion-passed, and annotated "
                  "with why it works. The palette on this sheet was borrowed from one of them."),
        "body": """<div class="stat-grid">
      <div class="stat-card">
        <div class="stat-num"><span data-stat="corpus.captured">—</span><span class="unit">pages</span></div>
        <div class="stat-label">Captured</div>
        <div class="stat-note">Fingerprinted, screenshot, motion-passed — each a full card.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num"><span data-stat="corpus.annotated">—</span><span class="unit">reviewed</span></div>
        <div class="stat-label">Vision-reviewed</div>
        <div class="stat-note">A vision pass wrote the why-it-works annotation on each card.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num"><span data-stat="corpus.style_indexed">—</span><span class="unit">indexed</span></div>
        <div class="stat-label">Style-indexed</div>
        <div class="stat-note">Vectorised into style-index.json — searchable in natural language.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num"><span data-stat="corpus.dark_themed">—</span><span class="unit">dark</span></div>
        <div class="stat-label">Dark-themed</div>
        <div class="stat-note">Cards whose semantic.json ships a full dark palette.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num"><span data-stat="corpus.behaviors">—</span><span class="unit">motion</span></div>
        <div class="stat-label">Motion-evidenced</div>
        <div class="stat-note">Recorded card-motion.webm + behaviors.md: what moves, when, and the easing.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">11<span class="unit">tools</span></div>
        <div class="stat-label">Local-first</div>
        <div class="stat-note">No cloud, no credits, no accounts. The library is a folder on your disk.</div>
      </div>
    </div>
    <div class="ref-line" id="ref-line">REFERENCE — <code>loading…</code></div>""",
    },
    "feature-spotlight": {
        "title": "This page was graded by the same pass your agent gets",
        "intro": ("Six checks, measured off the rendered document — the figures below were read "
                  "from this build, not from the record that planned it."),
        "body": """<div id="verdict-root"></div>""",
    },
    "ledger": {
        "title": "No users yet. Read the record upward instead.",
        "intro": ("Every verdict the review pass has returned on this page, oldest at the foot. "
                  "A ledger with no pending row is a ledger that stopped being kept."),
        "body": """<div id="ledger-root"></div>""",
    },
    "cta-banner": {
        "title": "One-shot your own sheet",
        "intro": ("Two commands: scaffold runs the tools and renders the skeleton; grade measures "
                  "the result and keeps the ledger row. Fill the content in between — that part is yours."),
        "body": """<div class="cmd-list">
      <div class="cmd">
        <span class="arrow">→</span>
        <code>python scripts/one_shot.py scaffold --brief "your page" --direction "measured technical"</code>
        <span class="note">decisions + structure</span>
        <button class="copy-btn" data-copy='python scripts/one_shot.py scaffold --brief "your page" --direction "measured technical"'>copy</button>
      </div>
      <div class="cmd">
        <span class="arrow">→</span>
        <code>python scripts/section_scan.py --all</code>
        <span class="note">measure the corpus</span>
        <button class="copy-btn" data-copy="python scripts/section_scan.py --all">copy</button>
      </div>
      <div class="cmd">
        <span class="arrow">→</span>
        <code>python scripts/one_shot.py grade --label "R1 one-shot"</code>
        <span class="note">grading</span>
        <button class="copy-btn" data-copy='python scripts/one_shot.py grade --label "R1 one-shot"'>copy</button>
      </div>
    </div>
    <div class="start-note">0 credits · no cloud · no accounts · the corpus stays on your disk</div>""",
    },
    "pricing": {
        "title": "What one page costs",
        "intro": ("Every figure below divides by zero — the rate is checkable because it is zero. "
                  "The pricing band earned its place the measured way: it was one of the most "
                  "common band types in the scan."),
        "body": """<div class="stat-grid">
      <div class="stat-card">
        <div class="stat-num">0<span class="unit">credits</span></div>
        <div class="stat-label">Per build</div>
        <div class="stat-note">Every tool is free — the register quotes the price list before a build starts: zero.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">1<span class="unit">library</span></div>
        <div class="stat-label">Per user</div>
        <div class="stat-note">One folder on your disk. No accounts, no Stripe, no expiry — pack credits never expire because there are none.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">∞<span class="unit">builds</span></div>
        <div class="stat-label">Per month</div>
        <div class="stat-note">Nothing resets at the end of a billing period, because there is no billing period. The ledger enforces it with a constraint: there is nothing to reset.</div>
      </div>
    </div>
    <div class="start-note">WHAT ONE PAGE COSTS: 0 CREDITS · LOCAL-FIRST · THE RATE IS CHECKABLE BECAUSE IT IS ZERO</div>""",
    },
}
