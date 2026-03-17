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
app = marimo.App(width="medium", app_title="Correlation vs Regression")


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
    # Correlation vs. Regression: The Slope

    **Correlation** ($r$) tells you the *strength and direction* of a linear relationship.
    **Regression** gives you the *equation* of the line (the slope and intercept) and a way to make predictions.

    These are related but different:
    - $r$ ranges from −1 to +1 and has no units
    - $R^2 = r^2$ tells you what fraction of the variance is "explained" by the relationship
    - The **regression slope** has units and tells you "for each 1-unit increase in X, Y changes by ___"

    Use the controls below to generate data and see how these statistics change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Adjust the underlying relationship and the noise level.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    n_points_slider = mo.ui.slider(
        start=10, stop=200, value=50, step=5,
        label="Number of Data Points", show_value=True
    )
    true_slope_slider = mo.ui.slider(
        start=-2.0, stop=2.0, value=0.8, step=0.1,
        label="True Slope", show_value=True
    )
    noise_slider = mo.ui.slider(
        start=0.5, stop=10.0, value=3.0, step=0.5,
        label="Noise Level (SD)", show_value=True
    )
    intercept_slider = mo.ui.slider(
        start=-10, stop=10, value=5, step=1,
        label="True Intercept", show_value=True
    )
    mo.hstack([n_points_slider, true_slope_slider, intercept_slider, noise_slider])
    return intercept_slider, n_points_slider, noise_slider, true_slope_slider


@app.cell(hide_code=True)
def _(intercept_slider, noise_slider, np, n_points_slider, pd, sp_stats, true_slope_slider):
    # Generate data
    np.random.seed(42)
    _n = n_points_slider.value
    _slope = true_slope_slider.value
    _intercept = intercept_slider.value
    _noise = noise_slider.value

    x_data = np.random.uniform(0, 20, _n)
    y_data = _intercept + _slope * x_data + np.random.normal(0, _noise, _n)

    scatter_df = pd.DataFrame({'X': x_data, 'Y': y_data})

    # Calculate statistics
    r_val, p_val = sp_stats.pearsonr(x_data, y_data)
    r_squared = r_val ** 2

    # Linear regression
    slope_est, intercept_est, r_val_2, p_val_2, se_slope = sp_stats.linregress(x_data, y_data)

    # Regression line data
    x_line = np.array([x_data.min(), x_data.max()])
    y_line = intercept_est + slope_est * x_line
    line_df = pd.DataFrame({'X': x_line, 'Y': y_line})
    return (
        intercept_est,
        line_df,
        p_val,
        r_squared,
        r_val,
        scatter_df,
        se_slope,
        slope_est,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Scatterplot with Line of Best Fit

    The **blue dots** are individual data points. The **red line** is the ordinary least-squares regression line.
    It minimizes the sum of squared vertical distances from each point to the line.
    """)
    return


@app.cell(hide_code=True)
def _(alt, line_df, r_squared, r_val, scatter_df, slope_est):
    # Scatterplot
    scatter = alt.Chart(scatter_df).mark_circle(
        size=50, opacity=0.6, color='#1f77b4'
    ).encode(
        x=alt.X('X:Q', title='X'),
        y=alt.Y('Y:Q', title='Y'),
        tooltip=[
            alt.Tooltip('X:Q', format='.2f'),
            alt.Tooltip('Y:Q', format='.2f')
        ]
    ).properties(
        width=600, height=450,
        title=f'Scatterplot (r = {r_val:.3f}, R² = {r_squared:.3f}, slope = {slope_est:.3f})'
    )

    # Regression line
    reg_line = alt.Chart(line_df).mark_line(
        color='#d62728', strokeWidth=2.5
    ).encode(x='X:Q', y='Y:Q')

    scatter + reg_line
    return


@app.cell(hide_code=True)
def _(intercept_est, mo, p_val, r_squared, r_val, se_slope, slope_est):
    _sig = "Yes" if p_val < 0.05 else "No"
    mo.md(f"""
    ## Statistics

    | Statistic | Value | Interpretation |
    |-----------|-------|----------------|
    | **Pearson's r** | {r_val:.3f} | {'Strong' if abs(r_val) > 0.7 else 'Moderate' if abs(r_val) > 0.4 else 'Weak'} {'positive' if r_val > 0 else 'negative'} correlation |
    | **R²** | {r_squared:.3f} | **{r_squared:.1%}** of Y's variance is explained by X |
    | **Slope (β₁)** | {slope_est:.3f} ± {se_slope:.3f} | For each 1-unit ↑ in X, Y changes by {slope_est:.3f} |
    | **Intercept (β₀)** | {intercept_est:.3f} | Predicted Y when X = 0 |
    | **p-value** | {p_val:.4f} | Significant? **{_sig}** |

    **Important distinctions:**
    - $r$ = {r_val:.3f} tells you the correlation *strength* (unitless, −1 to +1)
    - $R^2$ = {r_squared:.3f} tells you variance explained (0 to 1) — note r = {r_val:.3f} → R² = {r_squared:.3f}
    - The slope tells you the *rate of change* (in Y-units per X-unit)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How R² Changes with Noise

    The chart below shows how $R^2$ decreases as noise increases. At high noise,
    even a real linear relationship becomes invisible to the data.
    """)
    return


@app.cell(hide_code=True)
def _(alt, intercept_slider, np, pd, sp_stats, true_slope_slider):
    # R² vs noise level
    np.random.seed(42)
    _n = 50
    _slope = true_slope_slider.value
    _intercept = intercept_slider.value
    _x = np.random.uniform(0, 20, _n)

    noise_range = np.arange(0.5, 10.5, 0.5)
    r2_data = []
    for _noise in noise_range:
        _y = _intercept + _slope * _x + np.random.normal(0, _noise, _n)
        _r, _ = sp_stats.pearsonr(_x, _y)
        r2_data.append({'Noise (SD)': float(_noise), 'R²': _r ** 2})

    r2_df = pd.DataFrame(r2_data)

    r2_chart = alt.Chart(r2_df).mark_line(
        color='#ff7f0e', strokeWidth=2.5, point=True
    ).encode(
        x=alt.X('Noise (SD):Q'),
        y=alt.Y('R²:Q', scale=alt.Scale(domain=[0, 1])),
        tooltip=[
            alt.Tooltip('Noise (SD):Q'),
            alt.Tooltip('R²:Q', format='.3f')
        ]
    ).properties(
        width=700, height=300,
        title=f'R² vs Noise Level (True Slope = {_slope:.1f})'
    )

    r2_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Common Pitfalls

    **Correlation ≠ Causation:** This is the most famous warning in statistics, but it bears repeating.
    A strong correlation between X and Y could be due to:
    - X causes Y
    - Y causes X
    - A third variable (confounder) causes both
    - Pure coincidence (especially with many variables tested)

    **Other pitfalls:**
    - **Outliers** can dramatically change $r$ and the regression line
    - **Restricted range** (only sampling a narrow range of X) will underestimate $r$
    - **Non-linear relationships** may have $r ≈ 0$ even with a strong association (e.g., U-shaped curves)
    - **Ecological fallacy:** Correlations at the group level don't necessarily hold at the individual level
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Verified: PMID 13751193, Kannel et al., Ann Intern Med, 1961
    mo.md(r"""
    ## Anchor Paper: The Framingham Heart Study (1961)

    **Kannel WB, Dawber TR, Kagan A, Revotskie N, Stokes J 3rd.** "Factors of risk in the
    development of coronary heart disease — six year follow-up experience. The Framingham Study."
    *Ann Intern Med.* 1961;55:33-50.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/13751193/)

    This paper **popularized the term "risk factor"** in medical literature and established that
    serum cholesterol, blood pressure, and LVH on ECG were strong predictors of coronary heart disease.

    **Key regression/correlation teaching points:**
    - Framingham used **multivariate regression** — adjusting for multiple risk factors simultaneously
    - This is how you determine whether cholesterol *independently* predicts CHD after controlling for age, smoking, BP, etc.
    - These relationships informed the **Framingham Risk Score**, which uses multiple regression to predict 10-year cardiovascular risk
    - The $R^2$ of the Framingham Risk Score is moderate — it explains much but not all of the variability in outcomes
    - **Regression to the mean:** Extreme first measurements tend to be less extreme on remeasurement —
      this is a statistical phenomenon, not a treatment effect
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | What It Tells You | Range |
    |---------|-------------------|-------|
    | **Pearson's r** | Strength and direction of linear association | −1 to +1 |
    | **R²** | Proportion of variance explained | 0 to 1 |
    | **Slope (β₁)** | Rate of change of Y per unit X | Any real number |
    | **p-value (slope)** | Is the slope significantly different from 0? | 0 to 1 |

    **Board pearls:**
    - $r = 0.7$ → $R^2 = 0.49$ → only ~49% of variance explained (not 70%!)
    - Correlation does NOT imply causation
    - **Regression to the mean** is a statistical artifact, not a biological effect
    - **Multivariate regression** adjusts for confounders — essential for observational studies

    ## Questions

    1. Set the true slope to 0. What is $r$? Is it exactly 0? Why or why not?

    2. With slope = 1.0 and noise = 2.0, what is R²? Now increase noise to 8.0. How does R² change?

    3. A study reports $r = 0.3$ between coffee consumption and longevity. A headline says "Coffee extends life!" What's wrong with this claim?

    4. What is the difference between $r = 0.5$ and $R^2 = 0.5$? Which represents a stronger relationship?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Framingham 1961 — very old, no PMC PDF
    # Verified: PMID 13751193
    mo.accordion(
        {
            "Read the Anchor Paper: Framingham Heart Study (1961)": mo.md("""
**Kannel WB, Dawber TR, Kagan A, Revotskie N, Stokes J 3rd.** "Factors of risk in the
development of coronary heart disease — six year follow-up experience. The Framingham Study."
*Ann Intern Med.* 1961;55:33-50.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/13751193/) |
[Open on Annals of Internal Medicine](https://doi.org/10.7326/0003-4819-55-1-33)

*This classic paper may require institutional access through the Annals of Internal Medicine.*
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
