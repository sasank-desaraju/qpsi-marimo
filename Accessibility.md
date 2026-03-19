# Accessibility Compliance

This document describes the accessibility features implemented across all QPSI biostatistics notebooks, guided by feedback from the QPSI team and standard web accessibility practices.

## 1. SVG Chart Output

**Status: Compliant by default**

All interactive charts use [Altair](https://altair-viz.github.io/), which renders as **SVG** rather than HTML Canvas. SVG elements are part of the DOM and can be read by assistive technologies, unlike canvas-rendered charts which appear as opaque images.

No additional changes were needed for this requirement.

## 2. Table Versions of Charts

**Status: Implemented**

Every chart in every notebook includes a collapsible **"View data table"** accordion directly below it. When expanded, it displays the chart's underlying data as an interactive table (`mo.ui.table`), which can be sorted and searched.

This allows screen reader users to access the data behind each visualization in a structured, tabular format. For sighted users, the accordion is collapsed by default — it appears as a thin clickable header and does not clutter the view.

**Notebooks updated (22 chart cells total):**

| Notebook | Charts with data tables |
|----------|----------------------|
| Hypothesis Testing & Power | 2 (distribution curves, power vs sample size) |
| Diagnostic Testing | 3 (dot grid, PPV/NPV curve, confusion matrix) |
| Likelihood Ratios | 2 (Fagan's nomogram, post-test probability sweep) |
| Survival Analysis | 2 (KM curves, number at risk) |
| Confidence Intervals | 2 (forest plot, CI width curve) |
| Measures of Association | 3 (risk bars, NNT curve, OR vs RR) |
| ROC Curves | 2 (distributions, ROC curve) |
| Screening Bias | 2 (lead-time Gantt, detection rate bars) |
| Forest Plots | 1 (interactive forest plot) |
| Correlation & Regression | 2 (scatterplot, R² vs noise) |

## 3. Keyboard-Accessible Inputs

**Status: Compliant by default**

All interactive controls (sliders, dropdowns, checkboxes) are built with [marimo's UI elements](https://docs.marimo.io/api/inputs/), which render as standard HTML form elements. These are natively keyboard-accessible:

- **Tab** to navigate between controls
- **Arrow keys** to adjust slider values
- **Space/Enter** to toggle checkboxes
- **Arrow keys** to navigate dropdown options

No additional changes were needed for this requirement.

## 4. ARIA Live Regions for Dynamic Content

**Status: Implemented**

Every chart cell includes a **visually hidden** `<div>` element with the following ARIA attributes:

- `aria-live="polite"` — announces changes without interrupting the user
- `aria-atomic="true"` — reads the entire summary when updated, not just the changed portion

These elements contain a brief, dynamically-generated text summary of the current chart state. For example:

> "Forest plot of 20 simulated trials with true effect 0.30 at 95% confidence level. 15 of 20 trials reached statistical significance."

The summaries update reactively when users adjust slider values, providing screen reader users with a text description of what changed in the visualization.

The elements use the standard "sr-only" CSS pattern (`position:absolute; clip:rect(0,0,0,0); ...`) so they are **completely invisible** to sighted users while remaining accessible to screen readers.

## Visual Impact

These accessibility features were designed to have **minimal visual impact** on the notebook experience for sighted users:

- **SVG output**: No visual change (already the default)
- **Data tables**: Collapsed accordion headers add ~20px height below each chart
- **Keyboard access**: No visual change (already the default)
- **ARIA summaries**: Completely invisible (visually hidden)

## Remaining Items / Future Work

- **Manual screen reader testing**: The ARIA summaries and data tables should be tested with actual screen readers (NVDA, VoiceOver, JAWS) to verify the experience is smooth.
- **Color contrast**: Altair chart colors were chosen for visual clarity but have not been formally audited against WCAG contrast ratios. This may be worth reviewing.
- **iframe embedding**: When notebooks are embedded via iframe in the QPSI Knowledgebase (WordPress/Divi), the iframe itself should have a descriptive `title` attribute for screen readers (e.g., `title="Hypothesis Testing Interactive Notebook"`).
