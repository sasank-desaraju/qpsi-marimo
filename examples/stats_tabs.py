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
    return alt, auc, confusion_matrix, mo, np, pd, roc_curve, stats


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Stats Tabs

    This app makes cool visualizations for some stats concepts.

    Use the tabs below to explore different statistical concepts with interactive visualizations.
    """
    )
    return


@app.cell
def _(mo):
    tabs = mo.ui.tabs({
        "Central Limit Theorem": mo.md(""),
        "Confidence Intervals": mo.md(""), 
        "Hypothesis Testing": mo.md(""),
        "ROC Analysis": mo.md(""),
        "Correlation vs Causation": mo.md("")
    })
    tabs
    return (tabs,)


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Central Limit Theorem")
    mo.md(
        r"""
        ## Central Limit Theorem

        The Central Limit Theorem states that the distribution of sample means approaches a normal distribution 
        as the sample size increases, regardless of the population distribution.

        Adjust the parameters below to see this in action:
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Central Limit Theorem")

    # CLT controls
    population_dist = mo.ui.dropdown(
        options=["uniform", "exponential", "bimodal"], 
        value="uniform", 
        label="Population Distribution"
    )
    sample_size = mo.ui.slider(1, 100, value=10, label="Sample Size", show_value=True)
    num_samples = mo.ui.slider(100, 2000, value=1000, label="Number of Samples", show_value=True)

    mo.hstack([population_dist, sample_size, num_samples])
    return num_samples, population_dist, sample_size


@app.cell
def _(alt, mo, np, num_samples, pd, population_dist, sample_size, tabs):
    mo.stop(tabs.value != "Central Limit Theorem")

    # Generate population data
    if population_dist.value == "uniform":
        population = np.random.uniform(0, 10, size=10000)
    elif population_dist.value == "exponential":
        population = np.random.exponential(2, size=10000)
    else:  # bimodal
        pop1 = np.random.normal(3, 1, 5000)
        pop2 = np.random.normal(7, 1, 5000)
        population = np.concatenate([pop1, pop2])

    # Generate sample means
    sample_means = []
    for _ in range(num_samples.value):
        sample = np.random.choice(population, size=sample_size.value)
        sample_means.append(np.mean(sample))

    # Create DataFrames for plotting
    pop_df = pd.DataFrame({"value": population, "type": "Population"})
    means_df = pd.DataFrame({"value": sample_means, "type": "Sample Means"})

    # Population distribution plot
    pop_plot = alt.Chart(pop_df).transform_density(
        'value',
        as_=['value', 'density']
    ).mark_area(opacity=0.7, color='lightblue').encode(
        x=alt.X('value:Q', title='Value'),
        y=alt.Y('density:Q', title='Density')
    ).properties(
        title=f'Population Distribution ({population_dist.value})',
        width=400,
        height=200
    )

    # Sample means distribution plot
    means_plot = alt.Chart(means_df).transform_density(
        'value',
        as_=['value', 'density']
    ).mark_area(opacity=0.7, color='orange').encode(
        x=alt.X('value:Q', title='Sample Mean'),
        y=alt.Y('density:Q', title='Density')
    ).properties(
        title=f'Distribution of Sample Means (n={sample_size.value})',
        width=400,
        height=200
    )

    alt.vconcat(pop_plot, means_plot)
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Confidence Intervals")
    mo.md(
        r"""
        ## Confidence Intervals

        A confidence interval gives us a range of plausible values for a population parameter. 
        The confidence level tells us how often the interval would contain the true parameter 
        if we repeated the experiment many times.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Confidence Intervals")

    # CI controls
    true_mean = mo.ui.slider(40, 60, value=50, label="True Population Mean", show_value=True)
    sample_size_ci = mo.ui.slider(10, 200, value=30, label="Sample Size", show_value=True)
    confidence_level = mo.ui.slider(0.8, 0.99, value=0.95, step=0.01, label="Confidence Level", show_value=True)
    num_intervals = mo.ui.slider(50, 200, value=100, label="Number of Intervals", show_value=True)

    mo.hstack([true_mean, sample_size_ci, confidence_level, num_intervals])
    return confidence_level, num_intervals, sample_size_ci, true_mean


@app.cell
def _(
    alt,
    confidence_level,
    mo,
    np,
    num_intervals,
    pd,
    sample_size_ci,
    stats,
    tabs,
    true_mean,
):
    mo.stop(tabs.value != "Confidence Intervals")

    # Generate confidence intervals
    np.random.seed(42)  # For reproducibility
    intervals_data = []
    contains_true = 0

    for i in range(num_intervals.value):
        # Generate sample from normal distribution
        sample_ci = np.random.normal(true_mean.value, 10, sample_size_ci.value)

        # Calculate confidence interval
        sample_mean_ci = np.mean(sample_ci)
        sample_std_ci = np.std(sample_ci, ddof=1)
        sem_ci = sample_std_ci / np.sqrt(sample_size_ci.value)

        # Use t-distribution for small samples
        t_val_ci = stats.t.ppf((1 + confidence_level.value) / 2, sample_size_ci.value - 1)
        margin_error_ci = t_val_ci * sem_ci

        ci_lower = sample_mean_ci - margin_error_ci
        ci_upper = sample_mean_ci + margin_error_ci

        # Check if interval contains true mean
        contains = ci_lower <= true_mean.value <= ci_upper
        if contains:
            contains_true += 1

        intervals_data.append({
            'interval_id': i,
            'sample_mean': sample_mean_ci,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'contains_true': contains
        })

    intervals_df = pd.DataFrame(intervals_data)

    # Create visualization
    base = alt.Chart(intervals_df).add_selection(
        alt.selection_interval(bind='scales', encodings=['y'])
    )

    # Confidence intervals as error bars
    intervals_chart = base.mark_rule().encode(
        x=alt.X('ci_lower:Q', title='Value'),
        x2='ci_upper:Q',
        y=alt.Y('interval_id:O', title='Sample Number', axis=alt.Axis(labels=False, ticks=False)),
        color=alt.Color('contains_true:N', 
                       scale=alt.Scale(domain=[True, False], range=['steelblue', 'red']),
                       legend=alt.Legend(title="Contains True Mean"))
    ).properties(
        title=f'Confidence Intervals: {contains_true}/{num_intervals.value} contain true mean ({contains_true/num_intervals.value:.1%})',
        width=600,
        height=400
    )

    # Sample means as points
    means_chart = base.mark_circle(size=30).encode(
        x='sample_mean:Q',
        y='interval_id:O',
        color=alt.Color('contains_true:N', 
                       scale=alt.Scale(domain=[True, False], range=['steelblue', 'red']))
    )

    # True mean line
    true_mean_line = alt.Chart(pd.DataFrame({'true_mean': [true_mean.value]})).mark_rule(
        color='black', strokeWidth=2, strokeDash=[5, 5]
    ).encode(
        x='true_mean:Q'
    )

    intervals_chart + means_chart + true_mean_line
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Hypothesis Testing")
    mo.md(
        r"""
        ## Hypothesis Testing

        Hypothesis testing allows us to make decisions about populations based on sample data.
        We can visualize p-values and explore Type I and Type II errors.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Hypothesis Testing")

    # Hypothesis testing controls
    null_mean = mo.ui.slider(45, 55, value=50, label="Null Hypothesis Mean", show_value=True)
    true_mean_ht = mo.ui.slider(45, 55, value=52, label="True Mean", show_value=True)
    sample_size_ht = mo.ui.slider(10, 100, value=25, label="Sample Size", show_value=True)
    alpha_level = mo.ui.slider(0.01, 0.10, value=0.05, step=0.01, label="Significance Level (α)", show_value=True)

    mo.hstack([null_mean, true_mean_ht, sample_size_ht, alpha_level])
    return alpha_level, null_mean, sample_size_ht, true_mean_ht


@app.cell
def _(
    alpha_level,
    alt,
    mo,
    np,
    null_mean,
    pd,
    sample_size_ht,
    stats,
    tabs,
    true_mean_ht,
):
    mo.stop(tabs.value != "ht_content")

    # Generate sample data
    np.random.seed(123)
    sample_ht = np.random.normal(true_mean_ht.value, 5, sample_size_ht.value)
    sample_mean_ht = np.mean(sample_ht)
    sample_std_ht = np.std(sample_ht, ddof=1)

    # Calculate t-statistic and p-value
    t_stat = (sample_mean_ht - null_mean.value) / (sample_std_ht / np.sqrt(sample_size_ht.value))
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), sample_size_ht.value - 1))

    # Critical values
    t_crit = stats.t.ppf(1 - alpha_level.value/2, sample_size_ht.value - 1)

    # Create t-distribution for visualization
    x_vals = np.linspace(-4, 4, 1000)
    y_vals = stats.t.pdf(x_vals, sample_size_ht.value - 1)

    t_dist_df = pd.DataFrame({
        'x': x_vals,
        'y': y_vals
    })

    # Base t-distribution
    t_dist_chart = alt.Chart(t_dist_df).mark_line(color='blue').encode(
        x=alt.X('x:Q', title='t-statistic'),
        y=alt.Y('y:Q', title='Probability Density')
    ).properties(
        title=f'T-distribution (df={sample_size_ht.value-1}), t-stat={t_stat:.2f}, p-value={p_value:.4f}',
        width=500,
        height=300
    )

    # Critical regions
    critical_left = alt.Chart(pd.DataFrame({
        'x': x_vals[x_vals <= -t_crit],
        'y': y_vals[x_vals <= -t_crit]
    })).mark_area(opacity=0.3, color='red').encode(x='x:Q', y='y:Q')

    critical_right = alt.Chart(pd.DataFrame({
        'x': x_vals[x_vals >= t_crit],
        'y': y_vals[x_vals >= t_crit]
    })).mark_area(opacity=0.3, color='red').encode(x='x:Q', y='y:Q')

    # Test statistic line
    test_stat_line = alt.Chart(pd.DataFrame({'t_stat': [t_stat]})).mark_rule(
        color='orange', strokeWidth=3
    ).encode(x='t_stat:Q')

    # Decision
    reject_null = abs(t_stat) > t_crit
    decision_text = "Reject H₀" if reject_null else "Fail to reject H₀"

    final_chart = t_dist_chart + critical_left + critical_right + test_stat_line

    # Display results
    mo.md(f"""
    **Sample Mean:** {sample_mean_ht:.2f}  
    **Test Statistic:** {t_stat:.3f}  
    **P-value:** {p_value:.4f}  
    **Critical Value:** ±{t_crit:.3f}  
    **Decision:** {decision_text}
    """)

    final_chart
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "ROC Analysis")
    mo.md(
        r"""
        ## ROC Analysis

        ROC (Receiver Operating Characteristic) curves help us understand diagnostic test performance.
        We model a biomarker that discriminates between sick and healthy populations.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "ROC Analysis")

    # ROC analysis controls
    sick_count = mo.ui.number(value=100, label='Sick Count')
    healthy_count = mo.ui.number(value=100, label='Healthy Count')

    sick_mean_roc = mo.ui.slider(start=20, stop=40, value=30, label='Sick Mean', show_value=True)
    healthy_mean_roc = mo.ui.slider(start=10, stop=30, value=20, label='Healthy Mean', show_value=True)

    sick_std_roc = mo.ui.slider(start=1, stop=8, value=5, label='Sick Std Dev', show_value=True)
    healthy_std_roc = mo.ui.slider(start=1, stop=8, value=5, label='Healthy Std Dev', show_value=True)

    cutoff_roc = mo.ui.slider(start=15, stop=35, value=25, label='Cutoff Value', show_value=True)

    mo.vstack([
        mo.hstack([sick_count, sick_mean_roc, sick_std_roc]),
        mo.hstack([healthy_count, healthy_mean_roc, healthy_std_roc]),
        cutoff_roc
    ])
    return (
        cutoff_roc,
        healthy_count,
        healthy_mean_roc,
        healthy_std_roc,
        sick_count,
        sick_mean_roc,
        sick_std_roc,
    )


@app.cell
def _(
    alt,
    cutoff_roc,
    healthy_count,
    healthy_mean_roc,
    healthy_std_roc,
    mo,
    np,
    pd,
    sick_count,
    sick_mean_roc,
    sick_std_roc,
    tabs,
):
    mo.stop(tabs.value != "ROC Analysis")

    # Generate biomarker data
    np.random.seed(42)
    sick_values = np.random.normal(sick_mean_roc.value, sick_std_roc.value, sick_count.value)
    healthy_values = np.random.normal(healthy_mean_roc.value, healthy_std_roc.value, healthy_count.value)

    # Create DataFrame
    biomarker_df = pd.DataFrame({
        'Value': np.concatenate([sick_values, healthy_values]),
        'Condition': ['Sick'] * len(sick_values) + ['Healthy'] * len(healthy_values),
        'True_Label': [1] * len(sick_values) + [0] * len(healthy_values)
    })

    # Distribution plots
    sick_dist = alt.Chart(biomarker_df[biomarker_df['Condition'] == 'Sick']).transform_density(
        'Value',
        as_=['Value', 'Density']
    ).mark_area(opacity=0.6, color='orange').encode(
        x=alt.X('Value:Q', title='Biomarker Value'),
        y=alt.Y('Density:Q', title='Density')
    )

    healthy_dist = alt.Chart(biomarker_df[biomarker_df['Condition'] == 'Healthy']).transform_density(
        'Value',
        as_=['Value', 'Density']
    ).mark_area(opacity=0.6, color='steelblue').encode(
        x=alt.X('Value:Q'),
        y=alt.Y('Density:Q')
    )

    # Cutoff line
    cutoff_line_roc = alt.Chart(pd.DataFrame({'cutoff': [cutoff_roc.value]})).mark_rule(
        color='red', strokeWidth=2
    ).encode(x='cutoff:Q')

    # Scatter plot with jitter
    scatter_plot = alt.Chart(biomarker_df).mark_circle(size=40, opacity=0.6).encode(
        x=alt.X('Value:Q'),
        yOffset="jitter:Q",
        color=alt.Color('Condition:N', scale=alt.Scale(domain=['Sick', 'Healthy'], range=['orange', 'steelblue']))
    ).properties(
        height=80
    ).transform_calculate(
        jitter="sqrt(-2*log(random()))*cos(2*PI*random())"
    )

    biomarker_viz = alt.vconcat(
        (sick_dist + healthy_dist + cutoff_line_roc).properties(
            title='Biomarker Distributions',
            width=500,
            height=250
        ),
        (scatter_plot + cutoff_line_roc).properties(
            title='Individual Values',
            width=500
        )
    )

    biomarker_viz
    return (biomarker_df,)


@app.cell
def _(alt, biomarker_df, confusion_matrix, cutoff_roc, mo, pd, tabs):
    mo.stop(tabs.value != "ROC Analysis")

    # Calculate confusion matrix
    predictions = (biomarker_df['Value'] > cutoff_roc.value).astype(int)
    true_labels = biomarker_df['True_Label'].values

    cm = confusion_matrix(true_labels, predictions)
    tn, fp, fn, tp = cm.ravel()

    # Create confusion matrix visualization
    conf_data = pd.DataFrame({
        'Actual': ['Negative', 'Negative', 'Positive', 'Positive'],
        'Predicted': ['Negative', 'Positive', 'Negative', 'Positive'],
        'Count': [tn, fp, fn, tp],
        'Label': ['TN', 'FP', 'FN', 'TP']
    })

    confusion_heatmap = alt.Chart(conf_data).mark_rect().encode(
        x=alt.X('Predicted:O', title='Predicted'),
        y=alt.Y('Actual:O', title='Actual'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues')),
        tooltip=['Actual', 'Predicted', 'Count', 'Label']
    ).properties(
        title='Confusion Matrix',
        width=250,
        height=250
    )

    # Add text labels
    confusion_text = alt.Chart(conf_data).mark_text(
        fontSize=16,
        fontWeight='bold'
    ).encode(
        x='Predicted:O',
        y='Actual:O',
        text='Count:Q',
        color=alt.value('white')
    )

    confusion_viz = confusion_heatmap + confusion_text

    # Calculate metrics
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    metrics_text = mo.md(f"""
    **Performance Metrics:**
    - Sensitivity (True Positive Rate): {sensitivity:.3f}
    - Specificity (True Negative Rate): {specificity:.3f}
    - False Positive Rate: {1-specificity:.3f}
    """)

    mo.hstack([confusion_viz, mo.vstack([metrics_text])])
    return sensitivity, specificity


@app.cell
def _(
    alt,
    auc,
    biomarker_df,
    cutoff_roc,
    mo,
    pd,
    roc_curve,
    sensitivity,
    specificity,
    tabs,
):
    mo.stop(tabs.value != "ROC Analysis")

    # Generate ROC curve data
    y_true = biomarker_df['True_Label'].values
    y_scores = biomarker_df['Value'].values

    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    # Create ROC curve DataFrame
    roc_df = pd.DataFrame({
        'False Positive Rate': fpr,
        'True Positive Rate': tpr,
        'Threshold': thresholds if len(thresholds) == len(fpr) else list(thresholds) + [thresholds[-1]]
    })

    # ROC curve plot
    roc_plot = alt.Chart(roc_df).mark_line(point=True, color='blue').encode(
        x=alt.X('False Positive Rate:Q', scale=alt.Scale(domain=[0, 1])),
        y=alt.Y('True Positive Rate:Q', scale=alt.Scale(domain=[0, 1])),
        tooltip=['False Positive Rate', 'True Positive Rate', 'Threshold']
    ).properties(
        title=f'ROC Curve (AUC = {roc_auc:.3f})',
        width=400,
        height=400
    )

    # Diagonal reference line
    diagonal = alt.Chart(pd.DataFrame({
        'x': [0, 1],
        'y': [0, 1]
    })).mark_line(strokeDash=[5, 5], color='gray').encode(
        x='x:Q',
        y='y:Q'
    )

    # Current cutoff point
    current_fpr = 1 - specificity
    current_point = alt.Chart(pd.DataFrame({
        'fpr': [current_fpr],
        'tpr': [sensitivity]
    })).mark_circle(size=100, color='red').encode(
        x='fpr:Q',
        y='tpr:Q',
        tooltip=alt.value(f'Current Cutoff: {cutoff_roc.value}')
    )

    roc_final = roc_plot + diagonal + current_point
    roc_final
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Correlation vs Causation")
    mo.md(
        r"""
        ## Correlation vs Causation

        One of the most important concepts in statistics: correlation does not imply causation.
        Let's explore this with interactive examples.
        """
    )
    return


@app.cell
def _(mo, tabs):
    mo.stop(tabs.value != "Correlation vs Causation")

    # Correlation controls
    scenario = mo.ui.dropdown(
        options=["Ice cream and drowning", "Shoe size and reading ability", "Custom relationship"],
        value="Ice cream and drowning",
        label="Scenario"
    )

    correlation_strength = mo.ui.slider(-1, 1, value=0.7, step=0.1, label="Correlation Strength", show_value=True)
    sample_size_corr = mo.ui.slider(50, 500, value=200, label="Sample Size", show_value=True)

    mo.hstack([scenario, correlation_strength, sample_size_corr])
    return correlation_strength, sample_size_corr, scenario


@app.cell
def _(alt, correlation_strength, mo, np, pd, sample_size_corr, scenario, tabs):
    mo.stop(tabs.value != "Correlation vs Causation")

    np.random.seed(42)

    if scenario.value == "Ice cream and drowning":
        # Temperature as confounding variable
        temperature = np.random.uniform(60, 100, sample_size_corr.value)

        # Ice cream sales increase with temperature + noise
        ice_cream = 2 * temperature + np.random.normal(0, 10, sample_size_corr.value)

        # Drownings increase with temperature (more swimming) + noise
        drownings = 0.1 * temperature + np.random.normal(0, 2, sample_size_corr.value)

        corr_df = pd.DataFrame({
            'x': ice_cream,
            'y': drownings,
            'temperature': temperature
        })

        x_label, y_label = "Ice Cream Sales", "Drowning Incidents"
        confounding_var = "Temperature"

    elif scenario.value == "Shoe size and reading ability":
        # Age as confounding variable
        age = np.random.uniform(5, 18, sample_size_corr.value)

        # Shoe size increases with age + noise
        shoe_size = 0.8 * age + 3 + np.random.normal(0, 1, sample_size_corr.value)

        # Reading ability increases with age + noise
        reading_score = 5 * age + 20 + np.random.normal(0, 8, sample_size_corr.value)

        corr_df = pd.DataFrame({
            'x': shoe_size,
            'y': reading_score,
            'age': age
        })

        x_label, y_label = "Shoe Size", "Reading Score"
        confounding_var = "Age"

    else:  # Custom relationship
        # Generate correlated data
        x = np.random.normal(0, 1, sample_size_corr.value)
        y = correlation_strength.value * x + np.sqrt(1 - correlation_strength.value**2) * np.random.normal(0, 1, sample_size_corr.value)

        corr_df = pd.DataFrame({
            'x': x,
            'y': y,
            'confounding': np.random.uniform(0, 1, sample_size_corr.value)
        })

        x_label, y_label = "Variable X", "Variable Y"
        confounding_var = "Confounding Variable"

    # Calculate correlation
    actual_correlation = np.corrcoef(corr_df['x'], corr_df['y'])[0, 1]

    # Create scatter plot
    scatter = alt.Chart(corr_df).mark_circle(size=60, opacity=0.7).encode(
        x=alt.X('x:Q', title=x_label),
        y=alt.Y('y:Q', title=y_label),
        color=alt.Color(list(corr_df.columns)[2] + ':Q', 
                       scale=alt.Scale(scheme='viridis'),
                       legend=alt.Legend(title=confounding_var)) if scenario.value != "Custom relationship" else alt.value('steelblue'),
        tooltip=['x:Q', 'y:Q'] + ([list(corr_df.columns)[2] + ':Q'] if scenario.value != "Custom relationship" else [])
    ).properties(
        title=f'{scenario.value}: Correlation = {actual_correlation:.3f}',
        width=500,
        height=400
    )

    # Add regression line
    regression = scatter.transform_regression('x', 'y').mark_line(color='red', strokeWidth=2)

    correlation_viz = scatter + regression

    # Explanation text
    if scenario.value == "Ice cream and drowning":
        explanation = """
        **Explanation:** Ice cream sales and drowning incidents are both caused by hot weather (temperature).
        People buy more ice cream when it's hot, and more people swim (and potentially drown) when it's hot.
        The correlation doesn't mean ice cream causes drowning!
        """
    elif scenario.value == "Shoe size and reading ability":
        explanation = """
        **Explanation:** Shoe size and reading ability are both caused by age.
        Older children have bigger feet and better reading skills.
        Having bigger feet doesn't make you a better reader!
        """
    else:
        explanation = f"""
        **Explanation:** This shows a correlation of {actual_correlation:.3f} between two variables.
        Remember: correlation measures how variables move together, but doesn't tell us if one causes the other.
        """

    mo.vstack([correlation_viz, mo.md(explanation)])
    return


if __name__ == "__main__":
    app.run()
