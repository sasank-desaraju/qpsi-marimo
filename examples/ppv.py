# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.13.15",
#     "altair==4.2.0",
#     "pandas==2.3.0",
#     "numpy==2.3.0",
#     "matplotlib>=3.0.0",
# ]
# ///

import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium", app_title="PPV and Prevalence")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    return mo, plt


@app.cell
def _(mo):
    mo.md(r"""
    # Understanding Positive Predictive Value (PPV) and Negative Predictive Value (NPV)

    In **medical testing**, the Positive Predictive Value (PPV) and Negative Predictive Value (NPV) are important metrics that help us understand the effectiveness of a test.

    - **PPV** is the probability that subjects with a positive screening test truly have the disease.
    - **NPV** is the probability that subjects with a negative screening test truly do not have the disease.

    These values depend on the prevalence of the disease in the population and the sensitivity and specificity of the test.

    In this notebook, we will explore how to calculate PPV and NPV using interactive visualizations.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Setting Sensitivity, Specificity, and Prevalence

    Let's create sliders to adjust the sensitivity, specificity, and prevalence of a disease in a population.
    """)
    return


@app.cell
def _(mo):
    # Create sliders for sensitivity, specificity, and prevalence
    sensitivity_slider = mo.ui.slider(0, 100, value=90, label="Sensitivity (%)")
    specificity_slider = mo.ui.slider(0, 100, value=90, label="Specificity (%)")
    prevalence_slider = mo.ui.slider(0, 100, value=10, label="Prevalence (%)")

    mo.hstack([sensitivity_slider, specificity_slider, prevalence_slider])
    return prevalence_slider, sensitivity_slider, specificity_slider


@app.cell
def _(mo):
    mo.md(r"""
    ## PPV and NPV formulae

    Now, let's write out our formulae for calculating PPV and NPV.

    $$PPV = \frac{TP}{TP + FP} = \frac{Sensitivity \times Prevalence}{Sensitivity \times Prevalence + (1 - Specificity) \times (1 - Prevalence)}$$

    $$NPV = \frac{TN}{TN + FN} = \frac{Specificity \times (1 - Prevalence)}{(1 - Sensitivity) \times Prevalence + Specificity \times (1 - Prevalence)}$$


    Do these make sense? Let's take a moment to think about them...
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Code for calculating PPV and NPV
    """)
    return


@app.cell
def _(mo, prevalence_slider, sensitivity_slider, specificity_slider):
    # Calculate PPV and NPV based on slider values
    sensitivity = sensitivity_slider.value / 100
    specificity = specificity_slider.value / 100
    prevalence = prevalence_slider.value / 100

    # Calculate PPV and NPV
    ppv = (sensitivity * prevalence) / ((sensitivity * prevalence) + ((1 - specificity) * (1 - prevalence)))
    npv = (specificity * (1 - prevalence)) / (((1 - sensitivity) * prevalence) + (specificity * (1 - prevalence)))

    ppv, npv

    mo.show_code()
    return npv, ppv


@app.cell
def _(npv, plt, ppv):
    # Visualize PPV and NPV
    labels = ['PPV', 'NPV']
    values = [ppv, npv]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, values, color=['#1f77b4', '#ff7f0e'])
    plt.ylim(0, 1)
    plt.title('Positive Predictive Value (PPV) and Negative Predictive Value (NPV)')
    plt.ylabel('Probability')
    plt.gca()
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
