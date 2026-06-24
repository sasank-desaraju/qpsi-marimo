# QPSI Marimo Notebook Theming — Design

*Date: 2026-06-24*

## Goal

Restyle the 10 biostatistics marimo notebooks so their accent colors and
typography align with the QPSI Knowledgebase (https://knowledge.qpsi.med.ufl.edu/),
so embedded iframes blend visually into the host site. **Accent theming** only —
the notebooks keep marimo's clean light layout; we recolor accents and match the
heading font, we do not add site chrome (nav/logo/footer) inside the notebook.

## Brand palette (extracted from the live Divi stylesheet)

Source: `et-core-unified-2.min.css` on the live site, plus the page's inline styles.

| Token | Hex | Role |
|-------|-----|------|
| UF Blue (primary) | `#0021A5` | Headings, links, control accents — the site's dominant brand color (used on all `h2`/`h3`) |
| Deep navy | `#002657` | Secondary dark accent, visited links, table-header tint |
| Body text | `#262626` | Default text (marimo default is close; left as-is) |
| Gold | `#F2A900` | Warm accent (charts, decorative) |
| Orange | `#ED6B21` | Secondary warm accent / second chart category |
| Crimson | `#cf2e2e` | Alert/highlight (already used as chart "red" lines) |

Fonts: site uses **`Anybody`** (Google font) for headings/body; Adobe Typekit
also loads Myriad Pro. We adopt **Anybody for headings** to match.

Notes:
- We deliberately do **not** use Divi's default link blue `#2ea3f2` — it fails
  WCAG AA contrast on white. `#0021A5` on white is ~11:1 (passes AA/AAA).
- Blue ↔ orange chart pairing is colorblind-safe (deuteranopia/protanopia).

## Mechanism

marimo exposes per-notebook theming via app config, and both files are bundled
into the WASM HTML export automatically — **no build-script changes needed**:

- `marimo.App(..., css_file="qpsi_theme.css", html_head_file="qpsi_head.html")`
  — paths are relative to the notebook file (all live in `notebooks/`).

marimo scopes its theme tokens on `:root` (`--primary`, `--link`, `--accent`,
`--marimo-heading-font`, …) and injects custom CSS **after** its own styles, so a
`:root { --primary: #0021A5; … }` override wins cleanly.

### Files

1. **`notebooks/qpsi_theme.css`** (new, shared) — overrides:
   - `--primary`, `--primary-foreground` → UF Blue / white (sliders, buttons, checkboxes)
   - `--link`, `--link-visited` → UF Blue / navy
   - `--accent`, `--accent-foreground` → light blue tint / UF Blue
   - markdown headings (`h1`–`h3`) color → UF Blue
   - table / accordion header tint → navy
2. **`notebooks/qpsi_head.html`** (new, shared) — loads the Anybody font and sets
   `--marimo-heading-font: 'Anybody', sans-serif`.
3. **All 10 notebooks** — add `css_file` + `html_head_file` to `marimo.App(...)`.

### Chart palette (layer 2) — DEFERRED

Deferred at user request (2026-06-24): recoloring charts requires going into each
notebook's chart cells. Not done now. When picked up later:

- Register a lightweight Altair theme in each notebook's setup cell that sets the
  default categorical `range.category` to the brand palette
  `['#0021A5', '#ED6B21', '#82C0C7', '#F2A900', '#6B7280']`.
- Swap hardcoded category literals (e.g. `#1f77b4` / `#ff7f0e`) → UF navy / orange.
- Keep semantic `red` cutoff/alert rules as-is (meaning, not branding).

## Out of scope

- Site chrome (nav/logo/footer) inside notebooks.
- The GitHub Pages `index.html` landing page (could be branded later; easy follow-up).
- Restyling the iframe wrapper beyond fixing `#003087` → `#0021A5` for consistency.

## Verification

- Build locally with the existing build script; confirm exported HTML inlines the
  custom CSS and the Anybody font link.
- Serve `_site/` on localhost and visually confirm headings/links/controls are UF
  Blue and the heading font matches.
- Spot-check contrast (links/headings on white ≥ 4.5:1).

## Cleanup / logging

- Fix `examples/iframe_embed.html` `#003087` → `#0021A5`.
- Update `ai/LOG.md` per `ai/CONTEXT.md` convention.
