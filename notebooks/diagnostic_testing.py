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
app = marimo.App(width="medium", app_title="Diagnostic Testing: The 2x2 Matrix & Prevalence")


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
    # Diagnostic Testing: The 2x2 Matrix & Prevalence

    When we order a diagnostic test, we want to know: **"If this test is positive, does my patient actually have the disease?"**

    The answer depends on more than just the test's accuracy — it depends critically on **how common the disease is** in the population you're testing.

    This notebook uses an interactive population of **1,000 people** to make this tangible.
    You control the test characteristics and disease prevalence, and watch how the 2x2 matrix
    and predictive values change in real time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Set Test Characteristics and Prevalence

    - **Sensitivity** = P(Test+ | Disease+) — How good is the test at catching sick people?
    - **Specificity** = P(Test− | Disease−) — How good is the test at correctly clearing healthy people?
    - **Prevalence** = What fraction of the population actually has the disease?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    sensitivity_slider = mo.ui.slider(
        start=0, stop=100, value=95, step=1,
        label="Sensitivity (%)", show_value=True
    )
    specificity_slider = mo.ui.slider(
        start=0, stop=100, value=90, step=1,
        label="Specificity (%)", show_value=True
    )
    prevalence_slider = mo.ui.slider(
        start=1, stop=50, value=10, step=1,
        label="Prevalence (%)", show_value=True
    )
    mo.hstack([sensitivity_slider, specificity_slider, prevalence_slider])
    return prevalence_slider, sensitivity_slider, specificity_slider


@app.cell(hide_code=True)
def _(np, prevalence_slider, sensitivity_slider, specificity_slider):
    # Core calculations on a population of 1000
    population = 1000
    sens = sensitivity_slider.value / 100
    spec = specificity_slider.value / 100
    prev = prevalence_slider.value / 100

    # True disease status
    n_sick = int(round(population * prev))
    n_healthy = population - n_sick

    # Test results
    tp = int(round(n_sick * sens))           # True positives
    fn = n_sick - tp                          # False negatives
    tn = int(round(n_healthy * spec))         # True negatives
    fp = n_healthy - tn                       # False positives

    # Predictive values
    ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0

    # For the dot grid, assign each of the 1000 people
    np.random.seed(42)
    statuses = []
    # Sick people
    for i in range(n_sick):
        if i < tp:
            statuses.append('True Positive')
        else:
            statuses.append('False Negative')
    # Healthy people
    for i in range(n_healthy):
        if i < fp:
            statuses.append('False Positive')
        else:
            statuses.append('True Negative')

    # Shuffle for visual effect
    order = np.random.permutation(population)
    statuses_shuffled = [statuses[i] for i in order]
    return fn, fp, n_healthy, n_sick, npv, order, population, ppv, statuses_shuffled, tn, tp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The 1,000-Person Population

    Each dot below represents one person out of 1,000. The grid shows the **truth** after we apply the test:

    - **Green** = True Positive (sick, correctly detected)
    - **Red** = False Positive (healthy, but test says sick)
    - **Blue** = True Negative (healthy, correctly cleared)
    - **Gray** = False Negative (sick, but test missed them)

    Watch how the ratio of red (false positive) to green (true positive) dots changes as you lower the prevalence.
    When disease is rare, **false positives dominate** the positives.
    """)
    return


@app.cell(hide_code=True)
def _(alt, pd, population, statuses_shuffled):
    # Build the dot grid (25 columns x 40 rows = 1000 dots)
    cols = 25
    rows = population // cols
    dot_data = pd.DataFrame({
        'col': [i % cols for i in range(population)],
        'row': [i // cols for i in range(population)],
        'status': statuses_shuffled
    })

    color_map = {
        'True Positive': '#2ca02c',   # green
        'False Positive': '#d62728',   # red
        'True Negative': '#1f77b4',    # blue
        'False Negative': '#7f7f7f'    # gray
    }

    dot_chart = alt.Chart(dot_data).mark_circle(size=60).encode(
        x=alt.X('col:O', axis=None),
        y=alt.Y('row:O', axis=None, sort='descending'),
        color=alt.Color('status:N', scale=alt.Scale(
            domain=list(color_map.keys()),
            range=list(color_map.values())
        ), legend=alt.Legend(title='Result')),
        tooltip=['status:N']
    ).properties(
        width=500,
        height=350,
        title='Population of 1,000 People'
    ).configure_view(strokeWidth=0)

    dot_chart
    return


@app.cell(hide_code=True)
def _(fn, fp, mo, n_healthy, n_sick, npv, population, ppv, tn, tp):
    mo.md(f"""
    ## The 2x2 Table

    Out of **{population}** people, **{n_sick}** have the disease and **{n_healthy}** are healthy.

    |  | **Disease +** | **Disease −** | **Total** |
    |--|:---:|:---:|:---:|
    | **Test +** | {tp} (TP) | {fp} (FP) | {tp + fp} |
    | **Test −** | {fn} (FN) | {tn} (TN) | {fn + tn} |
    | **Total** | {n_sick} | {n_healthy} | {population} |

    ## Predictive Values

    | Metric | Formula | Value |
    |--------|---------|-------|
    | **PPV** (Positive Predictive Value) | TP / (TP + FP) = {tp} / ({tp} + {fp}) | **{ppv:.1%}** |
    | **NPV** (Negative Predictive Value) | TN / (TN + FN) = {tn} / ({tn} + {fn}) | **{npv:.1%}** |

    **PPV answers:** "If the test is positive, what's the chance my patient is actually sick?"
    With current settings, a positive test means there's only a **{ppv:.1%}** chance the patient truly has the disease.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How PPV Changes with Prevalence

    This is the most important graph in diagnostic testing.
    Even with excellent sensitivity and specificity, **PPV plummets when prevalence is low**.

    This is why we don't screen the general population for rare diseases — the false positives would overwhelm the true positives.
    """)
    return


@app.cell(hide_code=True)
def _(alt, np, pd, sensitivity_slider, specificity_slider):
    # PPV and NPV as a function of prevalence
    _sens = sensitivity_slider.value / 100
    _spec = specificity_slider.value / 100

    prev_range = np.arange(1, 51, 1)
    pv_data = []
    for _p_pct in prev_range:
        _p = _p_pct / 100
        _ppv = (_sens * _p) / (_sens * _p + (1 - _spec) * (1 - _p))
        _npv = (_spec * (1 - _p)) / ((1 - _sens) * _p + _spec * (1 - _p))
        pv_data.append({'Prevalence (%)': int(_p_pct), 'PPV': _ppv, 'NPV': _npv})
    pv_df = pd.DataFrame(pv_data)

    # Melt for Altair
    pv_long = pv_df.melt(
        id_vars=['Prevalence (%)'],
        value_vars=['PPV', 'NPV'],
        var_name='Metric',
        value_name='Value'
    )

    pv_chart = alt.Chart(pv_long).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Prevalence (%):Q', title='Disease Prevalence (%)'),
        y=alt.Y('Value:Q', title='Predictive Value', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Metric:N', scale=alt.Scale(
            domain=['PPV', 'NPV'],
            range=['#2ca02c', '#1f77b4']
        )),
        tooltip=[
            alt.Tooltip('Prevalence (%):Q'),
            alt.Tooltip('Metric:N'),
            alt.Tooltip('Value:Q', format='.1%')
        ]
    ).properties(
        width=700,
        height=350,
        title=f'PPV and NPV vs Prevalence (Sens={_sens:.0%}, Spec={_spec:.0%})'
    )

    pv_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Confusion Matrix Visualized

    Another way to see the 2x2 table — as a heatmap. The intensity shows the count in each cell.
    """)
    return


@app.cell(hide_code=True)
def _(alt, fn, fp, pd, tn, tp):
    # Confusion matrix heatmap
    conf_data = pd.DataFrame({
        'True Condition': ['Disease +', 'Disease +', 'Disease −', 'Disease −'],
        'Test Result': ['Test +', 'Test −', 'Test +', 'Test −'],
        'Count': [tp, fn, fp, tn],
        'Label': [f'TP = {tp}', f'FN = {fn}', f'FP = {fp}', f'TN = {tn}']
    })

    heatmap = alt.Chart(conf_data).mark_rect(cornerRadius=4).encode(
        x=alt.X('Test Result:O', title='Test Result'),
        y=alt.Y('True Condition:O', title='True Condition', sort=['Disease +', 'Disease −']),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='blues'), legend=None),
        tooltip=['True Condition:N', 'Test Result:N', 'Count:Q']
    ).properties(
        width=300,
        height=250,
        title='Confusion Matrix'
    )

    text = alt.Chart(conf_data).mark_text(
        fontSize=16, fontWeight='bold'
    ).encode(
        x='Test Result:O',
        y=alt.Y('True Condition:O', sort=['Disease +', 'Disease −']),
        text='Label:N',
        color=alt.condition(
            alt.datum.Count > 300,
            alt.value('white'),
            alt.value('black')
        )
    )

    conf_chart = heatmap + text
    conf_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Anchor Paper: PIOPED II — CT Pulmonary Angiography for PE

    **Stein PD, Fowler SE, Goodman LR, et al.** "Multidetector computed tomography for acute
    pulmonary embolism." *N Engl J Med.* 2006;354(22):2317-27.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/16738268/) |
    [DOI: 10.1056/NEJMoa052367](https://doi.org/10.1056/NEJMoa052367)

    The **PIOPED II** study evaluated CT pulmonary angiography for diagnosing PE, but D-dimer
    is the classic screening example:

    - **D-dimer sensitivity:** ~95-97% (very good at catching PE)
    - **D-dimer specificity:** ~40-50% (many things elevate D-dimer — surgery, infection, cancer, pregnancy)

    **The clinical lesson:** In the ED, PE prevalence among patients being worked up is maybe 10-20%.
    Even with 95% sensitivity, the **low specificity** means most positive D-dimers are false positives.

    **Try it yourself:** Set sensitivity to 95%, specificity to 45%, prevalence to 15%.
    Notice that the PPV is only about 24% — three out of four positive D-dimers are **not** PE!

    This is why a positive D-dimer doesn't diagnose PE. It just means "you can't rule it out yet"
    and you need further imaging (CTA). A **negative** D-dimer, however, has excellent NPV because
    of the high sensitivity — if it's negative, you're very unlikely to have PE.

    **Board-relevant concept:** Sensitivity and specificity are **intrinsic** to the test.
    PPV and NPV are **extrinsic** — they change with prevalence!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | Definition | Depends on Prevalence? |
    |---------|------------|:----------------------:|
    | **Sensitivity** | P(Test+ \| Disease+) — "catch rate" | No (intrinsic) |
    | **Specificity** | P(Test− \| Disease−) — "clear rate" | No (intrinsic) |
    | **PPV** | P(Disease+ \| Test+) — "positive means sick?" | **Yes** (extrinsic) |
    | **NPV** | P(Disease− \| Test−) — "negative means healthy?" | **Yes** (extrinsic) |

    **Clinical mnemonic:**
    - **Sn**-N-**Out**: A highly **Sensitive** test, when **Negative**, rules disease **Out** (high NPV)
    - **Sp**-P-**In**: A highly **Specific** test, when **Positive**, rules disease **In** (high PPV)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Questions

    1. Set prevalence to 1% with sensitivity 95% and specificity 90%. What is the PPV? Would you screen the general population for this disease?

    2. Now increase prevalence to 40% (a high-risk population). How does PPV change? How does this inform targeted screening?

    3. Keep prevalence at 10%. Try increasing specificity from 80% to 99%. How much does PPV improve? Compare this to increasing sensitivity from 80% to 99%.

    4. Why is the D-dimer most useful as a "rule-out" test rather than a "rule-in" test? Which metric (PPV or NPV) explains this?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # PIOPED II — NEJM paywalled; link to PubMed
    # Verified: PMID 16738268, DOI 10.1056/NEJMoa052367
    mo.accordion(
        {
            "Read the Anchor Paper: PIOPED II (2006)": mo.md("""
**Stein PD, et al.** "Multidetector computed tomography for acute pulmonary embolism."
*N Engl J Med.* 2006;354(22):2317-27.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/16738268/) |
[Open on NEJM (may require institutional access)](https://doi.org/10.1056/NEJMoa052367)

*If you are on a UF network or VPN, the NEJM link should provide full-text access.*
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
