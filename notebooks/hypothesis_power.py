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
app = marimo.App(width="medium", app_title="Hypothesis Testing, Power, and p-values")


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
    # The p-value, Power, and Effect Size Triad

    When we run a clinical trial, we're asking: **"Is the treatment effect real, or could it be due to chance?"**

    Under the hood, hypothesis testing compares two worlds:

    - **Null hypothesis ($H_0$):** There is no true difference (effect size = 0).
    - **Alternative hypothesis ($H_1$):** There is a real difference of some size $\Delta$.

    Each world corresponds to a **sampling distribution** of our test statistic (e.g., the difference in means).
    The overlap between these distributions determines how often we make correct vs. incorrect decisions.

    Use the sliders below to explore how **sample size**, **effect size**, and **significance level** interact.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Adjust these parameters to see how the distributions and decision regions change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    sample_size_slider = mo.ui.slider(
        start=5, stop=500, value=30, step=5,
        label="Sample Size per Group (n)", show_value=True
    )
    effect_size_slider = mo.ui.slider(
        start=0.0, stop=2.0, value=0.5, step=0.05,
        label="Effect Size (Cohen's d)", show_value=True
    )
    alpha_slider = mo.ui.slider(
        start=0.01, stop=0.20, value=0.05, step=0.01,
        label="Significance Level (α)", show_value=True
    )
    mo.vstack([
        mo.hstack([sample_size_slider, effect_size_slider, alpha_slider])
    ])
    return alpha_slider, effect_size_slider, sample_size_slider


@app.cell(hide_code=True)
def _(alpha_slider, effect_size_slider, np, pd, sample_size_slider, sp_stats):
    # Compute the null and alternative distributions for a two-sample z-test
    n = sample_size_slider.value
    d = effect_size_slider.value
    alpha = alpha_slider.value

    # Standard error of the difference in means (assuming sigma=1 for standardized)
    se = np.sqrt(2.0 / n)

    # Null distribution: mean=0, sd=se
    # Alternative distribution: mean=d, sd=se
    z_crit = sp_stats.norm.ppf(1 - alpha)  # one-sided critical value

    # Power = P(Z > z_crit | H1 is true)
    power = 1 - sp_stats.norm.cdf(z_crit, loc=d / se, scale=1)
    # Actually, let's work in the "difference in means" space
    # Null: N(0, se), Alt: N(d, se)
    crit_value = z_crit * se  # critical value in raw units

    power_val = 1 - sp_stats.norm.cdf(crit_value, loc=d, scale=se)
    beta_val = 1 - power_val

    # Generate distribution curves
    x_min = min(0, d) - 4 * se
    x_max = max(0, d) + 4 * se
    x_vals = np.linspace(x_min, x_max, 500)

    null_pdf = sp_stats.norm.pdf(x_vals, loc=0, scale=se)
    alt_pdf = sp_stats.norm.pdf(x_vals, loc=d, scale=se)

    # Build dataframes for the curves
    curve_df = pd.DataFrame({
        'x': np.concatenate([x_vals, x_vals]),
        'density': np.concatenate([null_pdf, alt_pdf]),
        'Distribution': ['Null (H₀)'] * len(x_vals) + ['Alternative (H₁)'] * len(x_vals)
    })

    # Alpha shading: null distribution, x > crit_value
    alpha_mask = x_vals >= crit_value
    alpha_shade_df = pd.DataFrame({
        'x': x_vals[alpha_mask],
        'density': null_pdf[alpha_mask],
        'Region': 'α (Type I Error)'
    })

    # Power shading: alternative distribution, x > crit_value
    power_mask = x_vals >= crit_value
    power_shade_df = pd.DataFrame({
        'x': x_vals[power_mask],
        'density': alt_pdf[power_mask],
        'Region': 'Power (1 − β)'
    })

    # Beta shading: alternative distribution, x < crit_value
    beta_mask = x_vals < crit_value
    beta_shade_df = pd.DataFrame({
        'x': x_vals[beta_mask],
        'density': alt_pdf[beta_mask],
        'Region': 'β (Type II Error)'
    })
    return (
        alpha_shade_df,
        beta_shade_df,
        beta_val,
        crit_value,
        curve_df,
        d,
        n,
        power_shade_df,
        power_val,
        se,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Two Distributions

    The **blue curve** is the sampling distribution assuming no effect (Null, $H_0$).
    The **orange curve** is the distribution assuming the true effect exists (Alternative, $H_1$).

    - The **red vertical line** is the critical value — our decision boundary.
    - The **red shaded area** under the null curve (right of the line) is **α** — the probability of a Type I error (false positive).
    - The **green shaded area** under the alternative curve (right of the line) is **Power** — the probability of correctly detecting a real effect.
    - The **gray area** under the alternative curve (left of the line) is **β** — the probability of a Type II error (false negative).
    """)
    return


@app.cell(hide_code=True)
def _(
    alpha_shade_df,
    alt,
    beta_shade_df,
    crit_value,
    curve_df,
    pd,
    power_shade_df,
):
    # Main distribution curves
    curves = alt.Chart(curve_df).mark_line(strokeWidth=2.5).encode(
        x=alt.X('x:Q', title='Observed Effect (Difference in Means)'),
        y=alt.Y('density:Q', title='Probability Density'),
        color=alt.Color('Distribution:N', scale=alt.Scale(
            domain=['Null (H₀)', 'Alternative (H₁)'],
            range=['#1f77b4', '#ff7f0e']
        )),
        strokeDash=alt.StrokeDash('Distribution:N', scale=alt.Scale(
            domain=['Null (H₀)', 'Alternative (H₁)'],
            range=[[1, 0], [6, 3]]
        ))
    ).properties(
        width=700,
        height=400,
        title='Null vs Alternative Sampling Distributions'
    )

    # Alpha shading (Type I Error)
    alpha_area = alt.Chart(alpha_shade_df).mark_area(
        opacity=0.35, color='#d62728'
    ).encode(
        x='x:Q',
        y='density:Q',
        tooltip=[alt.Tooltip('Region:N')]
    )

    # Power shading
    power_area = alt.Chart(power_shade_df).mark_area(
        opacity=0.35, color='#2ca02c'
    ).encode(
        x='x:Q',
        y='density:Q',
        tooltip=[alt.Tooltip('Region:N')]
    )

    # Beta shading (Type II Error)
    beta_area = alt.Chart(beta_shade_df).mark_area(
        opacity=0.2, color='#7f7f7f'
    ).encode(
        x='x:Q',
        y='density:Q',
        tooltip=[alt.Tooltip('Region:N')]
    )

    # Critical value line
    crit_line = alt.Chart(pd.DataFrame({'x': [crit_value]})).mark_rule(
        color='#d62728', strokeWidth=2, strokeDash=[5, 3]
    ).encode(x='x:Q')

    # Crit value label
    crit_label = alt.Chart(pd.DataFrame({
        'x': [crit_value], 'label': ['Critical Value']
    })).mark_text(
        align='left', dx=5, dy=-10, fontSize=11, color='#d62728'
    ).encode(x='x:Q', text='label:N')

    chart = curves + alpha_area + power_area + beta_area + crit_line + crit_label
    chart
    return


@app.cell(hide_code=True)
def _(alpha, beta_val, d, mo, n, power_val, se):
    mo.md(f"""
    ## Current Statistics

    | Parameter | Value |
    |-----------|-------|
    | Sample size per group (n) | **{n}** |
    | Effect size (Cohen's d) | **{d:.2f}** |
    | Significance level (α) | **{alpha:.2f}** |
    | Standard error | **{se:.4f}** |
    | **Power (1 − β)** | **{power_val:.1%}** |
    | **β (Type II Error)** | **{beta_val:.1%}** |

    **Interpretation:** With {n} patients per group and an effect size of {d:.2f}, there is a **{power_val:.1%}** chance of detecting a real effect at α = {alpha:.2f}.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How Power Changes with Sample Size

    The plot below shows how statistical power increases as sample size grows, for your current effect size and α.
    The dashed line marks 80% power — a common target in study design.
    """)
    return


@app.cell(hide_code=True)
def _(alpha_slider, alt, effect_size_slider, np, pd, sample_size_slider, sp_stats):
    # Power curve as a function of sample size
    _d = effect_size_slider.value
    _alpha = alpha_slider.value
    _n_current = sample_size_slider.value

    n_range = np.arange(5, 505, 5)
    power_curve_data = []
    for _n in n_range:
        _se = np.sqrt(2.0 / _n)
        _z_crit = sp_stats.norm.ppf(1 - _alpha)
        _crit_val = _z_crit * _se
        _pwr = 1 - sp_stats.norm.cdf(_crit_val, loc=_d, scale=_se)
        power_curve_data.append({'n': int(_n), 'Power': _pwr})
    power_curve_df = pd.DataFrame(power_curve_data)

    power_line = alt.Chart(power_curve_df).mark_line(
        color='#2ca02c', strokeWidth=2.5
    ).encode(
        x=alt.X('n:Q', title='Sample Size per Group'),
        y=alt.Y('Power:Q', title='Statistical Power', scale=alt.Scale(domain=[0, 1])),
        tooltip=[alt.Tooltip('n:Q'), alt.Tooltip('Power:Q', format='.1%')]
    ).properties(
        width=700,
        height=300,
        title=f'Power vs Sample Size (d={_d:.2f}, α={_alpha:.2f})'
    )

    # 80% power reference line
    ref_line = alt.Chart(pd.DataFrame({'y': [0.8]})).mark_rule(
        strokeDash=[5, 3], color='gray'
    ).encode(y='y:Q')

    ref_label = alt.Chart(pd.DataFrame({
        'x': [10], 'y': [0.82], 'label': ['80% Power']
    })).mark_text(
        align='left', fontSize=11, color='gray'
    ).encode(x='x:Q', y='y:Q', text='label:N')

    # Current sample size dot
    _se_current = np.sqrt(2.0 / _n_current)
    _z_crit_current = sp_stats.norm.ppf(1 - _alpha)
    _power_current = 1 - sp_stats.norm.cdf(_z_crit_current * _se_current, loc=_d, scale=_se_current)
    current_dot = alt.Chart(pd.DataFrame({
        'n': [_n_current], 'Power': [_power_current]
    })).mark_point(
        color='red', size=100, filled=True
    ).encode(
        x='n:Q', y='Power:Q',
        tooltip=[alt.Tooltip('n:Q', title='Current n'), alt.Tooltip('Power:Q', format='.1%')]
    )

    power_chart = power_line + ref_line + ref_label + current_dot
    power_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Anchor Paper: The SPRINT Trial (2015)

    **Systolic Blood Pressure Intervention Trial (SPRINT)** randomized 9,361 patients to intensive
    ($<$120 mmHg) vs. standard ($<$140 mmHg) systolic blood pressure targets.

    **Key biostatistics takeaway:** The trial was **stopped early** because the treatment effect was so large
    (HR = 0.75 for the primary composite outcome, p < 0.001) that continuing would have been unethical.

    This illustrates several concepts from our visualization:

    - **Large effect size + large sample** = very high power. The data monitoring committee saw overwhelming evidence.
    - **Stopping early** relates to **interim analyses** — checking whether the effect has already crossed a pre-specified boundary.
    - A "fragile" p-value (barely below 0.05) would NOT have justified early stopping. SPRINT's result was robust.

    **Board-relevant question:** *A study with 50 patients per group finds p = 0.048. Another with 5,000 per group
    finds p = 0.001. Which result is more convincing, and why?*

    The answer involves all three parts of our triad: the second study has higher power, so its p-value
    reflects a more reliable finding — it's less "fragile" and less likely to be a false positive.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | Definition | Clinical Relevance |
    |---------|------------|--------------------|
    | **p-value** | Probability of seeing data this extreme if $H_0$ is true | Smaller p → stronger evidence against no effect |
    | **α (Type I Error)** | False positive rate — rejecting $H_0$ when it's actually true | Usually set at 0.05 by convention |
    | **β (Type II Error)** | False negative rate — failing to reject $H_0$ when $H_1$ is true | Missed real effects |
    | **Power (1 − β)** | Probability of detecting a real effect | Target ≥ 80% in study design |
    | **Effect Size** | Magnitude of the true difference (e.g., Cohen's d) | Larger effects are easier to detect |
    | **Sample Size** | Number of participants per group | More participants → narrower distributions → more power |

    **The triad:** These three factors — sample size, effect size, and α — completely determine power.
    Fix any two, and the third is determined.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Questions

    1. Set the effect size to 0. What happens to power? Why can't we detect a non-existent effect?

    2. With a small sample (n=10) and small effect (d=0.2), what is the power? What does this say about underpowered studies?

    3. If you increase α from 0.05 to 0.10, what happens to power? What's the trade-off?

    4. What sample size do you need to achieve 80% power with an effect size of d=0.3?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # SPRINT Trial — PMC free full text available
    # Verified: PMID 26551272, DOI 10.1056/NEJMoa1511939, PMCID PMC4689591
    mo.accordion(
        {
            "Read the Anchor Paper: SPRINT Trial (2015)": mo.pdf(
                src="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4689591/pdf/nihms742755.pdf",
                width="100%",
                height="70vh",
            )
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
