# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==5.5.0",
#     "ipywidgets==8.1.7",
#     "matplotlib==3.10.6",
#     "numpy==2.3.3",
#     "pandas==2.3.2",
#     "scikit-learn==1.7.2",
#     "scipy==1.16.2",
#     "seaborn==0.13.2",
# ]
# ///

import marimo

__generated_with = "0.15.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.metrics import roc_curve, auc, confusion_matrix
    from scipy import stats
    import altair as alt
    import math
    return alt, mo, np, pd, stats


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Stats Examples

    This app helps visualize some examples and connect them to stats concepts.

    Use the tabs below to explore the different the different examples.
    """
    )
    return


@app.cell
def _(mo):
    tabs = mo.ui.tabs({
        # For the larynhoscopy odds example, I want to show odds ratio ofc. I also want to show how this would look with risk (a probability) instead of odds. I think I can also include the concepts of absolute and relative risk reduction and number needed to treat.
        "Laryngoscopy (Odds)": mo.md(
                      "Test results of a new intubation technique: 100 patients died using direct laryngoscopy, while 10 died using a blindfolded technique; 900 patients survived using direct laryngoscopy, while 200 survived using the blindfolded technique. What is the odds ratio for dying using direct laryngoscopy vs blindfolded?"
        ),
        # For the whipple tests example, I want to show a t-test and ANOVA. I also want to show the concept of paired vs unpaired tests. I think I can also include the concepts of type 1 and type 2 errors here.
        "Whipple (Tests)": mo.md(
            "Patients scheduled to undergo a whipple are randomized into 2 groups.  Group 1 receives GETA + regional anesthesia and Group 2 receives GETA + a ketamine infusion.  PACU opoid usage is measured for 4 hours.  Which of the following statistical tests would be MOST appropriate to determine whether opioid usage changes with respect to the type of anesthesia?"
        ),
    })
    tabs
    return (tabs,)


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Laryngoscopy (Odds)")
    mo.md(
        r"""
        ## Odds Ratios vs Risk Analysis

        **Clinical Scenario:** Comparing two intubation techniques - direct laryngoscopy vs a blindfolded technique.

        Understanding the difference between **odds** and **risk** is crucial in medical decision-making:

        - **Risk (probability)** = Deaths / Total patients in each group
        - **Odds** = Deaths / Survivors in each group  
        - **Odds Ratio** = (Odds in exposed group) / (Odds in control group)
        - **Relative Risk** = (Risk in exposed group) / (Risk in control group)

        Use the sliders below to explore how different patient outcomes affect these key statistics.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Laryngoscopy (Odds)")

    # Interactive controls for the 2x2 table
    direct_deaths = mo.ui.slider(1, 200, value=100, label="Direct Laryngoscopy Deaths", show_value=True)
    direct_survivors = mo.ui.slider(100, 1000, value=900, label="Direct Laryngoscopy Survivors", show_value=True)
    blind_deaths = mo.ui.slider(1, 200, value=10, label="Blindfolded Deaths", show_value=True)
    blind_survivors = mo.ui.slider(50, 500, value=200, label="Blindfolded Survivors", show_value=True)

    mo.hstack([
        mo.vstack([direct_deaths, direct_survivors]),
        mo.vstack([blind_deaths, blind_survivors])
    ])
    return blind_deaths, blind_survivors, direct_deaths, direct_survivors


@app.cell
def _(
    alt,
    blind_deaths,
    blind_survivors,
    direct_deaths,
    direct_survivors,
    mo,
    pd,
    tabs,
):
    mo.stop(tabs.value != "Laryngoscopy (Odds)")

    # Calculate key statistics
    direct_total = direct_deaths.value + direct_survivors.value
    blind_total = blind_deaths.value + blind_survivors.value

    # Risk calculations
    direct_risk = direct_deaths.value / direct_total
    blind_risk = blind_deaths.value / blind_total
    relative_risk = direct_risk / blind_risk
    absolute_risk_reduction = direct_risk - blind_risk
    number_needed_to_treat = 1 / abs(absolute_risk_reduction) if absolute_risk_reduction != 0 else float('inf')

    # Odds calculations  
    direct_odds = direct_deaths.value / direct_survivors.value
    blind_odds = blind_deaths.value / blind_survivors.value
    odds_ratio = direct_odds / blind_odds

    # Create 2x2 contingency table data
    table_data = pd.DataFrame({
        'Technique': ['Direct Laryngoscopy', 'Direct Laryngoscopy', 'Blindfolded', 'Blindfolded'],
        'Outcome': ['Death', 'Survival', 'Death', 'Survival'], 
        'Count': [direct_deaths.value, direct_survivors.value, blind_deaths.value, blind_survivors.value],
        'Row': ['Direct', 'Direct', 'Blindfolded', 'Blindfolded'],
        'Col': ['Death', 'Survival', 'Death', 'Survival']
    })

    # Create heatmap
    heatmap = alt.Chart(table_data).mark_rect().encode(
        x=alt.X('Col:O', title='Outcome'),
        y=alt.Y('Row:O', title='Technique'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues'), legend=alt.Legend(title="Count")),
        tooltip=['Technique', 'Outcome', 'Count']
    ).properties(
        title='2x2 Contingency Table',
        width=300,
        height=200
    )

    # Add text labels
    text = alt.Chart(table_data).mark_text(
        fontSize=16,
        fontWeight='bold'
    ).encode(
        x='Col:O',
        y='Row:O', 
        text='Count:Q',
        color=alt.value('white')
    )

    contingency_viz = heatmap + text

    # Statistics summary
    stats_text = mo.md(f"""
    **Key Statistics:**

    - **Direct Laryngoscopy Risk:** {direct_risk:.1%} ({direct_deaths.value}/{direct_total})
    - **Blindfolded Risk:** {blind_risk:.1%} ({blind_deaths.value}/{blind_total})
    - **Relative Risk:** {relative_risk:.2f}
    - **Absolute Risk Reduction:** {abs(absolute_risk_reduction):.1%}
    - **Number Needed to Treat:** {number_needed_to_treat:.1f} patients

    **Odds Calculations:**

    - **Direct Laryngoscopy Odds:** {direct_odds:.3f} ({direct_deaths.value}/{direct_survivors.value})
    - **Blindfolded Odds:** {blind_odds:.3f} ({blind_deaths.value}/{blind_survivors.value})
    - **Odds Ratio:** {odds_ratio:.2f}
    """)

    mo.vstack([
        mo.md("### Contingency Table Analysis"),
        mo.hstack([contingency_viz, stats_text], gap=0.5),
        mo.md("")  # Add whitespace after this section
    ])
    return blind_risk, direct_risk, odds_ratio, relative_risk


@app.cell
def _(alt, blind_risk, direct_risk, mo, pd, tabs):
    mo.stop(tabs.value != "Laryngoscopy (Odds)")

    # Risk comparison visualization
    risk_data = pd.DataFrame({
        'Technique': ['Direct Laryngoscopy', 'Blindfolded'],
        'Risk': [direct_risk, blind_risk],
        'Risk_Percent': [direct_risk * 100, blind_risk * 100]
    })

    risk_bars = alt.Chart(risk_data).mark_bar().encode(
        x=alt.X('Technique:O', title='Intubation Technique'),
        y=alt.Y('Risk_Percent:Q', title='Death Risk (%)', scale=alt.Scale(domain=[0, max(direct_risk, blind_risk) * 110])),
        color=alt.Color('Technique:N', scale=alt.Scale(domain=['Direct Laryngoscopy', 'Blindfolded'], 
                                                     range=['#FF6B6B', '#4ECDC4'])),
        tooltip=['Technique', 'Risk_Percent:Q']
    ).properties(
        title='Death Risk by Technique',
        width=400,
        height=300
    )

    # Add text labels on bars
    risk_text = alt.Chart(risk_data).mark_text(
        align='center',
        baseline='bottom',
        fontSize=12,
        fontWeight='bold'
    ).encode(
        x='Technique:O',
        y='Risk_Percent:Q',
        text=alt.Text('Risk_Percent:Q', format='.1f'),
        color=alt.value('black')
    )

    risk_viz = risk_bars + risk_text

    mo.vstack([
        mo.md("### Death Risk Comparison"),
        risk_viz,
        mo.md("")  # Add whitespace
    ])
    return


@app.cell
def _(alt, mo, odds_ratio, pd, relative_risk, tabs):
    mo.stop(tabs.value != "Laryngoscopy (Odds)")

    # Odds ratio and relative risk comparison
    comparison_data = pd.DataFrame({
        'Metric': ['Odds Ratio', 'Relative Risk'],
        'Value': [odds_ratio, relative_risk],
        'Reference_Line': [1.0, 1.0]  # Reference line at 1
    })

    # Calculate appropriate y-axis domain to include reference line
    max_value = max(odds_ratio, relative_risk)
    y_max = max(max_value * 1.1, 1.2)  # Ensure reference line is visible
    y_min = 0  # Always start bars at 0

    comparison_bars = alt.Chart(comparison_data).mark_bar(width=80).encode(
        x=alt.X('Metric:O', title='Statistical Measure'),
        y=alt.Y('Value:Q', title='Ratio Value', scale=alt.Scale(domain=[y_min, y_max])),
        color=alt.Color('Metric:N', scale=alt.Scale(domain=['Odds Ratio', 'Relative Risk'], 
                                                   range=['#FF9999', '#99CCFF'])),
        tooltip=['Metric', 'Value:Q']
    ).properties(
        title='Odds Ratio vs Relative Risk',
        width=400,
        height=300
    )

    # Reference line at 1.0
    ref_line = alt.Chart(comparison_data).mark_rule(strokeDash=[5, 5], color='black').encode(
        y=alt.datum(1.0)
    )

    # Add value labels
    comparison_text = alt.Chart(comparison_data).mark_text(
        align='center',
        baseline='bottom',
        fontSize=12,
        fontWeight='bold'
    ).encode(
        x='Metric:O',
        y='Value:Q',
        text=alt.Text('Value:Q', format='.2f'),
        color=alt.value('black')
    )

    comparison_viz = comparison_bars + ref_line + comparison_text

    mo.vstack([
        mo.md("### Odds Ratio vs Relative Risk"),
        comparison_viz,
        mo.md("---")  # Add separator line
    ])
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Whipple (Tests)")
    mo.md(
        r"""
        ## Statistical Test Selection

        **Clinical Scenario:** Patients undergoing Whipple procedure are randomized into two anesthesia groups:
        - **Group 1:** GETA + Regional anesthesia  
        - **Group 2:** GETA + Ketamine infusion

        **Outcome:** PACU opioid usage measured over 4 hours (continuous variable)

        **Research Question:** Does opioid usage differ between the two anesthesia approaches?

        Use the controls below to explore sample data and see which statistical test is most appropriate.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Whipple (Tests)")

    # Interactive controls for sample data generation
    n_patients = mo.ui.slider(20, 100, value=60, label="Total patients", show_value=True)
    group1_mean = mo.ui.slider(10, 50, value=25, label="Group 1 mean opioid usage (mg)", show_value=True)
    group2_mean = mo.ui.slider(10, 50, value=35, label="Group 2 mean opioid usage (mg)", show_value=True) 
    effect_size = mo.ui.slider(0.1, 2.0, value=0.8, step=0.1, label="Effect size (Cohen's d)", show_value=True)

    mo.vstack([
        mo.hstack([n_patients, effect_size]),
        mo.hstack([group1_mean, group2_mean])
    ])
    return effect_size, group1_mean, group2_mean, n_patients


@app.cell
def _(
    effect_size,
    group1_mean,
    group2_mean,
    mo,
    n_patients,
    np,
    pd,
    stats,
    tabs,
):
    mo.stop(tabs.value != "Whipple (Tests)")

    # Generate sample data
    np.random.seed(42)  # For reproducible results

    n_group1 = n_patients.value // 2
    n_group2 = n_patients.value - n_group1

    # Calculate standard deviation based on effect size
    # Cohen's d = (mean1 - mean2) / pooled_std
    mean_diff = abs(group2_mean.value - group1_mean.value)
    pooled_std = mean_diff / effect_size.value if effect_size.value > 0 else 10

    # Generate data
    group1_data = np.random.normal(group1_mean.value, pooled_std, n_group1)
    group2_data = np.random.normal(group2_mean.value, pooled_std, n_group2)

    # Ensure no negative values (opioid usage can't be negative)
    group1_data = np.maximum(group1_data, 0)
    group2_data = np.maximum(group2_data, 0)

    # Create combined dataset
    whipple_data = pd.DataFrame({
        'patient_id': range(1, n_patients.value + 1),
        'group': ['GETA + Regional'] * n_group1 + ['GETA + Ketamine'] * n_group2,
        'opioid_usage': np.concatenate([group1_data, group2_data])
    })

    # Perform statistical tests
    t_stat, t_pvalue = stats.ttest_ind(group1_data, group2_data)

    # Also perform Mann-Whitney U test (non-parametric alternative)
    u_stat, u_pvalue = stats.mannwhitneyu(group1_data, group2_data, alternative='two-sided')

    # Calculate descriptive statistics
    group1_stats = {
        'mean': np.mean(group1_data),
        'std': np.std(group1_data, ddof=1),
        'median': np.median(group1_data),
        'n': n_group1
    }

    group2_stats = {
        'mean': np.mean(group2_data),
        'std': np.std(group2_data, ddof=1),
        'median': np.median(group2_data),
        'n': n_group2
    }

    whipple_data
    return (
        group1_stats,
        group2_stats,
        t_pvalue,
        t_stat,
        u_pvalue,
        u_stat,
        whipple_data,
    )


@app.cell
def _(
    alt,
    group1_stats,
    group2_stats,
    mo,
    t_pvalue,
    t_stat,
    tabs,
    u_pvalue,
    u_stat,
    whipple_data,
):
    mo.stop(tabs.value != "Whipple (Tests)")

    # Create box plot visualization
    box_plot = alt.Chart(whipple_data).mark_boxplot(size=60).encode(
        x=alt.X('group:N', title='Anesthesia Group'),
        y=alt.Y('opioid_usage:Q', title='PACU Opioid Usage (mg)', scale=alt.Scale(zero=False)),
        color=alt.Color('group:N', scale=alt.Scale(domain=['GETA + Regional', 'GETA + Ketamine'], 
                                                 range=['#FF6B6B', '#4ECDC4']))
    ).properties(
        title='PACU Opioid Usage by Anesthesia Group',
        width=400,
        height=300
    )

    # Add individual points
    strip_plot = alt.Chart(whipple_data).mark_circle(
        opacity=0.6,
        size=40
    ).encode(
        x=alt.X('group:N', title='Anesthesia Group'),
        y=alt.Y('opioid_usage:Q', title='PACU Opioid Usage (mg)'),
        color=alt.Color('group:N', scale=alt.Scale(domain=['GETA + Regional', 'GETA + Ketamine'], 
                                                 range=['#FF6B6B', '#4ECDC4'])),
        tooltip=['patient_id:O', 'group:N', 'opioid_usage:Q']
    )

    combined_plot = box_plot + strip_plot

    # Statistical results summary
    stats_summary = mo.md(f"""
    **Descriptive Statistics:**

    **GETA + Regional (n={group1_stats['n']})**

    - Mean: {group1_stats['mean']:.1f} ± {group1_stats['std']:.1f} mg
    - Median: {group1_stats['median']:.1f} mg

    **GETA + Ketamine (n={group2_stats['n']})**

    - Mean: {group2_stats['mean']:.1f} ± {group2_stats['std']:.1f} mg  
    - Median: {group2_stats['median']:.1f} mg

    **Statistical Test Results:**

    **Independent t-test:**

    - t-statistic: {t_stat:.3f}
    - p-value: {t_pvalue:.4f}
    - Result: {'Significant' if t_pvalue < 0.05 else 'Not significant'} (α = 0.05)

    **Mann-Whitney U test:**

    - U-statistic: {u_stat:.1f}
    - p-value: {u_pvalue:.4f}
    - Result: {'Significant' if u_pvalue < 0.05 else 'Not significant'} (α = 0.05)
    """)

    mo.hstack([combined_plot, stats_summary], gap=0.5)
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Whipple (Tests)")

    mo.md("""
    ### Statistical Test Selection Guide

    **Most Appropriate Test: Independent t-test (two-sample t-test)**

    **Why this test is correct:**

    1. **Independent groups**: Patients are randomized to different anesthesia groups
    2. **Continuous outcome**: Opioid usage is measured in mg (continuous variable)
    3. **Two groups**: Comparing exactly 2 treatment arms
    4. **Unpaired data**: Each patient receives only one type of anesthesia

    **Key assumptions to check:**

    - **Normality**: Opioid usage should be approximately normally distributed in each group
    - **Equal variances**: Groups should have similar variability (can use Welch's t-test if violated)
    - **Independence**: Random assignment ensures this

    **Alternative tests to consider:**

    - **Mann-Whitney U test**: If data is not normally distributed (non-parametric alternative)
    - **Welch's t-test**: If variances are unequal between groups

    **Tests that would be INCORRECT:**

    - **ANOVA**: Only needed for ≥3 groups
    - **Paired t-test**: Would be used if same patients received both treatments
    - **Chi-square**: Used for categorical outcomes, not continuous
    - **Correlation**: Tests association, not group differences
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    Please send any feedback to Sasank at sasank.desaraju@ufl.edu.

    He'd love to hear what's helpful, not helpful, and any suggestions for future notebooks!
    """
    )
    return


if __name__ == "__main__":
    app.run()
