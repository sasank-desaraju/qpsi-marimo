Log for AI agents to update with what they do.


2026-03-17:

- Created `notebooks/hypothesis_power.py` — Marimo app for Syllabus Topic 1: Hypothesis Testing, Power, and p-values.
  - Interactive sliders for sample size (n), effect size (Cohen's d), and significance level (α).
  - Dynamic visualization of null vs alternative sampling distributions with shaded α, β, and power regions.
  - Power vs sample size curve with 80% power reference line.
  - Anchor paper: SPRINT Trial (2015). Includes board-relevant questions.

- Created `notebooks/diagnostic_testing.py` — Marimo app for Syllabus Topic 2: Diagnostic Testing: The 2x2 Matrix & Prevalence.
  - 1,000-dot interactive population grid showing TP/FP/TN/FN.
  - Sliders for sensitivity, specificity, and prevalence.
  - Dynamic 2x2 confusion matrix heatmap.
  - PPV/NPV vs prevalence curve showing the "prevalence trap."
  - Anchor paper: D-dimer / PIOPED II. Includes SnNOut/SpPIn mnemonic and board questions.

- Created `notebooks/likelihood_ratios.py` — Syllabus Topic 3: Likelihood Ratios & Fagan's Nomogram.
  - Fagan's nomogram visualization with LR+ (green) and LR- (red) lines.
  - Pre-test → Post-test probability sweep chart.
  - Anchor paper: JAMA Rational Clinical Examination series (WARNING: specific JVP article PMID not verified).

- Created `notebooks/survival_analysis.py` — Syllabus Topic 4: Kaplan-Meier & Hazard Ratios.
  - Simulated survival data with exponential model and censoring.
  - KM curves with censor tick marks and number-at-risk table.
  - Anchor paper: EMPA-REG OUTCOME (PMID 26378978, DOI verified).

- Created `notebooks/confidence_intervals.py` — Syllabus Topic 5: Precision vs Significance.
  - Forest plot of 20 simulated trials with adjustable sample size and effect.
  - CI width vs sample size curve showing 1/sqrt(n) relationship.
  - Anchor paper: ISIS-2 (PMID 2899772, DOI not fully verified — linked PubMed only).

- Created `notebooks/measures_of_association.py` — Syllabus Topic 6: OR vs RR vs NNT.
  - Interactive bar charts for risk comparison.
  - NNT vs baseline risk curve showing NNT explosion at low prevalence.
  - OR vs RR divergence plot across baseline risks.
  - Anchor paper: WOSCOPS (PMID 7566020, DOI verified).

- Created `notebooks/roc_curves.py` — Syllabus Topic 7: ROC Curves & Optimal Cutoff.
  - Dual distribution plot with sliding cutoff.
  - Full ROC curve with current operating point and AUC.
  - Anchor paper: Cardiac Troponin (WARNING: specific 1990s troponin paper not verified — no link added).

- Created `notebooks/screening_bias.py` — Syllabus Topic 8: Lead-Time and Length-Time Bias.
  - Gantt-chart timeline showing lead-time bias with identical death dates.
  - Length-time bias simulation with screening detection rates by disease aggressiveness.
  - Anchor paper: NLST (PMID 21714641, DOI verified).

- Created `notebooks/forest_plots.py` — Syllabus Topic 9: Forest Plots & Heterogeneity.
  - Interactive forest plot with toggleable studies (checkboxes).
  - Pooled diamond and I² update in real time.
  - Anchor paper: Cochrane Reviews (WARNING: specific albumin review not verified — no link added).

- Created `notebooks/correlation_regression.py` — Syllabus Topic 10: Correlation vs Regression.
  - Scatterplot with regression line, r, R², slope statistics.
  - R² vs noise level curve.
  - Anchor paper: Framingham Heart Study (WARNING: specific original paper not verified — no link added).

### Citations — All Now Verified:
- Topic 3: Wang CS et al., JAMA 2005 — PMID 16234501, DOI 10.1001/jama.294.15.1944 ✓
- Topic 7: Katus HA et al., Clin Chem 1991 — PMID 2049849 ✓
- Topic 9: Albumin Reviewers, Cochrane 2004/2011 — PMID 17120476 ✓
- Topic 10: Kannel WB et al., Ann Intern Med 1961 — PMID 13751193 ✓
(Previously unverified; confirmed on second round of web searches.)

- Added `mo.accordion()` with anchor paper access to all 10 notebooks:
  - SPRINT (notebook 1) and NLST (notebook 8): embedded PDF via `mo.pdf()` from PMC open-access PDFs
  - All other notebooks: collapsible accordion with PubMed + journal links (paywalled journals block iframe embedding)
  - All accordions use `lazy=True` so PDFs don't load until the user expands them
- Updated notebook 2 (diagnostic_testing) with verified PIOPED II citation (PMID 16738268, DOI 10.1056/NEJMoa052367)

### Specs Implementation (planning/specs.md):

- Created `.github/workflows/deploy.yml` — GitHub Actions workflow for deploying to GitHub Pages
  - Triggers on push to main or manual dispatch
  - Uses uv + Python 3.10 to run the build script
  - Deploys via actions/deploy-pages@v4

- Created `.github/scripts/build.py` — Build script for WASM export
  - Exports all notebooks in notebooks/ as apps (run mode, code hidden)
  - Pins marimo==0.21.0 via `uvx marimo==0.21.0`
  - Uses `--sandbox` flag so PEP 723 inline deps are installed per-notebook
  - Generates index.html from Jinja2 template
  - Creates .nojekyll file for GitHub Pages

- Created `templates/index.html.j2` — Tailwind-styled landing page for QPSI
  - Grid layout of all notebooks with "Open Notebook" links
  - Branded for UF QPSI with contact info

- Created `examples/iframe_embed.html` — iframe embedding demo
  - Shows how notebooks would look embedded in the QPSI Knowledgebase
  - Includes code snippets for embedding any notebook
  - Documents loading="lazy" and allow="cross-origin-isolated" attributes

- Rewrote `README.md` — Developer-oriented documentation
  - Quick start with uv installation and running notebooks
  - Project structure overview
  - Deployment guide (GitHub Pages setup, manual build)
  - iframe embedding instructions
  - Development conventions (Altair, hide_code, PEP 723)

- Set `hide_code=True` on ALL @app.cell decorators across all 10 notebooks
  - Previously only accordion and feedback cells had it
  - Now all cells hide code by default since audience is non-technical

### Deployment Assessment:

- Created `ai/deployment_AI.md` — comprehensive assessment of deployment options
  - Analyzed 5 options: GitHub Pages WASM, molab, self-hosted WASM, HiPerGator, full server deploy
  - Discovered QPSI Knowledgebase runs WordPress/Divi — iframe embedding is straightforward via Divi's Code module
  - Recommended strategy: GitHub Pages (primary) + iframe into QPSI WordPress (integration) + molab badges (supplementary)
  - Flagged ADA compliance as main open concern — recommended UF accessibility team review before full rollout
  - All our packages (Altair, NumPy, Pandas, SciPy) confirmed Pyodide-compatible for WASM

