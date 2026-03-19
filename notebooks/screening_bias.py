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
app = marimo.App(width="medium", app_title="Bias: Lead-Time and Length-Time")


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
    # Bias in Screening: Lead-Time and Length-Time

    Screening tests can save lives — but they can also **appear** to save lives even when they don't.
    Two critical biases create this illusion:

    1. **Lead-time bias:** Detecting disease earlier starts the "survival clock" sooner, making survival
       *look* longer even if the death date doesn't change.
    2. **Length-time bias:** Screening preferentially detects slow-growing (less aggressive) diseases,
       because they spend more time in the detectable-but-asymptomatic window.

    Understanding these biases is essential for interpreting screening studies — and a board favorite!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Part 1: Lead-Time Bias

    Imagine a disease that always kills 10 years after it starts (biologic onset).
    - **Without screening**, symptoms appear at year 7, and the patient "survives" 3 years after diagnosis.
    - **With screening**, the disease is detected at year 3, and the patient "survives" 7 years after diagnosis.

    **Same death date. Same outcome. But "survival after diagnosis" doubled!**

    Use the sliders to explore this.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    onset_to_death = mo.ui.slider(
        start=5, stop=20, value=10, step=1,
        label="Years from Onset to Death", show_value=True
    )
    symptom_year = mo.ui.slider(
        start=1, stop=15, value=7, step=1,
        label="Year Symptoms Appear (after onset)", show_value=True
    )
    screening_year = mo.ui.slider(
        start=1, stop=10, value=3, step=1,
        label="Year Screening Detects (after onset)", show_value=True
    )
    mo.hstack([onset_to_death, symptom_year, screening_year])
    return onset_to_death, screening_year, symptom_year


@app.cell(hide_code=True)
def _(alt, mo, onset_to_death, pd, screening_year, symptom_year):
    # Timeline visualization for lead-time bias
    _death = onset_to_death.value
    _symptom = min(symptom_year.value, _death)
    _screen = min(screening_year.value, _symptom)

    # Patient A: No screening (diagnosed at symptom onset)
    # Patient B: Screening (diagnosed at screening detection)
    survival_no_screen = _death - _symptom
    survival_with_screen = _death - _screen
    lead_time = _symptom - _screen

    # Build timeline data
    timeline_data = []

    # Patient without screening
    timeline_data.append({'Patient': 'No Screening', 'Phase': 'Pre-symptomatic', 'Start': 0, 'End': _symptom, 'Color': '#aaaaaa'})
    timeline_data.append({'Patient': 'No Screening', 'Phase': f'Survival = {survival_no_screen} yrs', 'Start': _symptom, 'End': _death, 'Color': '#d62728'})

    # Patient with screening
    timeline_data.append({'Patient': 'With Screening', 'Phase': 'Pre-detection', 'Start': 0, 'End': _screen, 'Color': '#aaaaaa'})
    timeline_data.append({'Patient': 'With Screening', 'Phase': f'Lead Time = {lead_time} yrs', 'Start': _screen, 'End': _symptom, 'Color': '#ff7f0e'})
    timeline_data.append({'Patient': 'With Screening', 'Phase': f'Post-symptom = {survival_no_screen} yrs', 'Start': _symptom, 'End': _death, 'Color': '#2ca02c'})

    tl_df = pd.DataFrame(timeline_data)

    gantt = alt.Chart(tl_df).mark_bar(height=30).encode(
        x=alt.X('Start:Q', title='Years Since Disease Onset'),
        x2='End:Q',
        y=alt.Y('Patient:N', title='', sort=['No Screening', 'With Screening']),
        color=alt.Color('Phase:N', scale=alt.Scale(
            domain=tl_df['Phase'].tolist(),
            range=tl_df['Color'].tolist()
        ), legend=alt.Legend(title='Phase')),
        tooltip=['Patient:N', 'Phase:N', 'Start:Q', 'End:Q']
    ).properties(
        width=700, height=150,
        title='Lead-Time Bias: Same Death Date, Different "Survival"'
    )

    # Death marker
    death_df = pd.DataFrame({
        'x': [_death, _death],
        'Patient': ['No Screening', 'With Screening']
    })
    death_mark = alt.Chart(death_df).mark_point(
        shape='cross', size=200, color='black', strokeWidth=3
    ).encode(
        x='x:Q',
        y=alt.Y('Patient:N', sort=['No Screening', 'With Screening'])
    )

    _gantt_combined = gantt + death_mark
    mo.vstack([
        _gantt_combined,
        mo.accordion({"View data table": mo.ui.table(tl_df)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">Lead-time bias timeline: without screening survival is {survival_no_screen} years, with screening apparent survival is {survival_with_screen} years. Lead time is {lead_time} years.</div>')
    ])
    return lead_time, survival_no_screen, survival_with_screen


@app.cell(hide_code=True)
def _(lead_time, mo, survival_no_screen, survival_with_screen):
    mo.md(f"""
    ## Lead-Time Bias Summary

    | Scenario | Survival After Diagnosis |
    |----------|------------------------|
    | **No Screening** | **{survival_no_screen} years** (diagnosed when symptoms appear) |
    | **With Screening** | **{survival_with_screen} years** (diagnosed earlier by screening) |
    | **Lead Time** | **{lead_time} years** (the "extra" survival is purely from earlier detection) |

    **The patient dies at the exact same time!** The apparent survival benefit of {survival_with_screen - survival_no_screen} years
    is entirely **lead-time bias**.

    **To prove screening actually works, you need to show a reduction in *mortality rate*, not just longer survival after diagnosis.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Part 2: Length-Time Bias

    Not all diseases progress at the same rate. In the simulation below, each bar represents a disease
    with a different growth rate (slow, medium, or fast).

    - **Fast-growing** diseases spend little time in the "detectable but asymptomatic" window → screening often misses them
    - **Slow-growing** diseases linger in that window → screening easily catches them

    Result: **screened patients appear to have better prognoses**, but that's because screening over-samples
    the less aggressive cases.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    n_patients_sim = mo.ui.slider(
        start=20, stop=100, value=50, step=10,
        label="Number of Patients", show_value=True
    )
    mo.hstack([n_patients_sim])
    return (n_patients_sim,)


@app.cell(hide_code=True)
def _(alt, mo, n_patients_sim, np, pd):
    # Simulate diseases with different growth rates
    np.random.seed(42)
    _n = n_patients_sim.value

    # Assign growth rates: 40% slow, 35% medium, 25% fast
    growth_types = np.random.choice(
        ['Slow-growing', 'Medium', 'Fast-growing'],
        size=_n,
        p=[0.40, 0.35, 0.25]
    )

    # Detectable window duration (years in the asymptomatic-but-detectable phase)
    window_map = {'Slow-growing': 8, 'Medium': 4, 'Fast-growing': 1.5}

    # Screening happens at random time; disease detected if screening falls in the window
    diseases = []
    for i in range(_n):
        gtype = growth_types[i]
        window = window_map[gtype]
        onset = np.random.uniform(0, 10)  # random onset within 10-year period
        window_start = onset
        window_end = onset + window

        # Single screening at year 5
        screening_time = 5
        detected_by_screening = window_start <= screening_time <= window_end

        diseases.append({
            'Patient': i + 1,
            'Growth Type': gtype,
            'Window (years)': window,
            'Onset': onset,
            'Window Start': window_start,
            'Window End': window_end,
            'Detected by Screening': 'Yes' if detected_by_screening else 'No'
        })

    disease_df = pd.DataFrame(diseases)

    # Count detection rates by type
    detection_summary = disease_df.groupby('Growth Type').agg(
        Total=('Patient', 'count'),
        Detected=('Detected by Screening', lambda x: (x == 'Yes').sum())
    ).reset_index()
    detection_summary['Detection Rate (%)'] = (detection_summary['Detected'] / detection_summary['Total'] * 100).round(1)

    # Visualization: detection rate by growth type
    detect_bars = alt.Chart(detection_summary).mark_bar(width=60).encode(
        x=alt.X('Growth Type:O', sort=['Slow-growing', 'Medium', 'Fast-growing'], title='Disease Aggressiveness'),
        y=alt.Y('Detection Rate (%):Q', scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Growth Type:N', scale=alt.Scale(
            domain=['Slow-growing', 'Medium', 'Fast-growing'],
            range=['#2ca02c', '#ff7f0e', '#d62728']
        )),
        tooltip=['Growth Type:N', 'Total:Q', 'Detected:Q', 'Detection Rate (%):Q']
    ).properties(
        width=400, height=300,
        title='Screening Detection Rate by Disease Aggressiveness'
    )

    detect_text = alt.Chart(detection_summary).mark_text(
        dy=-10, fontSize=12, fontWeight='bold'
    ).encode(
        x=alt.X('Growth Type:O', sort=['Slow-growing', 'Medium', 'Fast-growing']),
        y='Detection Rate (%):Q',
        text=alt.Text('Detection Rate (%):Q', format='.1f')
    )

    detect_chart = detect_bars + detect_text
    mo.vstack([
        detect_chart,
        mo.accordion({"View data table": mo.ui.table(detection_summary)}),
        mo.Html(f'<div aria-live="polite" aria-atomic="true" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;">Detection rate bar chart for {n_patients_sim.value} patients showing screening detection rates by disease aggressiveness: slow-growing, medium, and fast-growing tumors.</div>')
    ])
    return (disease_df,)


@app.cell(hide_code=True)
def _(disease_df, mo):
    _total_detected = int((disease_df['Detected by Screening'] == 'Yes').sum())
    _slow_detected = int(((disease_df['Growth Type'] == 'Slow-growing') & (disease_df['Detected by Screening'] == 'Yes')).sum())
    _pct_slow = _slow_detected / _total_detected * 100 if _total_detected > 0 else 0

    mo.md(f"""
    ## Length-Time Bias in Action

    Of the **{_total_detected}** patients detected by screening, **{_slow_detected} ({_pct_slow:.0f}%)** had slow-growing disease.

    This means the screened group is **enriched for less aggressive disease**. If we compare their outcomes
    to symptomatic patients (who are enriched for aggressive disease), screened patients will appear to do better —
    even if screening didn't change any outcomes!

    **This is length-time bias.** It makes screening look more effective than it actually is.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Anchor paper: NLST
    # Verified: PMID 21714641, DOI: 10.1056/NEJMoa1102873
    mo.md(r"""
    ## Anchor Paper: NLST — National Lung Screening Trial (2011)

    **National Lung Screening Trial Research Team.** "Reduced lung-cancer mortality with low-dose
    computed tomographic screening." *N Engl J Med.* 2011;365(5):395-409.
    [PubMed](https://pubmed.ncbi.nlm.nih.gov/21714641/) |
    [DOI: 10.1056/NEJMoa1102873](https://doi.org/10.1056/NEJMoa1102873)

    **The study:** 53,454 high-risk patients randomized to annual low-dose CT (LDCT) vs. chest X-ray
    for 3 rounds. Primary outcome: lung cancer mortality.

    **Why this paper matters for bias:**
    - NLST showed a **20% relative reduction in lung cancer mortality** with LDCT
    - Critically, they used **mortality** as the endpoint, NOT "5-year survival after diagnosis"
    - This is precisely because **lead-time bias** would inflate survival statistics without proving benefit
    - **Length-time bias** was also a concern: LDCT detects many slow-growing nodules (overdiagnosis)
    - NLST estimated ~18% of screen-detected cancers may have been **overdiagnosed** (would never have caused symptoms)

    **Board-relevant vignette:** *A screening study reports that screened patients survive an average of 7 years
    after diagnosis vs. 3 years for unscreened patients. Does this prove screening saves lives?*

    **No!** You must see reduced **mortality in the screened group** (an intention-to-treat analysis),
    not just longer survival after diagnosis. Lead-time bias alone could explain the difference.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Concepts Summary

    | Bias | Mechanism | How to Detect/Prevent |
    |------|-----------|----------------------|
    | **Lead-time bias** | Earlier detection → longer apparent survival | Use mortality, not survival, as endpoint |
    | **Length-time bias** | Screening catches slow diseases preferentially | Compare mortality rates, not case fatality |
    | **Overdiagnosis** | Detecting disease that would never cause harm | Long-term follow-up; compare all-cause mortality |

    **Other screening biases to know:**
    - **Selection bias / Healthy volunteer effect:** People who get screened tend to be healthier
    - **Will Rogers phenomenon:** Stage migration — better imaging reclassifies patients to higher stages,
      making *all* stages appear to have better survival

    ## Questions

    1. A new screening test finds cancer an average of 5 years earlier. Screened patients survive 8 years vs. 4 years for unscreened. Is the test saving lives?

    2. In a screening study, 70% of screen-detected cancers are low-grade. In symptomatic patients, only 30% are low-grade. What bias explains this?

    3. How does the NLST study design avoid lead-time bias in its conclusions?

    4. What is "overdiagnosis" and why is it a harm of screening, even if the test is accurate?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # NLST — PMC free full text available
    # Verified: PMID 21714641, DOI 10.1056/NEJMoa1102873, PMCID PMC4356534
    mo.accordion(
        {
            "Read the Anchor Paper: NLST (2011)": mo.pdf(
                src="https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4356534/pdf/nihms320819.pdf",
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
