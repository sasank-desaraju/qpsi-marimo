# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.21.0",
#     "altair==5.5.0",
#     "numpy==2.3.2",
#     "pandas==2.3.2",
# ]
# ///

import marimo

__generated_with = "0.21.0"
app = marimo.App(width="medium", app_title="Systematic Reviews: Forest Plots & Heterogeneity")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import pandas as pd
    import altair as alt
    return alt, mo, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Systematic Reviews: Forest Plots & Heterogeneity

    A **systematic review with meta-analysis** pools results from multiple studies to get a more
    precise overall estimate. The **forest plot** is the standard visualization.

    But pooling is only meaningful if the studies are measuring roughly the same thing.
    **Heterogeneity** ($I^2$) tells us how much the variability across studies is due to *real differences*
    vs. random chance.

    In this notebook, you can toggle individual studies on and off and watch the pooled estimate
    (the "diamond") and $I^2$ update in real time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Set the number of studies and how much they vary. Then use the checkboxes to include/exclude studies.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    n_studies_slider = mo.ui.slider(
        start=5, stop=15, value=8, step=1,
        label="Number of Studies", show_value=True
    )
    true_effect_slider = mo.ui.slider(
        start=-0.5, stop=1.5, value=0.4, step=0.05,
        label="True Mean Effect (log-OR)", show_value=True
    )
    heterogeneity_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.3, step=0.05,
        label="Between-Study SD (τ)", show_value=True
    )
    mo.hstack([n_studies_slider, true_effect_slider, heterogeneity_slider])
    return heterogeneity_slider, n_studies_slider, true_effect_slider


@app.cell(hide_code=True)
def _(heterogeneity_slider, n_studies_slider, np, pd, true_effect_slider):
    # Generate simulated study data
    np.random.seed(42)
    _k = n_studies_slider.value
    _mu = true_effect_slider.value
    _tau = heterogeneity_slider.value

    studies = []
    for i in range(_k):
        # True effect for this study (random effects)
        theta_i = np.random.normal(_mu, _tau)
        # Within-study SE (varies by study size)
        n_i = np.random.randint(50, 500)
        se_i = np.random.uniform(0.1, 0.5) * np.sqrt(200 / n_i)
        # Observed effect
        y_i = np.random.normal(theta_i, se_i)
        studies.append({
            'Study': f'Study {i + 1}',
            'Effect': round(y_i, 3),
            'SE': round(se_i, 3),
            'CI Lower': round(y_i - 1.96 * se_i, 3),
            'CI Upper': round(y_i + 1.96 * se_i, 3),
            'N': n_i,
            'Weight': round(1 / se_i ** 2, 1)
        })

    studies_df = pd.DataFrame(studies)
    return (studies_df,)


@app.cell(hide_code=True)
def _(mo, studies_df):
    # Create checkboxes for each study
    study_toggles = mo.ui.array([
        mo.ui.checkbox(label=f"{row['Study']} (n={row['N']}, effect={row['Effect']:.2f})", value=True)
        for _, row in studies_df.iterrows()
    ])
    mo.md("### Include/Exclude Studies")
    return (study_toggles,)


@app.cell(hide_code=True)
def _(study_toggles):
    study_toggles
    return


@app.cell(hide_code=True)
def _(np, studies_df, study_toggles):
    # Filter to included studies and compute meta-analysis
    included = [i for i, toggle in enumerate(study_toggles.value) if toggle]

    if len(included) == 0:
        active_df = studies_df.iloc[0:0]  # empty
        pooled_effect = 0
        pooled_ci_low = 0
        pooled_ci_high = 0
        i_squared = 0
        q_stat = 0
    else:
        active_df = studies_df.iloc[included].copy()

        # Inverse-variance weighted fixed-effects meta-analysis
        weights = 1 / active_df['SE'].values ** 2
        pooled_effect = np.sum(weights * active_df['Effect'].values) / np.sum(weights)
        pooled_se = 1 / np.sqrt(np.sum(weights))
        pooled_ci_low = pooled_effect - 1.96 * pooled_se
        pooled_ci_high = pooled_effect + 1.96 * pooled_se

        # Cochran's Q and I²
        k = len(active_df)
        q_stat = np.sum(weights * (active_df['Effect'].values - pooled_effect) ** 2)
        df = max(k - 1, 1)
        i_squared = max(0, (q_stat - df) / q_stat * 100) if q_stat > 0 else 0
    return active_df, i_squared, pooled_ci_high, pooled_ci_low, pooled_effect, q_stat


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Forest Plot

    Each row is a study:
    - The **square** is the point estimate (size proportional to weight)
    - The **horizontal line** is the 95% CI
    - The **diamond** at the bottom is the pooled (overall) estimate
    - The **vertical line at 0** is the null (no effect)
    """)
    return


@app.cell(hide_code=True)
def _(
    active_df,
    alt,
    mo,
    pd,
    pooled_ci_high,
    pooled_ci_low,
    pooled_effect,
    studies_df,
):
    if len(active_df) == 0:
        _chart = alt.Chart(pd.DataFrame({'x': [0]})).mark_text(
            text='No studies selected', fontSize=16
        ).encode()
    else:
        # Study CIs (error bars)
        error_bars = alt.Chart(active_df).mark_rule(strokeWidth=2).encode(
            y=alt.Y('Study:N', title='', sort=list(studies_df['Study'])),
            x=alt.X('CI Lower:Q', title='Effect (log-OR)'),
            x2='CI Upper:Q',
            color=alt.value('#1f77b4')
        )

        # Study point estimates (size = weight)
        points = alt.Chart(active_df).mark_square(color='#1f77b4').encode(
            y=alt.Y('Study:N', sort=list(studies_df['Study'])),
            x='Effect:Q',
            size=alt.Size('Weight:Q', legend=None, scale=alt.Scale(range=[30, 300])),
            tooltip=[
                alt.Tooltip('Study:N'),
                alt.Tooltip('Effect:Q', format='.3f'),
                alt.Tooltip('CI Lower:Q', format='.3f'),
                alt.Tooltip('CI Upper:Q', format='.3f'),
                alt.Tooltip('N:Q'),
                alt.Tooltip('Weight:Q', format='.1f')
            ]
        )

        # Pooled estimate diamond
        diamond_df = pd.DataFrame({
            'Study': ['Pooled (Overall)'],
            'Effect': [pooled_effect],
            'CI Lower': [pooled_ci_low],
            'CI Upper': [pooled_ci_high]
        })

        diamond_bar = alt.Chart(diamond_df).mark_rule(
            strokeWidth=3, color='#d62728'
        ).encode(
            y=alt.Y('Study:N'),
            x='CI Lower:Q',
            x2='CI Upper:Q'
        )

        diamond_point = alt.Chart(diamond_df).mark_point(
            shape='diamond', size=200, filled=True, color='#d62728'
        ).encode(
            y='Study:N',
            x='Effect:Q',
            tooltip=[
                alt.Tooltip('Effect:Q', format='.3f', title='Pooled Effect'),
                alt.Tooltip('CI Lower:Q', format='.3f'),
                alt.Tooltip('CI Upper:Q', format='.3f')
            ]
        )

        # Null reference line
        null_line = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
            color='black', strokeDash=[5, 3]
        ).encode(x='x:Q')

        _chart = (error_bars + points + diamond_bar + diamond_point + null_line).properties(
            width=600, height=max(200, len(active_df) * 35 + 80),
            title='Forest Plot'
        )

    _sr_summary = f"Forest plot showing {len(active_df)} included studies. Pooled effect estimate = {pooled_effect:.3f} (95% CI: {pooled_ci_low:.3f} to {pooled_ci_high:.3f})."
    mo.vstack([
        _chart,
        mo.accordion({"View data table": mo.ui.table(active_df) if len(active_df) > 0 else mo.md("No studies selected.")}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">{_sr_summary}</div>')
    ])
    return


@app.cell(hide_code=True)
def _(active_df, i_squared, mo, pooled_ci_high, pooled_ci_low, pooled_effect, q_stat):
    _k = len(active_df)
    _sig = "Yes" if pooled_ci_low > 0 or pooled_ci_high < 0 else "No"

    # I² interpretation
    if i_squared < 25:
        _hetero_interp = "Low heterogeneity"
    elif i_squared < 50:
        _hetero_interp = "Moderate heterogeneity"
    elif i_squared < 75:
        _hetero_interp = "Substantial heterogeneity"
    else:
        _hetero_interp = "Considerable heterogeneity — pooled estimate may be misleading"

    mo.md(f"""
    ## Meta-Analysis Results

    | Metric | Value |
    |--------|-------|
    | Studies included | **{_k}** |
    | **Pooled Effect** | **{pooled_effect:.3f}** (95% CI: {pooled_ci_low:.3f} to {pooled_ci_high:.3f}) |
    | Statistically significant? | **{_sig}** (CI {'excludes' if _sig == 'Yes' else 'includes'} 0) |
    | **Cochran's Q** | {q_stat:.2f} (df = {max(_k - 1, 0)}) |
    | **I²** | **{i_squared:.1f}%** — {_hetero_interp} |

    **I² interpretation:**
    - 0–25%: Low — studies are consistent
    - 25–50%: Moderate
    - 50–75%: Substantial — consider subgroup analysis
    - >75%: Considerable — the "pooled" number may not be meaningful

    **Try it:** Remove a study that looks like an outlier. Watch how the diamond narrows and I² drops.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Verified: PMID 17120476
    mo.md(r"""
    ## Anchor Paper: Cochrane Review — Albumin for Fluid Resuscitation

    **The Albumin Reviewers (Alderson P, Bunn F, et al.).** "Human albumin solution for resuscitation
    and volume expansion in critically ill patients." *Cochrane Database Syst Rev.* 2004; updated 2011.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/17120476/) |
    [Cochrane Library](https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001208.pub4/full)

    **The study:** Meta-analysis of 32 RCTs (8,452 patients) comparing albumin vs. crystalloid/no albumin
    in critically ill patients. For hypovolemia: **RR of death = 1.02** (95% CI: 0.92–1.13).

    **Why this review teaches forest plots:**
    - Multiple studies with varying results → the forest plot shows each one
    - The pooled "diamond" gives the overall answer with its precision
    - High I² in some analyses led to debates about whether pooling was appropriate
    - Subgroup analyses (sepsis vs. trauma vs. burns) showed different effects → **heterogeneity matters!**

    **What to look for in any forest plot:**
    1. **Does the diamond cross the null line?** If yes → not statistically significant
    2. **How wide is the diamond?** Narrow = precise pooled estimate
    3. **Do individual studies mostly agree?** If scattered → high I² → be cautious
    4. **Are all studies on the same side?** If yes → consistent evidence
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | What It Means | What to Watch For |
    |---------|---------------|-------------------|
    | **Forest plot** | Visual summary of all studies + pooled result | Pattern of effects across studies |
    | **Diamond** | Pooled estimate and its CI | Width = precision; position = direction |
    | **I²** | % of variability due to true differences | >50% = be cautious about pooling |
    | **Cochran's Q** | Test for heterogeneity | Significant Q = studies differ |
    | **Fixed effects** | Assumes one true effect | Use when I² is low |
    | **Random effects** | Allows true effect to vary | Use when I² is moderate/high |
    | **Funnel plot** | Detect publication bias | Asymmetry suggests missing studies |

    ## Questions

    1. Exclude the largest study. How does the pooled estimate change? Why do larger studies have more influence?

    2. Increase between-study SD (τ) to 0.8. What happens to I²? Should you trust the pooled estimate?

    3. A meta-analysis reports a significant pooled effect but I² = 85%. A colleague says "the evidence is clear." How do you respond?

    4. All studies show effects between 0.2 and 0.6. One new study shows an effect of -0.3. What should you investigate before including it?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Cochrane albumin review — Cochrane Library, no embeddable PDF
    # Verified: PMID 17120476
    mo.accordion(
        {
            "Read the Anchor Paper: Cochrane Review — Albumin (2004/2011)": mo.md("""
**The Albumin Reviewers (Alderson P, Bunn F, et al.).** "Human albumin solution for resuscitation
and volume expansion in critically ill patients." *Cochrane Database Syst Rev.* 2004; updated 2011.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/17120476/) |
[Open on Cochrane Library](https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD001208.pub4/full)

*The Cochrane Library provides open access to review abstracts. Full text may require institutional access.*
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
