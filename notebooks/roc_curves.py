# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.21.0",
#     "altair==5.5.0",
#     "numpy==2.3.2",
#     "pandas==2.3.2",
#     "scipy>=1.10.0",
# ]
# ///

import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium", app_title="ROC Curves & The Optimal Cutoff")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import altair as alt
    from scipy import stats as sp_stats
    return alt, mo, np, pd, sp_stats


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ROC Curves & The "Optimal" Cutoff

    Every diagnostic test measures a continuous biomarker and applies a **cutoff** to classify patients
    as positive or negative. But where should we draw the line?

    - Move the cutoff **left** → Catch more disease (↑ sensitivity) but also more false positives (↓ specificity)
    - Move the cutoff **right** → Fewer false positives (↑ specificity) but miss more disease (↓ sensitivity)

    The **ROC curve** traces this trade-off across all possible cutoffs. The **Area Under the Curve (AUC)**
    summarizes overall test performance in a single number.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Adjust the distributions of the biomarker in diseased vs. non-diseased populations,
    then slide the cutoff to see how sensitivity and specificity change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    healthy_mean_slider = mo.ui.slider(
        start=0, stop=40, value=20, step=1,
        label="Healthy Mean", show_value=True
    )
    sick_mean_slider = mo.ui.slider(
        start=10, stop=60, value=35, step=1,
        label="Diseased Mean", show_value=True
    )
    spread_slider = mo.ui.slider(
        start=2, stop=15, value=6, step=0.5,
        label="Spread (SD for both)", show_value=True
    )
    mo.hstack([healthy_mean_slider, sick_mean_slider, spread_slider])
    return healthy_mean_slider, sick_mean_slider, spread_slider


@app.cell(hide_code=True)
def _(healthy_mean_slider, np, pd, sick_mean_slider, sp_stats, spread_slider):
    # Generate the two distributions
    healthy_mu = healthy_mean_slider.value
    sick_mu = sick_mean_slider.value
    sigma = spread_slider.value

    # Dense x range for smooth curves
    x_min = min(healthy_mu, sick_mu) - 4 * sigma
    x_max = max(healthy_mu, sick_mu) + 4 * sigma
    x_vals = np.linspace(x_min, x_max, 500)

    healthy_pdf = sp_stats.norm.pdf(x_vals, healthy_mu, sigma)
    sick_pdf = sp_stats.norm.pdf(x_vals, sick_mu, sigma)

    dist_df = pd.DataFrame({
        'Biomarker Value': np.concatenate([x_vals, x_vals]),
        'Density': np.concatenate([healthy_pdf, sick_pdf]),
        'Population': ['Healthy'] * len(x_vals) + ['Diseased'] * len(x_vals)
    })
    return dist_df, healthy_mu, sick_mu, sigma, x_max, x_min


@app.cell(hide_code=True)
def _(mo, x_max, x_min):
    cutoff_slider = mo.ui.slider(
        start=int(x_min), stop=int(x_max), value=int((x_min + x_max) / 2), step=1,
        label="Cutoff Value", show_value=True
    )
    mo.hstack([cutoff_slider])
    return (cutoff_slider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Two Distributions

    The **blue** distribution is the biomarker in **healthy** people; **orange** is **diseased**.
    The red vertical line is the cutoff.
    - Everything to the **right** of the cutoff is called "positive"
    - The overlap region is where diagnostic errors occur
    """)
    return


@app.cell(hide_code=True)
def _(alt, cutoff_slider, dist_df, mo, pd):
    # Distribution plot with cutoff
    dist_chart = alt.Chart(dist_df).mark_area(opacity=0.5).encode(
        x=alt.X('Biomarker Value:Q'),
        y=alt.Y('Density:Q'),
        color=alt.Color('Population:N', scale=alt.Scale(
            domain=['Healthy', 'Diseased'],
            range=['#1f77b4', '#ff7f0e']
        ))
    ).properties(width=700, height=300, title='Biomarker Distributions')

    cutoff_line = alt.Chart(pd.DataFrame({'x': [cutoff_slider.value]})).mark_rule(
        color='red', strokeWidth=2.5, strokeDash=[5, 3]
    ).encode(x='x:Q')

    cutoff_label = alt.Chart(pd.DataFrame({
        'x': [cutoff_slider.value], 'y': [0], 'label': [f'Cutoff = {cutoff_slider.value}']
    })).mark_text(
        align='left', dx=5, dy=-15, fontSize=11, color='red'
    ).encode(x='x:Q', y='y:Q', text='label:N')

    _dist_combined = dist_chart + cutoff_line + cutoff_label
    mo.vstack([
        _dist_combined,
        mo.accordion({"View data table": mo.ui.table(dist_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">Biomarker distribution chart for healthy and diseased populations with cutoff at {cutoff_slider.value}.</div>')
    ])
    return


@app.cell(hide_code=True)
def _(cutoff_slider, healthy_mu, sigma, sick_mu, sp_stats):
    # Calculate sensitivity and specificity at current cutoff
    cutoff = cutoff_slider.value

    # Test positive = biomarker > cutoff (assuming disease has higher values)
    sensitivity = 1 - sp_stats.norm.cdf(cutoff, sick_mu, sigma)
    specificity = sp_stats.norm.cdf(cutoff, healthy_mu, sigma)
    fpr = 1 - specificity

    ppv_text = ""
    return cutoff, fpr, sensitivity, specificity


@app.cell(hide_code=True)
def _(cutoff, fpr, mo, sensitivity, specificity):
    mo.md(f"""
    ## At Cutoff = {cutoff}

    | Metric | Value |
    |--------|-------|
    | **Sensitivity** (True Positive Rate) | **{sensitivity:.1%}** |
    | **Specificity** (True Negative Rate) | **{specificity:.1%}** |
    | **False Positive Rate** (1 − Specificity) | **{fpr:.1%}** |

    The current operating point is marked as a **red dot** on the ROC curve below.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The ROC Curve

    Each point on the curve represents a different cutoff value. The curve traces
    sensitivity (y-axis) vs. false positive rate (x-axis) across all possible thresholds.

    - **Upper-left corner** = perfect test (100% sensitivity, 0% FPR)
    - **Diagonal line** = random guessing (AUC = 0.5)
    - **AUC** = probability that the test correctly ranks a random diseased patient higher than a random healthy one
    """)
    return


@app.cell(hide_code=True)
def _(alt, fpr, healthy_mu, mo, np, pd, sensitivity, sigma, sick_mu, sp_stats):
    # Build ROC curve
    cutoff_range = np.linspace(
        min(healthy_mu, sick_mu) - 4 * sigma,
        max(healthy_mu, sick_mu) + 4 * sigma,
        200
    )
    roc_data = []
    for _c in cutoff_range:
        _sens = 1 - sp_stats.norm.cdf(_c, sick_mu, sigma)
        _spec = sp_stats.norm.cdf(_c, healthy_mu, sigma)
        roc_data.append({
            'Cutoff': float(_c),
            'Sensitivity (TPR)': _sens,
            'False Positive Rate': 1 - _spec
        })
    roc_df = pd.DataFrame(roc_data)

    # Calculate AUC using trapezoidal rule (sort by FPR)
    roc_sorted = roc_df.sort_values('False Positive Rate')
    auc_val = float(np.trapz(
        roc_sorted['Sensitivity (TPR)'].values,
        roc_sorted['False Positive Rate'].values
    ))

    roc_line = alt.Chart(roc_df).mark_line(
        color='#1f77b4', strokeWidth=2.5
    ).encode(
        x=alt.X('False Positive Rate:Q', title='False Positive Rate (1 − Specificity)',
                 scale=alt.Scale(domain=[0, 1])),
        y=alt.Y('Sensitivity (TPR):Q', title='Sensitivity (True Positive Rate)',
                 scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip('Cutoff:Q', format='.1f'),
            alt.Tooltip('Sensitivity (TPR):Q', format='.1%'),
            alt.Tooltip('False Positive Rate:Q', format='.1%')
        ]
    ).properties(
        width=500, height=500,
        title=f'ROC Curve (AUC = {auc_val:.3f})'
    )

    # Diagonal reference line
    diag_df = pd.DataFrame({'x': [0, 1], 'y': [0, 1]})
    diag_line = alt.Chart(diag_df).mark_line(
        strokeDash=[5, 3], color='gray'
    ).encode(x='x:Q', y='y:Q')

    # Current operating point
    current_point = alt.Chart(pd.DataFrame({
        'False Positive Rate': [fpr],
        'Sensitivity (TPR)': [sensitivity]
    })).mark_point(
        color='red', size=150, filled=True
    ).encode(
        x='False Positive Rate:Q',
        y='Sensitivity (TPR):Q',
        tooltip=[
            alt.Tooltip('Sensitivity (TPR):Q', format='.1%'),
            alt.Tooltip('False Positive Rate:Q', format='.1%')
        ]
    )

    roc_chart = roc_line + diag_line + current_point
    mo.vstack([
        roc_chart,
        mo.accordion({"View data table": mo.ui.table(roc_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">ROC curve with AUC = {auc_val:.3f}. Current operating point: sensitivity {sensitivity:.1%}, false positive rate {fpr:.1%}.</div>')
    ])
    return (auc_val,)


@app.cell(hide_code=True)
def _(auc_val, mo):
    mo.md(f"""
    ## AUC = {auc_val:.3f}

    | AUC Range | Interpretation |
    |-----------|---------------|
    | 0.90–1.00 | Excellent |
    | 0.80–0.89 | Good |
    | 0.70–0.79 | Fair |
    | 0.60–0.69 | Poor |
    | 0.50–0.59 | No better than chance |

    **The AUC does NOT depend on the cutoff** — it reflects the inherent discriminative ability
    of the biomarker. Changing the cutoff moves you along the ROC curve but doesn't change the curve itself.

    **What changes AUC?** Only the separation between the two distributions (controlled by the means and spread sliders above).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Verified: PMID 2049849, Katus et al., Clin Chem, 1991
    mo.md(r"""
    ## Anchor Paper: Cardiac Troponin T for MI Diagnosis

    **Katus HA, Remppis A, Looser S, Hallermeier K, Scheffold T, Kübler W.** "Cardiac troponin T
    in diagnosis of acute myocardial infarction." *Clin Chem.* 1991;37(6):845-52.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/2049849/)

    **The study:** Examined troponin T concentrations in 72 patients with confirmed MI. Found that
    sensitivity for detecting MI was **100% from 10 to 120 hours** after symptom onset.

    **Why this paper is perfect for ROC curves:**
    - The fundamental question was: where do you set the "upper limit of normal" for troponin?
    - Too low → many false positives (patients with minor myocardial injury, renal failure, etc.)
    - Too high → miss small but clinically significant MIs
    - The **99th percentile** of a healthy reference population was later adopted as the cutoff (per universal MI definition)
    - This is explicitly a **ROC-curve-informed decision** — choosing a threshold that maximizes clinical utility

    **Key teaching points:**
    - **High-sensitivity troponin (hs-cTn)** assays shifted the ROC curve upward by improving discrimination
    - The "optimal" cutoff still depends on context: ED rule-out vs. ICU monitoring
    - Better test → higher AUC → but the cutoff choice remains a clinical judgment
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | Definition | Clinical Relevance |
    |---------|------------|-------------------|
    | **ROC Curve** | Sens vs (1−Spec) across cutoffs | Visualizes the trade-off |
    | **AUC** | Area under the ROC curve | Overall test discrimination |
    | **Sensitivity** | P(Test+ \| Disease+) | High for screening tests |
    | **Specificity** | P(Test− \| Disease−) | High for confirmatory tests |
    | **Optimal cutoff** | Depends on clinical context! | No single "best" point |
    | **Youden's J** | Max(Sens + Spec − 1) | One approach to "optimal" cutoff |

    **Choosing a cutoff depends on clinical goals:**
    - **Screening test** (don't miss disease) → favor sensitivity → move cutoff left
    - **Confirmatory test** (don't over-treat) → favor specificity → move cutoff right
    - **Equal costs of errors** → Youden's index (maximize Sens + Spec)

    ## Questions

    1. Move both means closer together. What happens to the AUC? Why?

    2. Set the cutoff very far left. What are the sensitivity and specificity? Is this useful clinically?

    3. If AUC = 0.95 vs. AUC = 0.75, which test would you prefer for a screening program? For a confirmatory test?

    4. Why can two tests with different AUCs still be equally useful at a specific cutoff point?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Katus et al. — 1991 Clin Chem, no PMC PDF
    # Verified: PMID 2049849
    mo.accordion(
        {
            "Read the Anchor Paper: Troponin T for MI Diagnosis (1991)": mo.md("""
**Katus HA, Remppis A, Looser S, et al.** "Cardiac troponin T in diagnosis of acute myocardial
infarction." *Clin Chem.* 1991;37(6):845-52.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/2049849/)

*This article may require institutional access through Clinical Chemistry / Oxford Academic.*
""")
        },
        lazy=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Please send any feedback to Sasank at sasank.desaraju@ufl.edu.

    He'd love to hear what's helpful, not helpful, and any suggestions for future notebooks!
    """)
    return


if __name__ == "__main__":
    app.run()
