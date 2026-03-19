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
app = marimo.App(width="medium", app_title="Likelihood Ratios & Fagan's Nomogram")


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
    # Likelihood Ratios & Fagan's Nomogram

    The 2x2 table gives us sensitivity and specificity, but clinicians don't think in those terms at the bedside.
    What we really want to know is: **"Given this test result, how much should I update my belief that the patient has the disease?"**

    **Likelihood Ratios (LRs)** answer exactly this question:

    - **LR+** = Sensitivity / (1 − Specificity) — How much more likely is a positive result in someone WITH the disease vs WITHOUT?
    - **LR−** = (1 − Sensitivity) / Specificity — How much more likely is a negative result in someone WITH the disease vs WITHOUT?

    **Fagan's Nomogram** is a visual tool that connects **Pre-test Probability → Likelihood Ratio → Post-test Probability** with a straight line.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Set the **pre-test probability** (your clinical suspicion before the test) and the test's **sensitivity** and **specificity**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    pretest_slider = mo.ui.slider(
        start=1, stop=99, value=25, step=1,
        label="Pre-test Probability (%)", show_value=True
    )
    sens_slider = mo.ui.slider(
        start=1, stop=99, value=90, step=1,
        label="Sensitivity (%)", show_value=True
    )
    spec_slider = mo.ui.slider(
        start=1, stop=99, value=85, step=1,
        label="Specificity (%)", show_value=True
    )
    mo.hstack([pretest_slider, sens_slider, spec_slider])
    return pretest_slider, sens_slider, spec_slider


@app.cell(hide_code=True)
def _(np, pretest_slider, sens_slider, spec_slider):
    # Core calculations
    pretest_prob = pretest_slider.value / 100
    sens = sens_slider.value / 100
    spec = spec_slider.value / 100

    # Likelihood ratios
    lr_pos = sens / (1 - spec)
    lr_neg = (1 - sens) / spec

    # Pre-test odds
    pretest_odds = pretest_prob / (1 - pretest_prob)

    # Post-test odds and probability (positive test)
    posttest_odds_pos = pretest_odds * lr_pos
    posttest_prob_pos = posttest_odds_pos / (1 + posttest_odds_pos)

    # Post-test odds and probability (negative test)
    posttest_odds_neg = pretest_odds * lr_neg
    posttest_prob_neg = posttest_odds_neg / (1 + posttest_odds_neg)

    # For the nomogram: log-odds scale
    log_pretest_odds = np.log10(pretest_odds)
    log_lr_pos = np.log10(lr_pos)
    log_lr_neg = np.log10(lr_neg)
    log_posttest_odds_pos = np.log10(posttest_odds_pos)
    log_posttest_odds_neg = np.log10(posttest_odds_neg) if posttest_odds_neg > 0 else -4
    return (
        log_posttest_odds_neg,
        log_posttest_odds_pos,
        log_pretest_odds,
        lr_neg,
        lr_pos,
        posttest_prob_neg,
        posttest_prob_pos,
        pretest_prob,
        sens,
        spec,
    )


@app.cell(hide_code=True)
def _(lr_neg, lr_pos, mo, posttest_prob_neg, posttest_prob_pos, pretest_prob, sens, spec):
    mo.md(f"""
    ## Results

    | Metric | Value |
    |--------|-------|
    | **Pre-test Probability** | {pretest_prob:.1%} |
    | **Sensitivity** | {sens:.0%} |
    | **Specificity** | {spec:.0%} |
    | **LR+** | **{lr_pos:.2f}** |
    | **LR−** | **{lr_neg:.3f}** |
    | **Post-test Probability (Test +)** | **{posttest_prob_pos:.1%}** |
    | **Post-test Probability (Test −)** | **{posttest_prob_neg:.1%}** |

    **Interpretation:**
    - Starting with a {pretest_prob:.0%} suspicion, a **positive** test raises it to **{posttest_prob_pos:.1%}**.
    - A **negative** test lowers it to **{posttest_prob_neg:.1%}**.

    **LR rules of thumb:**
    - LR > 10 → large increase in probability (strong rule-in)
    - LR 5–10 → moderate increase
    - LR 2–5 → small increase
    - LR 0.1–0.2 → moderate decrease (useful rule-out)
    - LR < 0.1 → large decrease (strong rule-out)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Fagan's Nomogram

    Draw a straight line from the **Pre-test Probability** (left axis) through the **Likelihood Ratio** (middle axis)
    to read the **Post-test Probability** (right axis).

    The green line shows a **positive** test result (using LR+).
    The red line shows a **negative** test result (using LR−).
    """)
    return


@app.cell(hide_code=True)
def _(
    alt,
    lr_neg,
    lr_pos,
    mo,
    np,
    pd,
    posttest_prob_neg,
    posttest_prob_pos,
    pretest_prob,
):
    # Build a simplified nomogram visualization
    # Three vertical axes: pre-test prob, LR, post-test prob
    # We'll use scaled positions for visual clarity

    # Probability-to-position mapping (logit scale for even spacing)
    def prob_to_y(p):
        p = np.clip(p, 0.001, 0.999)
        return np.log10(p / (1 - p))

    def lr_to_y(lr):
        return np.log10(lr)

    # Axis tick marks for pre-test and post-test probability
    prob_ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
    prob_labels_df = pd.DataFrame({
        'x': [0.0] * len(prob_ticks),
        'y': [prob_to_y(p) for p in prob_ticks],
        'label': [f"{int(p*100)}%" for p in prob_ticks]
    })

    post_labels_df = pd.DataFrame({
        'x': [2.0] * len(prob_ticks),
        'y': [prob_to_y(p) for p in prob_ticks],
        'label': [f"{int(p*100)}%" for p in prob_ticks]
    })

    # LR axis ticks
    lr_ticks = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
    lr_labels_df = pd.DataFrame({
        'x': [1.0] * len(lr_ticks),
        'y': [lr_to_y(lr) for lr in lr_ticks],
        'label': [str(lr) for lr in lr_ticks]
    })

    # Axis lines
    axis_data = pd.DataFrame({
        'x': [0, 0, 1, 1, 2, 2],
        'y': [-2.5, 2.5, -2.5, 2.5, -2.5, 2.5],
        'axis': ['Pre-test', 'Pre-test', 'LR', 'LR', 'Post-test', 'Post-test']
    })

    axis_lines = alt.Chart(axis_data).mark_line(color='black', strokeWidth=2).encode(
        x=alt.X('x:Q', axis=None, scale=alt.Scale(domain=[-0.5, 2.5])),
        y=alt.Y('y:Q', axis=None, scale=alt.Scale(domain=[-2.8, 2.8])),
        detail='axis:N'
    )

    # Tick labels
    pre_ticks = alt.Chart(prob_labels_df).mark_text(align='right', dx=-8, fontSize=10).encode(
        x='x:Q', y='y:Q', text='label:N'
    )
    post_ticks = alt.Chart(post_labels_df).mark_text(align='left', dx=8, fontSize=10).encode(
        x='x:Q', y='y:Q', text='label:N'
    )
    lr_tick_marks = alt.Chart(lr_labels_df).mark_text(fontSize=10).encode(
        x='x:Q', y='y:Q', text='label:N'
    )

    # Axis titles
    titles_df = pd.DataFrame({
        'x': [0, 1, 2],
        'y': [2.7, 2.7, 2.7],
        'label': ['Pre-test\nProbability', 'Likelihood\nRatio', 'Post-test\nProbability']
    })
    titles = alt.Chart(titles_df).mark_text(fontSize=12, fontWeight='bold').encode(
        x='x:Q', y='y:Q', text='label:N'
    )

    # Nomogram lines (LR+ in green, LR- in red)
    pre_y = prob_to_y(pretest_prob)
    lr_pos_y = lr_to_y(lr_pos)
    lr_neg_y = lr_to_y(lr_neg)
    post_pos_y = prob_to_y(posttest_prob_pos)
    post_neg_y = prob_to_y(posttest_prob_neg)

    pos_line_df = pd.DataFrame({
        'x': [0, 1, 2],
        'y': [pre_y, lr_pos_y, post_pos_y],
        'test': ['LR+ (Positive Test)'] * 3
    })
    neg_line_df = pd.DataFrame({
        'x': [0, 1, 2],
        'y': [pre_y, lr_neg_y, post_neg_y],
        'test': ['LR− (Negative Test)'] * 3
    })

    pos_line = alt.Chart(pos_line_df).mark_line(
        strokeWidth=2.5, color='#2ca02c', strokeDash=[1, 0]
    ).encode(x='x:Q', y='y:Q')

    neg_line = alt.Chart(neg_line_df).mark_line(
        strokeWidth=2.5, color='#d62728', strokeDash=[6, 3]
    ).encode(x='x:Q', y='y:Q')

    # Points on the lines
    points_df = pd.DataFrame({
        'x': [0, 1, 2, 0, 1, 2],
        'y': [pre_y, lr_pos_y, post_pos_y, pre_y, lr_neg_y, post_neg_y],
        'test': ['Positive'] * 3 + ['Negative'] * 3,
        'label': [
            f"Pre: {pretest_prob:.0%}", f"LR+: {lr_pos:.1f}", f"Post: {posttest_prob_pos:.1%}",
            f"Pre: {pretest_prob:.0%}", f"LR−: {lr_neg:.2f}", f"Post: {posttest_prob_neg:.1%}"
        ]
    })

    points = alt.Chart(points_df).mark_circle(size=80).encode(
        x='x:Q', y='y:Q',
        color=alt.Color('test:N', scale=alt.Scale(
            domain=['Positive', 'Negative'],
            range=['#2ca02c', '#d62728']
        )),
        tooltip=['label:N']
    )

    nomogram = (axis_lines + pre_ticks + post_ticks + lr_tick_marks + titles
                + pos_line + neg_line + points)
    nomogram = nomogram.properties(
        width=500, height=500,
        title='Fagan\'s Nomogram'
    ).configure_view(strokeWidth=0)

    _summary_df = pd.DataFrame({
        'Metric': ['Pre-test Probability', 'LR+', 'LR-', 'Post-test Prob (Test +)', 'Post-test Prob (Test -)'],
        'Value': [f'{pretest_prob:.1%}', f'{lr_pos:.2f}', f'{lr_neg:.3f}', f'{posttest_prob_pos:.1%}', f'{posttest_prob_neg:.1%}']
    })
    mo.vstack([
        nomogram,
        mo.accordion({"View data table": mo.ui.table(_summary_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">Fagan\'s nomogram showing pre-test probability {pretest_prob:.0%} with LR+ {lr_pos:.1f} yielding post-test probability {posttest_prob_pos:.1%} (positive test) and LR- {lr_neg:.2f} yielding {posttest_prob_neg:.1%} (negative test).</div>')
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Post-test Probability Across Pre-test Probabilities

    This chart shows how a single test (with your chosen sensitivity/specificity) transforms
    any pre-test probability into a post-test probability.
    """)
    return


@app.cell(hide_code=True)
def _(alt, mo, np, pd, sens, spec):
    # Sweep pre-test probability
    _lr_pos = sens / (1 - spec)
    _lr_neg = (1 - sens) / spec

    pre_range = np.arange(1, 100, 1)
    sweep_data = []
    for _pre_pct in pre_range:
        _pre = _pre_pct / 100
        _pre_odds = _pre / (1 - _pre)
        _post_pos = (_pre_odds * _lr_pos) / (1 + _pre_odds * _lr_pos)
        _post_neg = (_pre_odds * _lr_neg) / (1 + _pre_odds * _lr_neg)
        sweep_data.append({
            'Pre-test Probability (%)': int(_pre_pct),
            'After Positive Test': _post_pos,
            'After Negative Test': _post_neg
        })
    sweep_df = pd.DataFrame(sweep_data)

    sweep_long = sweep_df.melt(
        id_vars=['Pre-test Probability (%)'],
        value_vars=['After Positive Test', 'After Negative Test'],
        var_name='Result', value_name='Post-test Probability'
    )

    # Reference line (no change)
    ref_df = pd.DataFrame({
        'Pre-test Probability (%)': list(range(1, 100)),
        'Post-test Probability': [p / 100 for p in range(1, 100)],
        'Result': ['No Test (reference)'] * 99
    })
    sweep_long = pd.concat([sweep_long, ref_df], ignore_index=True)

    sweep_chart = alt.Chart(sweep_long).mark_line(strokeWidth=2).encode(
        x=alt.X('Pre-test Probability (%):Q'),
        y=alt.Y('Post-test Probability:Q', title='Post-test Probability', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Result:N', scale=alt.Scale(
            domain=['After Positive Test', 'After Negative Test', 'No Test (reference)'],
            range=['#2ca02c', '#d62728', '#888888']
        )),
        strokeDash=alt.StrokeDash('Result:N', scale=alt.Scale(
            domain=['After Positive Test', 'After Negative Test', 'No Test (reference)'],
            range=[[1, 0], [1, 0], [5, 3]]
        )),
        tooltip=[
            alt.Tooltip('Pre-test Probability (%):Q'),
            alt.Tooltip('Result:N'),
            alt.Tooltip('Post-test Probability:Q', format='.1%')
        ]
    ).properties(
        width=700, height=350,
        title=f'How This Test Updates Probability (Sens={sens:.0%}, Spec={spec:.0%})'
    )

    mo.vstack([
        sweep_chart,
        mo.accordion({"View data table": mo.ui.table(sweep_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">Post-test probability sweep across all pre-test probabilities for a test with sensitivity {sens:.0%} and specificity {spec:.0%}. Shows how positive and negative results shift probability.</div>')
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    # Verified: PMID 16234501, DOI 10.1001/jama.294.15.1944
    mo.md(r"""
    ## Anchor Paper: The Rational Clinical Examination (JAMA Series)

    **Wang CS, FitzGerald JM, Schulzer M, Mak E, Ayas NT.** "Does this dyspneic patient in the
    emergency department have congestive heart failure?" *JAMA.* 2005;294(15):1944-56.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/16234501/) |
    [DOI: 10.1001/jama.294.15.1944](https://doi.org/10.1001/jama.294.15.1944)

    This JAMA **Rational Clinical Examination** article reviews the diagnostic accuracy of bedside
    findings for heart failure, reporting **likelihood ratios** for each:

    - **S3 gallop:** LR+ = 11 (95% CI: 4.9–25.0) — very strong rule-in
    - **Pulmonary venous congestion on CXR:** LR+ = 12.0 (95% CI: 6.8–21.0)
    - **History of heart failure:** LR+ = 5.8 (95% CI: 4.1–8.0)
    - **Paroxysmal nocturnal dyspnea:** LR+ = 2.6 (95% CI: 1.5–4.5) — modest

    **Try it:** Set pre-test probability to 30% (dyspneic patient), sensitivity to 50%, specificity to 95%.
    See how LR+ ≈ 10 shifts the post-test probability dramatically upward, while LR− ≈ 0.5 barely moves it down.

    **Board-relevant concept:** Likelihood ratios let you quantify the *clinical impact* of a finding,
    not just whether it's "positive" or "negative." This is why LRs are more clinically useful than
    sensitivity/specificity alone.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | Formula | Interpretation |
    |---------|---------|----------------|
    | **LR+** | Sens / (1 − Spec) | How many times more likely is a positive result in disease? |
    | **LR−** | (1 − Sens) / Spec | How many times more likely is a negative result in disease? |
    | **Pre-test odds** | P / (1 − P) | Convert probability to odds |
    | **Post-test odds** | Pre-test odds × LR | Bayes' theorem in odds form |
    | **Post-test prob** | Odds / (1 + Odds) | Convert back to probability |

    **The power of LRs:** They are *test-specific* and *prevalence-independent*. You can apply them
    to any patient by starting with YOUR pre-test probability for THAT patient.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Questions

    1. A test has sensitivity 95% and specificity 50%. Calculate LR+ and LR−. Is this a good rule-in test, rule-out test, or both?

    2. Your pre-test probability for PE is 40%. The D-dimer is negative (LR− ≈ 0.10). What is the post-test probability? Would you stop the workup?

    3. What happens to post-test probability when LR = 1? What does this test tell you?

    4. Why are likelihood ratios more useful than sensitivity/specificity for bedside clinical decision-making?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Wang et al. JAMA 2005 — no PMC PDF available
    # Verified: PMID 16234501, DOI 10.1001/jama.294.15.1944
    mo.accordion(
        {
            "Read the Anchor Paper: Rational Clinical Examination — CHF (2005)": mo.md("""
**Wang CS, FitzGerald JM, Schulzer M, Mak E, Ayas NT.** "Does this dyspneic patient in the
emergency department have congestive heart failure?" *JAMA.* 2005;294(15):1944-56.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/16234501/) |
[Open on JAMA (may require institutional access)](https://doi.org/10.1001/jama.294.15.1944)

*If you are on a UF network or VPN, the JAMA link should provide full-text access.*
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
