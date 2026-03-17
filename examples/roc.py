# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==5.5.0",
#     "ipywidgets==8.1.7",
#     "matplotlib==3.10.5",
#     "numpy==2.3.2",
#     "pandas==2.3.2",
#     "scikit-learn==1.7.2",
#     "seaborn==0.13.2",
#     "marimo>=0.17.0",
#     "pyzmq",
# ]
# ///

import marimo

__generated_with = "0.18.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    #import seaborn as sns
    import altair as alt
    import math
    return alt, math, mo, np, pd, plt


@app.cell
def _(mo):
    mo.md(r"""
    # How does a test tell us who's sick?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Motivation

    When we run a diagnostic test that can tell us if someone is sick, what's going on under the hood?

    Well, first, the inventors of the test need to find some biomarker number that tends to be pretty different between sick and healthy individuals. Then, they choose some cutoff value that splits these two populations the best they can.

    So when we run a test, we're seeing on which side of this cutoff the patient's biomarker falls.

    Let's explore this with an example and see how it connects to other concepts we know, such as a confusion matrix and ROC curve.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Our Model

    We'll model the values of the test biomarker as normally distributed with a mean and standard deviation that we can control.
    We also have a box for the number of Sick and Healthy people.
    """)
    return


@app.cell
def _(mo):
    # Get population data
    sick_number = mo.ui.number(value=60, label='Sick Count')
    healthy_number = mo.ui.number(value=60, label='Healthy Count')

    sick_mean = mo.ui.slider(start=0, stop=50, value=30, label='Sick Mean', show_value=True)
    healthy_mean = mo.ui.slider(start=0, stop=50, value=20, label='Healthy Mean', show_value=True)

    sick_std = mo.ui.slider(start=0.5, stop=10, value=5, label='Sick Std Dev', show_value=True)
    healthy_std = mo.ui.slider(start=0.5, stop=10, value=5, label='Healthy Std Dev', show_value=True)

    mo.vstack([mo.hstack([sick_number, sick_mean, sick_std]),
              mo.hstack([healthy_number, healthy_mean, healthy_std])])
    return (
        healthy_mean,
        healthy_number,
        healthy_std,
        sick_mean,
        sick_number,
        sick_std,
    )


@app.cell
def _(
    healthy_mean,
    healthy_number,
    healthy_std,
    np,
    pd,
    sick_mean,
    sick_number,
    sick_std,
):
    # Create dataframe
    sick_data = np.random.normal(sick_mean.value, sick_std.value, sick_number.value)
    healthy_data = np.random.normal(healthy_mean.value, healthy_std.value, healthy_number.value)

    # Create a DataFrame for Altair
    df = pd.DataFrame({
        'Value': np.concatenate([sick_data, healthy_data]),
        'Condition': ['Sick'] * len(sick_data) + ['Healthy'] * len(healthy_data)
    })
    return df, healthy_data, sick_data


@app.cell
def _(mo):
    mo.md(r"""
    Here we see a scatter plot and a Gaussian of the values.
    Sick and Healthy patients have values that tend to be different, though there is some overlap.
    """)
    return


@app.cell
def _(alt, cutoff_line, df):
    dp = alt.Chart(df).mark_point().encode(
        # x='Value:Q',
        x=alt.X('Value:Q'),
        yOffset="jitter:Q",
        color='Condition:N'
    ).properties(
        title='Scatter Plot of Values',
        # width=600,
        height=50
    ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter="sqrt(-2*log(random()))*cos(2*PI*random())"
    )

    # BUG: Since the random() above is recalculated every time the cutoff_line changes, it all jitters as you change the slider
    # This could be fixed by making it so that the below plotting happens in a different cell
    dp = dp + cutoff_line
    dp
    return


@app.cell
def _(alt, cutoff_line, df):
    dens_sick = alt.Chart(df.loc[df['Condition'] == 'Sick']).transform_density(
        'Value',
        as_=['Value', 'Density'],
    ).mark_area(opacity=0.5, color='orange').encode(
        x=alt.X('Value:Q'),
        y=alt.Y('Density:Q'),
        # color='blue'
    )
    dens_healthy = alt.Chart(df.loc[df['Condition'] == 'Healthy']).transform_density(
        'Value',
        as_=['Value', 'Density'],
    ).mark_area(opacity=0.5).encode(
        x=alt.X('Value:Q'),
        y=alt.Y('Density:Q'),
        # color='orange'
    )
    dens = dens_healthy + dens_sick
    dens = dens.properties(
        title='Density Distribution'
    )

    # This plot is not accurate for some reason.
    # The overall mass of A (sick) looks far larger than that of B (healthy)
    # dens = alt.Chart(df).transform_density(
    #     'Value',
    #     groupby=['Condition'],
    #     as_=['Value', 'Density'],
    # ).mark_area(opacity=0.5).encode(
    #     x=alt.X('Value:Q'),
    #     y=alt.Y('Density:Q'),
    #     color='Condition:N'
    # )
    dens = dens + cutoff_line
    dens
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Cutoff

    The vertical line on the plot above is our chosen cutoff value.
    When a patient's biomarker is above the cutoff value (to its right), we classify them as having a "positive" test value.
    Left of the cutoff line, accordingly, corresponds to a "negative" test result.

    Use the **slider** below to change the cutoff value.
    Note the metrics that are automatically calculated below.
    """)
    return


@app.cell
def _(df, math, mo):
    cutoff_slider = mo.ui.slider(
        start=math.floor(min(df['Value'])),
        stop=math.ceil(max(df['Value'])),
        # start=0,
        # stop=50,
        value=24,
        label='Cutoff Line Position',
        show_value=True
    )
    mo.hstack([cutoff_slider])
    return (cutoff_slider,)


@app.cell
def _(alt, cutoff_slider, pd):
    cutoff = cutoff_slider.value
    cutoff_line = alt.Chart(pd.DataFrame({'cutoff': [cutoff]})).mark_rule(color='red').encode(
    # cutoff_line = alt.Chart().mark_rule(color='red').encode(
        x='cutoff:Q',
        size=alt.value(2),
    )
    return cutoff, cutoff_line


@app.cell
def _(healthy_data, np, sick_data):
    # Helper function for getting stats from cutoff
    def eval_cutoff(sick, healthy, cutoff):
        # Sensitivity and specificity calculation
        tp = np.sum(sick_data > cutoff)
        fn = np.sum(sick_data <= cutoff)
        tn = np.sum(healthy_data <= cutoff)
        fp = np.sum(healthy_data > cutoff)

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        return sensitivity, specificity, tp, fn, tn, fp
    return (eval_cutoff,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Confusion Matrix

    Note the confusion matrix.
    As the cutoff value splits the distributions as seen above, we get improved results with our confusion matrix.
    """)
    return


@app.cell
def _(alt, cutoff, eval_cutoff, healthy_data, pd, sick_data):
    # Confusion Matrix
    _sens, _spec, _tp, _fn, _tn, _fp = eval_cutoff(sick_data, healthy_data, cutoff)
    _data = {
        'Actual': ['Positive', 'Positive', 'Negative', 'Negative'],
        'Predicted': ['Positive', 'Negative', 'Positive', 'Negative'],
        'Count': [_tp, _fn, _fp, _tn]
    }
    conf_df = pd.DataFrame(_data)
    # Create the heatmap using Altair
    heatmap = alt.Chart(conf_df).mark_rect(color='blue').encode(
        x='Predicted:O',
        y='Actual:O',
        color='Count:Q'
    ).properties(
        width=300,
        height=300,
        title='Confusion Matrix'
    )

    # Add text labels
    text = heatmap.mark_text().encode(
        text='Count:Q',
        color=alt.value('black')  # Set text color to black for better readability
    )

    # Combine the heatmap and text labels
    final_heatmap = heatmap + text

    final_heatmap
    return


@app.cell
def _(alt, df, eval_cutoff, healthy_data, math, pd, sick_data):
    # Static ROC Dataframe and Curve
    # TODO: Add Area Under Curve (AUC) to the ROC curve.
    # This will show how this statistic is inherent to how well the biomarker or whatever discriminates between the groups
    # And how it doesn't change based off of cutoff value choice
    # Calculate in this cell. Maybe by doing a triangle sum from all the sens/(1-spec) values.
    # Implement as an atl.Chart.mark_area() of the already existing Chart but try to add the number in the area
    roc_data = []
    # for cutoff_val in range(math.floor(min(df['Value'])), math.ceil(max(df['Value'])), 20):
    for cutoff_val in range(0, math.ceil(max(df['Value'])), 1):
        sens, spec, _tp, _fn, _tn, _fp = eval_cutoff(sick_data, healthy_data, cutoff_val)
        roc_data.append({'Cutoff': cutoff_val, 'True Positive Rate': sens, 'False Positive Rate': 1 - spec})
    roc_data = pd.DataFrame(roc_data)    # roc_data

    # roc = alt.Chart(roc_data).mark_line(point=True).encode(
    roc = alt.Chart(
        roc_data,
        title=alt.Title(
            "ROC Curve",
            subtitle="Receiver Operating Characteristic Curve"
        )
    ).mark_line(point=True).encode(
        y=alt.Y('True Positive Rate:Q'),
        x=alt.X('False Positive Rate:Q'),
        order='Cutoff',
        tooltip=['Cutoff', 'True Positive Rate', 'False Positive Rate']
    # ).properties(
        # width=600
    )
    return (roc,)


@app.cell
def _(mo):
    mo.md(r"""
    ## ROC Curve

    We can appreciate how the ROC curve is created by marking the true positive rate and false positive rate as we iterate through our cutoff value.
    """)
    return


@app.cell
def _(alt, cutoff, eval_cutoff, healthy_data, pd, roc, sick_data):
    # ROC Current Value and Display
    _sens, _spec, _tp, _fn, _tn, _fp = eval_cutoff(sick_data, healthy_data, cutoff)
    # current_stats = pd.DataFrame({'Cutoff': cutoff, 'True Positive Rate': _sens, 'False Positive Rate': _spec})
    current_stats = pd.DataFrame([[cutoff, _sens, 1 - _spec]], columns=['Cutoff', 'True Positive Rate', 'False Positive Rate'])
    current_dot = alt.Chart(current_stats).mark_point(color='red', size=100).encode(
        y=alt.Y('True Positive Rate:Q'),
        x=alt.X('False Positive Rate:Q'),
        tooltip=['Cutoff', 'True Positive Rate', 'False Positive Rate']
    )
    current_roc = roc + current_dot
    current_roc
    return


@app.cell
def _():
    # current_roc | final_heatmap
    # final_heatmap & current_roc
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Questions

    1. What cutoff value should we choose? Is there a "best" value? Could it depend on the use case?

    2. Why can't we just get it right? Is there anything we can do statistically to make the test more accurate? What is blocking the test from being more accurate?
    """)
    return


@app.cell(disabled=True)
def _(alt, df):
    # Scatter plot and PDF on same plot
    both_dens = alt.Chart(df).transform_density(
        'Value',
        groupby=['Condition'],
        as_=['Value', 'Density'],
    ).mark_area(opacity=0.5).encode(
        x=alt.X('Value:Q'),
        y=alt.Y('Density:Q'),
        color='Condition:N'
    )
    _df = df.copy()
    #_df = _df['Asdf'] = 1
    my_scatter = alt.Chart(_df).mark_point().encode(
        # x='Value:Q',
        # y=alt.Y('Asdf:Q'),
        x=alt.X('Value:Q'),
        yOffset="jitter:Q",
        color='Condition:N'
    ).properties(
        title='Scatter Plot of Values',
        # width=600,
        height=50
    ).transform_calculate(
        # Generate Gaussian jitter with a Box-Muller transform
        jitter="sqrt(-2*log(random()))*cos(2*PI*random())"
    )
    # both_dens = both_dens + my_scatter
    # both_dens
    # my_scatter
    return


@app.cell(disabled=True)
def _(alt, df):
    density_points_plot = alt.Chart(df).transform_density(
        'Value',
        as_=['Value', 'Density'],
        groupby=['Condition']
    ).mark_point().encode(
        x='Value:Q',
        y='Density:Q',
        color='Condition:N'
    ) + alt.Chart(df).mark_point(filled=True, opacity=0.5).encode(
        x='Value:Q',
        y='Density:Q',
        color='Condition:N'
    ).properties(
        title='Density and Points Plot of Values',
        width=600,
        height=400
    )

    # density_points_plot
    return


@app.cell(disabled=True)
def _(cutoff, display, healthy_data, np, pd, plt, sick_data):
    import seaborn as sns
    import ipywidgets as widgets
    from sklearn.metrics import roc_curve

    # Initialize parameters
    num_sick = 100
    mean_sick = 0
    std_sick = 1
    num_healthy = 100
    mean_healthy = 3
    std_healthy = 1
    poo_cutoff = 1.5

    # Generate data
    _sick_data = np.random.normal(loc=mean_sick, scale=std_sick, size=num_sick)
    _healthy_data = np.random.normal(loc=mean_healthy, scale=std_healthy, size=num_healthy)

    def update_plot(num_sick, mean_sick, std_sick, num_healthy, mean_healthy, std_healthy, cutoff):
        plt.figure(figsize=(12, 6))

        # Density plot
        sns.kdeplot(sick_data, color='red', label='Sick', fill=True)
        sns.kdeplot(healthy_data, color='blue', label='Healthy', fill=True)

        # Show points
        plt.scatter(sick_data, np.zeros_like(sick_data), color='red', alpha=0.5)
        plt.scatter(healthy_data, np.zeros_like(healthy_data), color='blue', alpha=0.5)

        # Cutoff line
        plt.axvline(x=cutoff, color='black', linestyle='--', label='Cutoff')

        plt.title('Density Plot of Sick and Healthy Populations')
        plt.xlabel('Biomarker Level')
        plt.ylabel('Density')
        plt.legend()
        plt.grid()
        plt.gca()

    # Sensitivity and specificity calculation
    def calculate_metrics(cutoff):
        tp = np.sum(sick_data > cutoff)
        fn = np.sum(sick_data <= cutoff)
        tn = np.sum(healthy_data <= cutoff)
        fp = np.sum(healthy_data > cutoff)

        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

        return sensitivity, specificity

    # Create sliders
    num_sick_slider = widgets.IntSlider(value=num_sick, min=1, max=500, description='Sick Count')
    mean_sick_slider = widgets.FloatSlider(value=mean_sick, min=-5, max=5, description='Sick Mean')
    std_sick_slider = widgets.FloatSlider(value=std_sick, min=0.1, max=5, description='Sick Std Dev')

    num_healthy_slider = widgets.IntSlider(value=num_healthy, min=1, max=500, description='Healthy Count')
    mean_healthy_slider = widgets.FloatSlider(value=mean_healthy, min=-5, max=5, description='Healthy Mean')
    std_healthy_slider = widgets.FloatSlider(value=std_healthy, min=0.1, max=5, description='Healthy Std Dev')

    poo_cutoff_slider = widgets.FloatSlider(value=cutoff, min=-5, max=5, step=0.1, description='Cutoff')

    def update_table(cutoff):
        sensitivity, specificity = calculate_metrics(cutoff)
        metrics_table = pd.DataFrame({
            'Metric': ['Sensitivity', 'Specificity'],
            'Value': [sensitivity, specificity]
        })
        return metrics_table

    def update_roc(cutoff):
        y_true = [1] * num_sick + [0] * num_healthy
        y_scores = np.concatenate([sick_data, healthy_data])
        fpr, tpr, thresholds = roc_curve(y_true, y_scores)

        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', label='ROC Curve')
        plt.scatter(fpr[np.abs(thresholds - cutoff).argmin()], tpr[np.abs(thresholds - cutoff).argmin()], color='red', label='Current Point')
        plt.title('ROC Curve')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.axhline(0.5, color='black', linestyle='--')
        plt.axvline(0.5, color='black', linestyle='--')
        plt.legend()
        plt.grid()
        plt.gca()

    # Output display
    def update_all(*args):
        update_plot(num_sick_slider.value, mean_sick_slider.value, std_sick_slider.value,
                     num_healthy_slider.value, mean_healthy_slider.value, std_healthy_slider.value,
                     poo_cutoff_slider.value)

        metrics = update_table(poo_cutoff_slider.value)
        display(metrics)

        update_roc(poo_cutoff_slider.value)

    # Attach update function to sliders
    num_sick_slider.observe(update_all, 'value')
    mean_sick_slider.observe(update_all, 'value')
    std_sick_slider.observe(update_all, 'value')
    num_healthy_slider.observe(update_all, 'value')
    mean_healthy_slider.observe(update_all, 'value')
    std_healthy_slider.observe(update_all, 'value')
    poo_cutoff_slider.observe(update_all, 'value')

    # Initial plot and table
    update_all()
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
