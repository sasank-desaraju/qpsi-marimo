# Planning the Syllabus for the Project



# Gemini Proposed Syllabus

## 1. The $p$-value, Power, and Effect Size Triad

- **The Visualization:** Sliders to adjust Sample Size ($n$), Effect Size ($\Delta$), and $\alpha$. A dynamic plot shows the overlapping Bell curves and the shaded "Power" ($\beta$) vs. "Type I Error" ($\alpha$) areas.
    
- **The Anchor Paper:** **The SPRINT Trial (2015)** — Intensive vs. Standard BP control. Great for discussing why they stopped early (high power/large effect).
    
- **Board Yield:** Understanding how $n$ affects power and the "fragility" of a $p$-value.
    

## 2. Diagnostic Testing: The 2x2 Matrix & Prevalence

- **The Visualization:** An interactive "Square" (1000 dots). Sliders for **Sensitivity** and **Specificity**. A "Prevalence" slider that shifts the dots between "Sick" and "Healthy" columns.
    
- **The Anchor Paper:** **D-dimer for PE (PIOPED II)** — Perfect for showing high sensitivity but low specificity, and how PPV tanks when prevalence is low.
    
- **Board Yield:** Sensitivity/Specificity (intrinsic) vs. PPV/NPV (prevalence-dependent).
    

## 3. Likelihood Ratios & Fagan’s Nomogram

- **The Visualization:** An interactive Nomogram. Drag the "Pre-test Probability" and "Likelihood Ratio" to see the "Post-test Probability" calculate in real-time.
    
- **The Anchor Paper:** **The Physical Exam (Rational Clinical Examination series in JAMA)** — e.g., using a JVP to diagnose Heart Failure.
    
- **Board Yield:** Moving beyond the 2x2 table to clinical application.
    

## 4. Survival Analysis: Kaplan-Meier & Hazard Ratios

- **The Visualization:** A plot where users can "censor" data points by clicking them and see the KM curve shift. A slider to adjust the Hazard Ratio (HR).
    
- **The Anchor Paper:** **EMPA-REG OUTCOME (2015)** — SGLT2 inhibitors in Type 2 Diabetes. The curves split very early, which is a great visual for HR.
    
- **Board Yield:** Interpreting "Number at Risk," censoring, and the proportionality assumption.
    

## 5. Precision vs. Significance (Confidence Intervals)

- **The Visualization:** A "Forest Plot" style chart of 20 simulated trials. As the user increases the sample size, the CIs narrow.
    
- **The Anchor Paper:** **ISIS-2 (1988)** — Aspirin/Streptokinase for MI. The sheer size of the study made the CIs incredibly tight.
    
- **Board Yield:** If the CI crosses 1.0 (OR/RR) or 0 (Mean Difference), $p > 0.05$.
    

## 6. Measures of Association: OR vs. RR vs. NNT

- **The Visualization:** An interactive bar chart. Changing the baseline risk shows how NNT (1/Absolute Risk Reduction) explodes as risk decreases, even if RR remains constant.
    
- **The Anchor Paper:** **WOSCOPS (1995)** — Pravastatin for primary prevention. Great for discussing Relative vs. Absolute risk reduction.
    
- **Board Yield:** NNT/NNH calculations and understanding why RR can be misleading.
    

## 7. ROC Curves & The "Optimal" Cutoff

- **The Visualization:** A dual-histogram of "Diseased" vs. "Non-diseased" distributions. As you slide the "Cutoff" line, the ROC curve point moves, showing the trade-off between Sensitivity and $1-\text{Specificity}$.
    
- **The Anchor Paper:** **Troponin T for MI (1990s)** — Determining the "upper limit of normal" for cardiac biomarkers.
    
- **Board Yield:** Area Under the Curve (AUC) as a measure of test "goodness."
    

## 8. Bias: Lead-time and Length-time

- **The Visualization:** An animation of a timeline. "Screening" happens at different points. You can see how finding a disease earlier _looks_ like longer survival even if the death date doesn't change.
    
- **The Anchor Paper:** **NLST (National Lung Screening Trial)** — LDCT for lung cancer.
    
- **Board Yield:** Identifying these biases in screening study vignettes.
    

## 9. Systematic Reviews: Heterogeneity & Forest Plots

- **The Visualization:** A Forest Plot where you can toggle individual studies on/off. See the "Diamond" (pooled estimate) shift and the $I^2$ (heterogeneity) update.
    
- **The Anchor Paper:** **Any Cochrane Review** (e.g., Albumin in fluid resuscitation).
    
- **Board Yield:** Reading a Forest Plot and understanding what the "Diamond" and the "Whiskers" represent.
    

## 10. Correlation vs. Regression (The Slope)

- **The Visualization:** A scatterplot where you can drag points. The "Line of Best Fit" and $R^2$ update instantly.
    
- **The Anchor Paper:** **Framingham Heart Study** — Original papers relating Cholesterol levels to Coronary Heart Disease.
    
- **Board Yield:** $R$ (correlation) vs. $R^2$ (coefficient of determination).
    

---

## Suggested MVP (6 Notebooks)

If you need an MVP of 6, I’d bundle them like this:

1. **The Basics:** Hypothesis Testing, Power, and $p$-values.
    
2. **The Diagnostic Lab:** Sens/Spec, PPV/NPV, and Prevalence.
    
3. **Clinical Application:** Likelihood Ratios and ROC Curves.
    
4. **Treatment Effects:** RR, OR, ARR, and NNT.
    
5. **Time-to-Event:** Kaplan-Meier and Hazard Ratios.
    
6. **Evidence Synthesis:** Confidence Intervals and Forest Plots.
    


