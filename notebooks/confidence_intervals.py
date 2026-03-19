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
app = marimo.App(width="medium", app_title="Precision vs Significance: Confidence Intervals")


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
    # Precision vs. Significance: Confidence Intervals

    A **p-value** tells you whether an effect is statistically significant. A **confidence interval (CI)**
    tells you much more: the **range of plausible effect sizes** and the **precision** of your estimate.

    This notebook simulates **20 independent trials** of the same treatment. Each trial estimates
    the effect and its 95% CI. Watch how:
    - **Larger samples → narrower CIs** (more precision)
    - Some CIs will miss the true effect (about 5% for a 95% CI)
    - A CI that crosses the null value (0 or 1) corresponds to p > 0.05
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Set the **true effect size** and the **sample size per trial**. All 20 simulated trials
    draw from the same underlying truth.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    true_effect_slider = mo.ui.slider(
        start=0.0, stop=1.0, value=0.3, step=0.05,
        label="True Effect Size (mean difference)", show_value=True
    )
    sample_size_slider = mo.ui.slider(
        start=10, stop=500, value=50, step=10,
        label="Sample Size per Trial", show_value=True
    )
    conf_level_slider = mo.ui.slider(
        start=80, stop=99, value=95, step=1,
        label="Confidence Level (%)", show_value=True
    )
    mo.hstack([true_effect_slider, sample_size_slider, conf_level_slider])
    return conf_level_slider, sample_size_slider, true_effect_slider


@app.cell(hide_code=True)
def _(conf_level_slider, np, pd, sample_size_slider, sp_stats, true_effect_slider):
    # Simulate 20 trials
    np.random.seed(42)
    n_trials = 20
    true_effect = true_effect_slider.value
    n_per_trial = sample_size_slider.value
    conf_level = conf_level_slider.value / 100

    z_crit = sp_stats.norm.ppf(1 - (1 - conf_level) / 2)

    trials = []
    for i in range(n_trials):
        # Each trial: treatment group mean = true_effect, control = 0, both sd = 1
        treatment = np.random.normal(true_effect, 1.0, n_per_trial)
        control = np.random.normal(0, 1.0, n_per_trial)

        diff = np.mean(treatment) - np.mean(control)
        se = np.sqrt(np.var(treatment, ddof=1) / n_per_trial + np.var(control, ddof=1) / n_per_trial)

        ci_low = diff - z_crit * se
        ci_high = diff + z_crit * se
        significant = ci_low > 0 or ci_high < 0  # doesn't cross 0
        covers_truth = ci_low <= true_effect <= ci_high

        trials.append({
            'Trial': i + 1,
            'Estimate': diff,
            'CI Lower': ci_low,
            'CI Upper': ci_high,
            'SE': se,
            'Significant': 'Yes' if significant else 'No',
            'Covers Truth': 'Yes' if covers_truth else 'No'
        })

    trials_df = pd.DataFrame(trials)

    n_significant = int(trials_df['Significant'].eq('Yes').sum())
    n_covers = int(trials_df['Covers Truth'].eq('Yes').sum())
    return conf_level, n_covers, n_significant, n_trials, trials_df, true_effect


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Forest Plot of 20 Simulated Trials

    Each horizontal line is a trial's **confidence interval**. The dot is the **point estimate**.

    - **Green** = CI does NOT cross 0 (statistically significant, p < α)
    - **Gray** = CI crosses 0 (not significant)
    - **Red dashed line** = the true effect size
    - **Black line** = null hypothesis (effect = 0)
    """)
    return


@app.cell(hide_code=True)
def _(alt, conf_level, mo, pd, trials_df, true_effect):
    # Forest plot
    error_bars = alt.Chart(trials_df).mark_rule(strokeWidth=2).encode(
        y=alt.Y('Trial:O', title='Trial', sort='descending'),
        x=alt.X('CI Lower:Q', title='Effect Size (Mean Difference)'),
        x2='CI Upper:Q',
        color=alt.Color('Significant:N', scale=alt.Scale(
            domain=['Yes', 'No'],
            range=['#2ca02c', '#999999']
        ), legend=alt.Legend(title='Significant'))
    ).properties(
        width=600, height=450,
        title=f'Forest Plot: 20 Simulated Trials ({conf_level:.0%} CI)'
    )

    points = alt.Chart(trials_df).mark_circle(size=60).encode(
        y=alt.Y('Trial:O', sort='descending'),
        x='Estimate:Q',
        color=alt.Color('Significant:N', scale=alt.Scale(
            domain=['Yes', 'No'],
            range=['#2ca02c', '#999999']
        )),
        tooltip=[
            alt.Tooltip('Trial:O'),
            alt.Tooltip('Estimate:Q', format='.3f'),
            alt.Tooltip('CI Lower:Q', format='.3f'),
            alt.Tooltip('CI Upper:Q', format='.3f'),
            alt.Tooltip('Significant:N')
        ]
    )

    # Null reference line
    null_line = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(
        color='black', strokeWidth=1.5
    ).encode(x='x:Q')

    # True effect line
    truth_line = alt.Chart(pd.DataFrame({'x': [true_effect]})).mark_rule(
        color='#d62728', strokeDash=[5, 3], strokeWidth=2
    ).encode(x='x:Q')

    truth_label = alt.Chart(pd.DataFrame({
        'x': [true_effect], 'y': [1], 'label': [f'True Effect = {true_effect:.2f}']
    })).mark_text(
        align='left', dx=5, fontSize=10, color='#d62728'
    ).encode(x='x:Q', y='y:O', text='label:N')

    forest = error_bars + points + null_line + truth_line + truth_label
    _n_sig = int(trials_df['Significant'].eq('Yes').sum())
    _sr_summary = f"Forest plot of {len(trials_df)} simulated trials with true effect {true_effect:.2f} at {conf_level:.0%} confidence level. {_n_sig} of {len(trials_df)} trials reached statistical significance."
    mo.vstack([
        forest,
        mo.accordion({"View data table": mo.ui.table(trials_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">{_sr_summary}</div>')
    ])
    return


@app.cell(hide_code=True)
def _(conf_level, mo, n_covers, n_significant, n_trials, true_effect):
    _expected_cover = conf_level * 100
    mo.md(f"""
    ## Summary

    | Metric | Value |
    |--------|-------|
    | True effect size | **{true_effect:.2f}** |
    | Trials that reached significance | **{n_significant} / {n_trials}** |
    | Trials whose CI covers the true effect | **{n_covers} / {n_trials}** (expect ~{_expected_cover:.0f}%) |

    **Key insight:** Even with a real effect of {true_effect:.2f}, not every trial detects it.
    The trials that "miss" (gray) are **Type II errors** — the study was underpowered or unlucky.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How CI Width Shrinks with Sample Size

    The width of a 95% CI is proportional to $1/\sqrt{n}$. Doubling your sample doesn't halve the CI —
    you need to **quadruple** it.
    """)
    return


@app.cell(hide_code=True)
def _(alt, mo, np, pd, sp_stats):
    # CI width as a function of n
    n_range = np.arange(10, 510, 10)
    _z = sp_stats.norm.ppf(0.975)
    # Assuming sd=1 for each group, SE = sqrt(2/n), CI width = 2 * z * SE
    ci_widths = [2 * _z * np.sqrt(2.0 / _n) for _n in n_range]

    width_df = pd.DataFrame({
        'Sample Size (per group)': n_range,
        'CI Width': ci_widths
    })

    width_chart = alt.Chart(width_df).mark_line(
        color='#1f77b4', strokeWidth=2.5
    ).encode(
        x=alt.X('Sample Size (per group):Q'),
        y=alt.Y('CI Width:Q', title='95% CI Width'),
        tooltip=[
            alt.Tooltip('Sample Size (per group):Q'),
            alt.Tooltip('CI Width:Q', format='.3f')
        ]
    ).properties(
        width=700, height=300,
        title='How Confidence Interval Width Shrinks with Sample Size'
    )

    _sr_summary = f"Line chart showing 95% CI width decreasing from {ci_widths[0]:.2f} at n=10 to {ci_widths[-1]:.2f} at n=500 as sample size increases."
    mo.vstack([
        width_chart,
        mo.accordion({"View data table": mo.ui.table(width_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">{_sr_summary}</div>')
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Anchor paper: ISIS-2
    # Verified: PMID 2899772, Lancet 1988
    # WARNING: DOI for ISIS-2 could not be confirmed via PubMed page. The commonly cited
    # DOI 10.1016/S0140-6736(88)92833-4 was not verified. Linking only to PubMed.
    mo.md(r"""
    ## Anchor Paper: ISIS-2 (1988)

    **ISIS-2 Collaborative Group.** "Randomised trial of intravenous streptokinase, oral aspirin, both,
    or neither among 17,187 cases of suspected acute myocardial infarction: ISIS-2."
    *Lancet.* 1988;2(8607):349-360.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/2899772/)

    **Why this paper is perfect for teaching CIs:**

    With **17,187 patients**, ISIS-2 was one of the largest trials of its era.
    The sheer sample size produced incredibly **tight confidence intervals**:

    - Aspirin: 23% reduction in vascular mortality (95% CI: 15–30%)
    - Streptokinase: 25% reduction (95% CI: 18–32%)
    - Both together: 42% reduction (95% CI: 34–50%)

    **Board-relevant points:**
    - These CIs are narrow because n is enormous — high **precision**
    - Compare: a trial with n = 200 might find the same point estimate but with CI: 5–45% (low precision)
    - **The CI tells you both significance AND clinical relevance:** a 15–30% reduction is meaningful no matter what
    - **CI crossing the null:** If a 95% CI for relative risk includes 1.0, or for mean difference includes 0, then p > 0.05

    **Famous teaching example:** A subgroup analysis of ISIS-2 by astrological sign "found" that aspirin was
    harmful for Libras and Geminis. This is a classic example of why subgroup analyses with wide CIs
    should not drive clinical decisions!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | What It Tells You |
    |---------|-------------------|
    | **Point estimate** | Best single guess of the effect |
    | **CI width** | Precision of the estimate (narrower = more precise) |
    | **CI includes null** | Not statistically significant (p > α) |
    | **CI excludes null** | Statistically significant (p < α) |
    | **CI entirely on one side** | Direction AND significance are clear |
    | **Narrow CI, small effect** | Precisely measured trivial effect |
    | **Wide CI, large effect** | Potentially important but imprecise |

    **The key rule:** If the 95% CI for OR/RR crosses 1.0, or for a mean difference crosses 0, then p > 0.05.

    ## Questions

    1. Set the true effect to 0.0 and run the simulation. How many trials are "significant"? What does this represent?

    2. With n = 20 per trial and true effect = 0.3, how many trials detect the effect? What about n = 200?

    3. Why is a study with a point estimate of 0.5 and CI [0.05, 0.95] less convincing than one with estimate 0.3 and CI [0.25, 0.35]?

    4. Change the confidence level from 95% to 80%. What happens to CI width? What is the trade-off?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # ISIS-2 — 1988 Lancet, no PMC PDF
    # Verified: PMID 2899772
    mo.accordion(
        {
            "Read the Anchor Paper: ISIS-2 (1988)": mo.md("""
**ISIS-2 Collaborative Group.** "Randomised trial of intravenous streptokinase, oral aspirin, both,
or neither among 17,187 cases of suspected acute myocardial infarction: ISIS-2."
*Lancet.* 1988;2(8607):349-360.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/2899772/)

*This article may require institutional access through The Lancet.*
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
