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
app = marimo.App(width="medium", app_title="Measures of Association: OR vs RR vs NNT")


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
    # Measures of Association: OR vs. RR vs. NNT

    When a treatment works, there are many ways to express *how much* it works.
    These measures can tell very different stories about the same data:

    - **Relative Risk (RR):** Risk in treatment / Risk in control — "By what *factor* does treatment change risk?"
    - **Odds Ratio (OR):** Odds in treatment / Odds in control — Approximates RR when events are rare
    - **Absolute Risk Reduction (ARR):** Risk in control − Risk in treatment — "How many *fewer* events per patient?"
    - **Number Needed to Treat (NNT):** 1 / ARR — "How many patients must I treat to prevent one event?"

    **The key insight:** RR can stay constant while NNT changes dramatically depending on baseline risk.
    This is why drug ads love to report relative risk reduction — it always sounds impressive!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Set the **baseline event risk** (control group) and the **relative risk reduction** from treatment.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    baseline_risk_slider = mo.ui.slider(
        start=1, stop=80, value=30, step=1,
        label="Baseline Event Risk (%)", show_value=True
    )
    rrr_slider = mo.ui.slider(
        start=5, stop=80, value=30, step=1,
        label="Relative Risk Reduction (%)", show_value=True
    )
    mo.hstack([baseline_risk_slider, rrr_slider])
    return baseline_risk_slider, rrr_slider


@app.cell(hide_code=True)
def _(baseline_risk_slider, np, rrr_slider):
    # Core calculations
    baseline_risk = baseline_risk_slider.value / 100
    rrr = rrr_slider.value / 100

    treatment_risk = baseline_risk * (1 - rrr)
    rr = treatment_risk / baseline_risk  # = 1 - RRR
    arr = baseline_risk - treatment_risk
    nnt = 1 / arr if arr > 0 else float('inf')

    # Odds
    baseline_odds = baseline_risk / (1 - baseline_risk)
    treatment_odds = treatment_risk / (1 - treatment_risk)
    odds_ratio = treatment_odds / baseline_odds
    return arr, baseline_risk, nnt, odds_ratio, rr, rrr, treatment_risk


@app.cell(hide_code=True)
def _(arr, baseline_risk, mo, nnt, odds_ratio, rr, rrr, treatment_risk):
    mo.md(f"""
    ## Current Values

    | Metric | Value | Interpretation |
    |--------|-------|----------------|
    | Baseline Risk (Control) | **{baseline_risk:.1%}** | Event rate without treatment |
    | Treatment Risk | **{treatment_risk:.1%}** | Event rate with treatment |
    | **Relative Risk (RR)** | **{rr:.3f}** | Treatment has {rr:.0%} the risk of control |
    | **Relative Risk Reduction (RRR)** | **{rrr:.1%}** | Treatment reduces *relative* risk by this much |
    | **Absolute Risk Reduction (ARR)** | **{arr:.1%}** | Treatment reduces *absolute* risk by this much |
    | **Number Needed to Treat (NNT)** | **{nnt:.1f}** | Treat this many patients to prevent 1 event |
    | **Odds Ratio (OR)** | **{odds_ratio:.3f}** | Ratio of odds (≈ RR when events are rare) |

    **Notice:** The RRR stays at {rrr:.0%} regardless of baseline risk, but the ARR and NNT change dramatically!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Risk Comparison Bar Chart

    The bars show event rates in each group. The gap between them is the **Absolute Risk Reduction** (ARR).
    As you lower baseline risk, the bars shrink together — same relative reduction, but tiny absolute difference.
    """)
    return


@app.cell(hide_code=True)
def _(alt, arr, baseline_risk, pd, treatment_risk):
    bar_data = pd.DataFrame({
        'Group': ['Control', 'Treatment'],
        'Event Risk (%)': [baseline_risk * 100, treatment_risk * 100]
    })

    bars = alt.Chart(bar_data).mark_bar(width=80).encode(
        x=alt.X('Group:O', title=''),
        y=alt.Y('Event Risk (%):Q', scale=alt.Scale(domain=[0, max(baseline_risk * 100 * 1.2, 5)])),
        color=alt.Color('Group:N', scale=alt.Scale(
            domain=['Control', 'Treatment'],
            range=['#d62728', '#2ca02c']
        )),
        tooltip=['Group:N', alt.Tooltip('Event Risk (%):Q', format='.1f')]
    ).properties(width=300, height=350, title='Event Risk by Group')

    bar_labels = alt.Chart(bar_data).mark_text(
        dy=-10, fontSize=13, fontWeight='bold'
    ).encode(
        x='Group:O',
        y='Event Risk (%):Q',
        text=alt.Text('Event Risk (%):Q', format='.1f')
    )

    # ARR annotation
    arr_df = pd.DataFrame({
        'x': ['Treatment'], 'y': [(baseline_risk + treatment_risk) / 2 * 100],
        'label': [f'ARR = {arr:.1%}']
    })
    arr_label = alt.Chart(arr_df).mark_text(
        dx=80, fontSize=12, color='#333'
    ).encode(x='x:O', y='y:Q', text='label:N')

    risk_chart = bars + bar_labels + arr_label
    risk_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## NNT Explodes at Low Baseline Risk

    This is the most important plot. As baseline risk decreases, the **NNT skyrockets** —
    even though the relative risk reduction is unchanged.

    The red dot marks your current baseline risk.
    """)
    return


@app.cell(hide_code=True)
def _(alt, baseline_risk_slider, np, pd, rrr):
    # NNT vs baseline risk curve
    risk_range = np.arange(1, 81, 1)
    nnt_data = []
    for _r_pct in risk_range:
        _r = _r_pct / 100
        _arr = _r * rrr
        _nnt = 1 / _arr if _arr > 0 else 500
        _nnt = min(_nnt, 500)  # cap for display
        nnt_data.append({
            'Baseline Risk (%)': int(_r_pct),
            'NNT': _nnt
        })
    nnt_df = pd.DataFrame(nnt_data)

    nnt_line = alt.Chart(nnt_df).mark_line(
        color='#1f77b4', strokeWidth=2.5
    ).encode(
        x=alt.X('Baseline Risk (%):Q'),
        y=alt.Y('NNT:Q', title='Number Needed to Treat', scale=alt.Scale(domain=[0, 200])),
        tooltip=[
            alt.Tooltip('Baseline Risk (%):Q'),
            alt.Tooltip('NNT:Q', format='.1f')
        ]
    ).properties(
        width=700, height=350,
        title=f'NNT vs Baseline Risk (RRR = {rrr:.0%} held constant)'
    )

    # Current point
    _current_br = baseline_risk_slider.value
    _current_nnt = 1 / (_current_br / 100 * rrr) if (_current_br / 100 * rrr) > 0 else 500
    current_pt = alt.Chart(pd.DataFrame({
        'Baseline Risk (%)': [_current_br],
        'NNT': [min(_current_nnt, 200)]
    })).mark_point(color='red', size=100, filled=True).encode(
        x='Baseline Risk (%):Q',
        y='NNT:Q',
        tooltip=[alt.Tooltip('NNT:Q', format='.1f')]
    )

    nnt_chart = nnt_line + current_pt
    nnt_chart
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## OR vs RR: When Do They Diverge?

    The **Odds Ratio approximates the Relative Risk** when events are rare (< ~10%).
    As baseline risk increases, the OR diverges from the RR — the OR overestimates the effect.

    This is clinically important: case-control studies can only calculate OR (not RR), so
    interpreting OR as RR in a common disease leads to exaggerated conclusions.
    """)
    return


@app.cell(hide_code=True)
def _(alt, np, pd, rrr):
    # OR vs RR across baseline risks
    risk_range_2 = np.arange(1, 81, 1)
    or_rr_data = []
    for _r_pct in risk_range_2:
        _r = _r_pct / 100
        _tr = _r * (1 - rrr)
        _rr = _tr / _r
        _or = (_tr / (1 - _tr)) / (_r / (1 - _r))
        or_rr_data.append({
            'Baseline Risk (%)': int(_r_pct),
            'RR': _rr,
            'OR': _or
        })
    or_rr_df = pd.DataFrame(or_rr_data)

    or_rr_long = or_rr_df.melt(
        id_vars=['Baseline Risk (%)'],
        value_vars=['RR', 'OR'],
        var_name='Metric', value_name='Value'
    )

    or_rr_chart = alt.Chart(or_rr_long).mark_line(strokeWidth=2.5).encode(
        x=alt.X('Baseline Risk (%):Q'),
        y=alt.Y('Value:Q', title='Ratio Value', scale=alt.Scale(domain=[0, 1.1])),
        color=alt.Color('Metric:N', scale=alt.Scale(
            domain=['RR', 'OR'], range=['#2ca02c', '#ff7f0e']
        )),
        tooltip=[
            alt.Tooltip('Baseline Risk (%):Q'),
            alt.Tooltip('Metric:N'),
            alt.Tooltip('Value:Q', format='.3f')
        ]
    ).properties(
        width=700, height=300,
        title=f'OR vs RR Across Baseline Risks (RRR = {rrr:.0%})'
    )

    # Reference line at 1
    ref = alt.Chart(pd.DataFrame({'y': [1.0]})).mark_rule(
        strokeDash=[5, 3], color='gray'
    ).encode(y='y:Q')

    or_rr_chart + ref
    return


@app.cell(hide_code=True)
def _(mo):
    # Anchor paper: WOSCOPS
    # Verified: PMID 7566020, DOI: 10.1056/NEJM199511163332001
    mo.md(r"""
    ## Anchor Paper: WOSCOPS (1995)

    **Shepherd J, et al.** "Prevention of coronary heart disease with pravastatin in men with
    hypercholesterolemia." *N Engl J Med.* 1995;333(20):1301-7.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/7566020/) |
    [DOI: 10.1056/NEJM199511163332001](https://doi.org/10.1056/NEJM199511163332001)

    **The study:** 6,595 men with elevated cholesterol but no prior MI were randomized to pravastatin
    40 mg vs. placebo. Primary outcome: nonfatal MI or death from coronary heart disease.

    **Key numbers for teaching:**
    - Event rate: 7.9% (placebo) vs. 5.5% (pravastatin) over ~5 years
    - **RRR = 31%** — sounds dramatic! "Pravastatin reduces heart attacks by a third!"
    - **ARR = 2.4%** — more modest
    - **NNT = 42** — must treat 42 men for 5 years to prevent one event

    **Board-relevant concepts:**
    - Drug advertisements and media often report **RRR** because it sounds more impressive
    - Informed consent requires patients understand the **absolute** benefit
    - In primary prevention (low-risk), NNT is inherently high — this doesn't mean the drug "doesn't work,"
      it means you need to treat more people because events are rare
    - Compare with **secondary prevention** (high-risk patients): same drug, same RRR, but much lower NNT
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Measure | Formula | Best Used When |
    |---------|---------|----------------|
    | **RR** | Risk_treatment / Risk_control | Cohort studies, RCTs |
    | **OR** | Odds_treatment / Odds_control | Case-control studies, logistic regression |
    | **RRR** | 1 − RR | Reporting relative benefit |
    | **ARR** | Risk_control − Risk_treatment | Reporting absolute benefit |
    | **NNT** | 1 / ARR | Communicating benefit to patients |
    | **NNH** | 1 / ARI (absolute risk increase) | Communicating harm |

    **Board pearls:**
    - OR ≈ RR when the outcome is **rare** (< 10%)
    - OR **overestimates** RR when the outcome is **common**
    - NNT depends on baseline risk — always ask "NNT in *what population*?"
    - NNT is the reciprocal of ARR: if ARR = 2%, NNT = 50

    ## Questions

    1. A drug reduces MI risk from 10% to 7%. Calculate the RRR, ARR, and NNT.

    2. The same drug (same RRR = 30%) is used in a population with 1% baseline risk. What is the NNT now?

    3. A case-control study reports OR = 2.5 for a disease with 40% prevalence. If you interpret this as RR = 2.5, are you overestimating or underestimating the true RR?

    4. A drug company reports "50% reduction in mortality!" The actual rates were 0.2% vs 0.1%. What is the NNT? Is this clinically impressive?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # WOSCOPS — 1995 NEJM, no PMC PDF
    # Verified: PMID 7566020, DOI 10.1056/NEJM199511163332001
    mo.accordion(
        {
            "Read the Anchor Paper: WOSCOPS (1995)": mo.md("""
**Shepherd J, Cobbe SM, Ford I, et al.** "Prevention of coronary heart disease with pravastatin
in men with hypercholesterolemia." *N Engl J Med.* 1995;333(20):1301-7.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/7566020/) |
[Open on NEJM (may require institutional access)](https://doi.org/10.1056/NEJM199511163332001)

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
