# QPSI Biostatistics — Interactive Marimo Notebooks

Interactive biostatistics notebooks for graduate medical education at the University of Florida's Quality and Patient Safety Initiative (QPSI).

Built with [marimo](https://marimo.io), a reactive Python notebook framework. Notebooks run in the browser via WebAssembly — no server required for the deployed version.

## Notebooks

| # | Topic | File |
|---|-------|------|
| 1 | Hypothesis Testing, Power, and p-values | `notebooks/hypothesis_power.py` |
| 2 | Diagnostic Testing: The 2x2 Matrix & Prevalence | `notebooks/diagnostic_testing.py` |
| 3 | Likelihood Ratios & Fagan's Nomogram | `notebooks/likelihood_ratios.py` |
| 4 | Kaplan-Meier & Hazard Ratios | `notebooks/survival_analysis.py` |
| 5 | Confidence Intervals: Precision vs Significance | `notebooks/confidence_intervals.py` |
| 6 | OR vs RR vs NNT | `notebooks/measures_of_association.py` |
| 7 | ROC Curves & Optimal Cutoff | `notebooks/roc_curves.py` |
| 8 | Lead-Time and Length-Time Bias | `notebooks/screening_bias.py` |
| 9 | Forest Plots & Heterogeneity | `notebooks/forest_plots.py` |
| 10 | Correlation vs Regression | `notebooks/correlation_regression.py` |

## Quick Start

### Prerequisites

- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — a fast Python package manager

Install uv (if you don't have it):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Run a notebook locally

Each notebook is a standalone `.py` file with its dependencies declared inline (PEP 723). You don't need to install anything globally — `uv` handles it.

```bash
# Run any notebook as an interactive app
uv run marimo run notebooks/hypothesis_power.py

# Or open in edit mode to see/modify the code
uv run marimo edit notebooks/hypothesis_power.py
```

The first run will install dependencies automatically. After that, notebooks start in seconds.

### Run all notebooks (development server)

```bash
uv run marimo edit notebooks/
```

This opens a file browser where you can pick any notebook to edit.

## Project Structure

```
qpsi-marimo/
├── notebooks/              # The 10 biostatistics notebooks
├── examples/               # Reference examples and iframe demo
│   └── iframe_embed.html   # Shows how to embed in the QPSI Knowledgebase
├── templates/              # Jinja2 template for the GitHub Pages index
├── .github/
│   ├── workflows/deploy.yml   # GitHub Actions workflow for Pages deployment
│   └── scripts/build.py       # Build script that exports notebooks to WASM
├── planning/               # Syllabus and specs
├── ai/                     # Context and logs for AI-assisted development
└── pyproject.toml
```

## Deployment

Notebooks are automatically deployed to GitHub Pages on every push to `main`.

### How it works

1. GitHub Actions runs `.github/scripts/build.py`
2. The build script exports each notebook to HTML/WebAssembly using `marimo export html-wasm`
3. Notebooks are exported in **run mode** with code hidden (audience is non-technical)
4. A landing page (`index.html`) is generated from the Jinja2 template
5. Everything is deployed to GitHub Pages

### Manual build (for testing locally)

```bash
uv run .github/scripts/build.py
```

This creates a `_site/` directory with the exported notebooks. Open `_site/index.html` in a browser to preview.

### GitHub Pages setup

In your repo settings:

1. Go to **Settings > Pages**
2. Under **Build and deployment**, select **GitHub Actions** as the source
3. Push to `main` — the workflow will run automatically

## Embedding in the QPSI Knowledgebase

After deployment, embed any notebook with an iframe:

```html
<iframe
  src="https://sasank-desaraju.github.io/qpsi-marimo/notebooks/hypothesis_power.html"
  style="width: 100%; height: 80vh; border: none;"
  loading="lazy"
  allow="cross-origin-isolated"
></iframe>
```

See `examples/iframe_embed.html` for a full working example.

## Development Guide

### Adding a new notebook

1. Create a new `.py` file in `notebooks/`
2. Add the PEP 723 inline metadata at the top:
   ```python
   # /// script
   # requires-python = ">=3.10"
   # dependencies = [
   #     "marimo>=0.21.0",
   #     "altair==5.5.0",
   #     "numpy==2.3.2",
   #     "pandas==2.3.2",
   # ]
   # ///
   ```
3. Use `marimo edit` to develop interactively:
   ```bash
   uv run marimo edit notebooks/my_new_notebook.py
   ```
4. Push to `main` — it will be automatically built and deployed

### Conventions

- **Altair** for all visualizations (not matplotlib)
- **`hide_code=True`** on all `@app.cell` decorators (audience is non-technical)
- Each notebook ends with a feedback cell pointing to `sasank.desaraju@ufl.edu`
- Anchor papers use `mo.accordion()` with `lazy=True` for embedded PDFs or links

### Useful commands

```bash
# Run a single notebook as an app (what end users see)
uv run marimo run notebooks/hypothesis_power.py

# Edit a notebook (full IDE with code visible)
uv run marimo edit notebooks/hypothesis_power.py

# Check all notebooks for errors
uv run marimo check notebooks/

# Export a single notebook to HTML/WASM
uv run marimo export html-wasm notebooks/hypothesis_power.py -o output/ --mode run
```

## Tech Stack

- **[marimo](https://marimo.io)** 0.21.0 — Reactive Python notebooks
- **[Altair](https://altair-viz.github.io/)** — Declarative statistical visualization
- **[uv](https://docs.astral.sh/uv/)** — Fast Python package management
- **GitHub Pages** — Static hosting via WebAssembly export
