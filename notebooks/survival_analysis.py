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
app = marimo.App(width="medium", app_title="Survival Analysis: Kaplan-Meier & Hazard Ratios")


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
    # Survival Analysis: Kaplan-Meier Curves & Hazard Ratios

    In clinical trials, we often ask: **"How long until the event occurs?"** — where the "event"
    might be death, disease recurrence, or hospitalization.

    **The challenge:** Not everyone reaches the endpoint. Some patients drop out, the study ends,
    or they're lost to follow-up. These are **censored** observations — we know they survived *at least*
    that long, but we don't know the exact event time.

    The **Kaplan-Meier (KM) estimator** handles censoring elegantly. The **Hazard Ratio (HR)** summarizes
    the relative risk of events between two groups over time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Controls

    Simulate two treatment arms. Adjust the hazard rate (event rate per time unit) for each group
    and the amount of censoring.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    n_per_group = mo.ui.slider(
        start=20, stop=200, value=80, step=10,
        label="Patients per Group", show_value=True
    )
    hazard_control = mo.ui.slider(
        start=0.01, stop=0.15, value=0.05, step=0.005,
        label="Control Hazard Rate", show_value=True
    )
    hazard_treatment = mo.ui.slider(
        start=0.005, stop=0.15, value=0.03, step=0.005,
        label="Treatment Hazard Rate", show_value=True
    )
    censor_pct = mo.ui.slider(
        start=0, stop=50, value=15, step=5,
        label="Censoring Rate (%)", show_value=True
    )
    mo.hstack([n_per_group, hazard_control, hazard_treatment, censor_pct])
    return censor_pct, hazard_control, hazard_treatment, n_per_group


@app.cell(hide_code=True)
def _(censor_pct, hazard_control, hazard_treatment, n_per_group, np):
    # Simulate survival data using exponential distribution
    np.random.seed(42)
    _n = n_per_group.value
    max_time = 60  # months

    # Event times from exponential distribution
    control_event_times = np.random.exponential(1 / hazard_control.value, _n)
    treatment_event_times = np.random.exponential(1 / hazard_treatment.value, _n)

    # Censor times (uniform across study period)
    _censor_rate = censor_pct.value / 100
    control_censor = np.where(
        np.random.random(_n) < _censor_rate,
        np.random.uniform(0, max_time, _n),
        max_time + 1  # beyond study end = not censored
    )
    treatment_censor = np.where(
        np.random.random(_n) < _censor_rate,
        np.random.uniform(0, max_time, _n),
        max_time + 1
    )

    # Observed time = min(event, censor, max_time)
    control_obs = np.minimum(control_event_times, np.minimum(control_censor, max_time))
    control_event = (control_event_times <= np.minimum(control_censor, max_time)).astype(int)

    treatment_obs = np.minimum(treatment_event_times, np.minimum(treatment_censor, max_time))
    treatment_event = (treatment_event_times <= np.minimum(treatment_censor, max_time)).astype(int)

    # True HR
    true_hr = hazard_treatment.value / hazard_control.value
    return (
        control_event,
        control_obs,
        max_time,
        treatment_event,
        treatment_obs,
        true_hr,
    )


@app.cell(hide_code=True)
def _(control_event, control_obs, np, treatment_event, treatment_obs):
    # Kaplan-Meier estimator
    def kaplan_meier(times, events):
        # Sort by time
        order = np.argsort(times)
        times = times[order]
        events = events[order]

        unique_times = np.unique(times[events == 1])
        n_at_risk = len(times)
        survival = 1.0
        km_times = [0.0]
        km_survival = [1.0]
        km_at_risk = [n_at_risk]

        for t in unique_times:
            # Number censored before this time
            n_censored = np.sum((times < t) & (events == 0) & (times > (km_times[-1] if km_times else 0)))
            n_at_risk -= n_censored

            # Events at this time
            n_events = np.sum((times == t) & (events == 1))

            if n_at_risk > 0:
                survival *= (1 - n_events / n_at_risk)

            km_times.append(t)
            km_survival.append(survival)
            km_at_risk.append(n_at_risk)

            n_at_risk -= n_events

        return np.array(km_times), np.array(km_survival), np.array(km_at_risk)

    control_km_t, control_km_s, control_km_n = kaplan_meier(control_obs, control_event)
    treatment_km_t, treatment_km_s, treatment_km_n = kaplan_meier(treatment_obs, treatment_event)

    # Censor marks (times where event=0)
    control_censor_times = control_obs[control_event == 0]
    treatment_censor_times = treatment_obs[treatment_event == 0]
    return (
        control_censor_times,
        control_km_n,
        control_km_s,
        control_km_t,
        kaplan_meier,
        treatment_censor_times,
        treatment_km_n,
        treatment_km_s,
        treatment_km_t,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Kaplan-Meier Survival Curves

    The **step function** shows the estimated probability of surviving past each time point.
    **Tick marks** on the curves indicate censored patients — they were still alive when last observed
    but we don't know what happened after.

    Watch how the curves separate (or don't) as you change the hazard rates.
    """)
    return


@app.cell(hide_code=True)
def _(
    alt,
    control_censor_times,
    control_km_s,
    control_km_t,
    np,
    pd,
    treatment_censor_times,
    treatment_km_s,
    treatment_km_t,
    true_hr,
):
    # Build KM curve data
    control_df = pd.DataFrame({
        'Time (months)': control_km_t,
        'Survival Probability': control_km_s,
        'Group': 'Control'
    })
    treatment_df = pd.DataFrame({
        'Time (months)': treatment_km_t,
        'Survival Probability': treatment_km_s,
        'Group': 'Treatment'
    })
    km_df = pd.concat([control_df, treatment_df], ignore_index=True)

    km_curves = alt.Chart(km_df).mark_line(
        interpolate='step-after', strokeWidth=2.5
    ).encode(
        x=alt.X('Time (months):Q', title='Time (months)'),
        y=alt.Y('Survival Probability:Q', title='Survival Probability',
                 scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('Group:N', scale=alt.Scale(
            domain=['Control', 'Treatment'],
            range=['#d62728', '#2ca02c']
        ))
    ).properties(
        width=700, height=400,
        title=f'Kaplan-Meier Survival Curves (True HR = {true_hr:.2f})'
    )

    # Censor tick marks
    def get_survival_at_time(km_t, km_s, t):
        idx = np.searchsorted(km_t, t, side='right') - 1
        idx = max(0, min(idx, len(km_s) - 1))
        return km_s[idx]

    if len(control_censor_times) > 0:
        control_censor_df = pd.DataFrame({
            'Time (months)': control_censor_times,
            'Survival Probability': [get_survival_at_time(control_km_t, control_km_s, t) for t in control_censor_times],
            'Group': 'Control'
        })
    else:
        control_censor_df = pd.DataFrame(columns=['Time (months)', 'Survival Probability', 'Group'])

    if len(treatment_censor_times) > 0:
        treatment_censor_df = pd.DataFrame({
            'Time (months)': treatment_censor_times,
            'Survival Probability': [get_survival_at_time(treatment_km_t, treatment_km_s, t) for t in treatment_censor_times],
            'Group': 'Treatment'
        })
    else:
        treatment_censor_df = pd.DataFrame(columns=['Time (months)', 'Survival Probability', 'Group'])

    censor_df = pd.concat([control_censor_df, treatment_censor_df], ignore_index=True)

    censor_marks = alt.Chart(censor_df).mark_tick(
        thickness=2, size=10
    ).encode(
        x='Time (months):Q',
        y='Survival Probability:Q',
        color=alt.Color('Group:N', scale=alt.Scale(
            domain=['Control', 'Treatment'],
            range=['#d62728', '#2ca02c']
        ))
    )

    km_chart = km_curves + censor_marks
    km_chart
    return


@app.cell(hide_code=True)
def _(
    control_event,
    control_obs,
    mo,
    n_per_group,
    np,
    treatment_event,
    treatment_obs,
    true_hr,
):
    # Simple log-rank-like summary
    _n = n_per_group.value
    control_events_total = int(np.sum(control_event))
    treatment_events_total = int(np.sum(treatment_event))
    control_median = np.median(control_obs[control_event == 1]) if control_events_total > 0 else float('inf')
    treatment_median = np.median(treatment_obs[treatment_event == 1]) if treatment_events_total > 0 else float('inf')

    mo.md(f"""
    ## Summary Statistics

    | Metric | Control | Treatment |
    |--------|---------|-----------|
    | Patients | {_n} | {_n} |
    | Events | {control_events_total} | {treatment_events_total} |
    | Median event time (months) | {control_median:.1f} | {treatment_median:.1f} |
    | **True Hazard Ratio** | | **{true_hr:.2f}** |

    **Interpreting the HR:**
    - HR = 1.0 → No difference between groups
    - HR < 1.0 → Treatment group has *fewer* events (treatment is protective)
    - HR > 1.0 → Treatment group has *more* events (treatment is harmful)
    - HR = {true_hr:.2f} means the treatment group has **{true_hr:.0%}** the hazard rate of control
      ({(1 - true_hr):.0%} relative risk reduction)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Number at Risk Table

    Below the KM curve, clinical papers always show a **"Number at Risk"** table.
    This tells you how many patients were still being followed at each time point.

    Declining numbers mean patients have either experienced events OR been censored.
    If numbers drop quickly, be cautious about interpreting the tail of the curve — it's based on few patients.
    """)
    return


@app.cell(hide_code=True)
def _(
    alt,
    control_event,
    control_obs,
    max_time,
    np,
    pd,
    treatment_event,
    treatment_obs,
):
    # Number at risk at specific time points
    time_points = list(range(0, max_time + 1, 12))

    nar_data = []
    for t in time_points:
        control_nar = int(np.sum(control_obs >= t))
        treatment_nar = int(np.sum(treatment_obs >= t))
        nar_data.append({'Time': t, 'Group': 'Control', 'At Risk': control_nar})
        nar_data.append({'Time': t, 'Group': 'Treatment', 'At Risk': treatment_nar})

    nar_df = pd.DataFrame(nar_data)

    nar_chart = alt.Chart(nar_df).mark_text(fontSize=12).encode(
        x=alt.X('Time:O', title='Time (months)'),
        y=alt.Y('Group:N', title=None),
        text='At Risk:Q',
        color=alt.Color('Group:N', scale=alt.Scale(
            domain=['Control', 'Treatment'],
            range=['#d62728', '#2ca02c']
        ), legend=None)
    ).properties(
        width=700, height=80,
        title='Number at Risk'
    )

    # Events per interval
    event_data = []
    for i in range(len(time_points) - 1):
        t_start = time_points[i]
        t_end = time_points[i + 1]
        c_events = int(np.sum((control_obs >= t_start) & (control_obs < t_end) & (control_event == 1)))
        t_events = int(np.sum((treatment_obs >= t_start) & (treatment_obs < t_end) & (treatment_event == 1)))
        event_data.append({'Interval': f'{t_start}-{t_end}', 'Control Events': c_events, 'Treatment Events': t_events})

    nar_chart
    return


@app.cell(hide_code=True)
def _(mo):
    # Anchor paper: EMPA-REG OUTCOME
    # Verified: PMID 26378978, DOI: 10.1056/NEJMoa1504720
    mo.md(r"""
    ## Anchor Paper: EMPA-REG OUTCOME (2015)

    **Zinman B, et al.** "Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes."
    *N Engl J Med.* 2015;373(22):2117-28.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/26378978/) |
    [DOI: 10.1056/NEJMoa1504720](https://doi.org/10.1056/NEJMoa1504720)

    **The study:** 7,020 patients with type 2 diabetes and high cardiovascular risk were randomized
    to empagliflozin (an SGLT2 inhibitor) vs. placebo. Primary outcome: composite of CV death, nonfatal MI, nonfatal stroke.

    **Key survival analysis findings:**
    - **HR = 0.86** (95% CI 0.74–0.99) for the primary composite outcome
    - **The KM curves separated early** — within the first few months — and continued to diverge
    - This early separation is a visual hallmark of a **rapid treatment effect**
    - All-cause mortality HR = 0.68 (p < 0.001) — a 32% relative risk reduction

    **Board-relevant concepts from this trial:**
    - **Read the Number at Risk table:** Do the groups remain balanced? High dropout would bias results.
    - **HR interpretation:** HR = 0.86 means at any time point, the empagliflozin group had 86% the hazard of placebo.
    - **Proportional hazards assumption:** The curves don't cross → the HR is relatively constant over time.
    - **Early curve separation** suggests the benefit isn't just long-term risk factor modification — it's an acute protective effect.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Concept | Definition | What to Watch For |
    |---------|------------|-------------------|
    | **Kaplan-Meier curve** | Non-parametric survival estimate | Step-down pattern; tail reliability |
    | **Censoring** | Patient lost/withdrawn before event | Tick marks on KM curve |
    | **Hazard Rate** | Instantaneous event rate at time t | Higher rate → steeper KM decline |
    | **Hazard Ratio (HR)** | Ratio of hazard rates between groups | HR < 1 = treatment benefit |
    | **Number at Risk** | Patients still followed at each time | Low numbers → unstable estimates |
    | **Proportional hazards** | Constant HR over time | Check: do KM curves cross? |
    | **Median survival** | Time when survival reaches 50% | More intuitive than HR for patients |

    ## Questions

    1. Set both hazard rates equal. What does the KM curve look like? What is the HR?

    2. Increase censoring to 50%. How does this affect the reliability of the KM curve's tail?

    3. If KM curves cross each other, what does this mean about the proportional hazards assumption?

    4. A trial reports HR = 0.75 (95% CI: 0.60–0.94). Is this statistically significant? How do you know?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # EMPA-REG OUTCOME — NEJM free article but may block iframe embedding
    # Verified: PMID 26378978, DOI 10.1056/NEJMoa1504720
    mo.accordion(
        {
            "Read the Anchor Paper: EMPA-REG OUTCOME (2015)": mo.md("""
**Zinman B, Wanner C, Lachin JM, et al.** "Empagliflozin, Cardiovascular Outcomes, and Mortality
in Type 2 Diabetes." *N Engl J Med.* 2015;373(22):2117-28.

[Open on PubMed](https://pubmed.ncbi.nlm.nih.gov/26378978/) |
[Open on NEJM (free article)](https://doi.org/10.1056/NEJMoa1504720) |
[Download PDF from NEJM](https://www.nejm.org/doi/pdf/10.1056/NEJMoa1504720)

*This article is free on NEJM. Click the PDF link above to download directly.*
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
