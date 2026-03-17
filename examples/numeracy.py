import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import altair as alt
    import polars as pl
    import numpy as np
    import openai
    import os
    from dotenv import load_dotenv
    load_dotenv(override=True)
    print(os.environ.get("LITELLM_API_KEY"))
    return alt, mo, np, os, pl


@app.cell
def _(mo):
    mo.md(r"""
    # Numeracy

    Let's review logarithms and exponential equations - 2 sides of the same coin that are essential in modeling how drugs leave the body.
    """)
    return


@app.cell
def _(mo):
    mo.md(f"""
    # Logarithms: visualizing log(a), log(b), and log(a·b)

    Use the controls below to explore how logarithms work. The plot shows:
    - The logarithm curve log_base(x)
    - Dotted vertical lines at x = a, x = b, and x = a·b
    - Circles at the points (a, log(a)), (b, log(b)), and (a·b, log(a·b))

    This helps visualize the identity: log(a) + log(b) = log(a·b).
    """)
    return


@app.cell
def _(mo):
    # Controls for log visualization
    base_choice = mo.ui.radio(
        options={"e (≈2.718)": "e", "10": "10", "2": "2", "custom": "custom"},
        value="e (≈2.718)",
        label="Log base"
    )
    base_custom = mo.ui.number(value=2.5, label="Custom base (>0, != 1)")

    slider_a = mo.ui.slider(0.1, 20.0, value=2.0, step=0.1, label="a")
    slider_b = mo.ui.slider(0.1, 20.0, value=3.0, step=0.1, label="b")

    x_range = mo.ui.range_slider(0.05, 100.0, value=(0.05, 25.0), step=0.05, label="x range")

    mo.vstack([
        mo.hstack([base_choice, base_custom]),
        mo.hstack([slider_a, slider_b]),
        x_range,
    ])
    return base_choice, base_custom, slider_a, slider_b, x_range


@app.cell
def _(base_choice, base_custom, mo, np, pl, slider_a, slider_b, x_range):
    # Compute log curve and markers based on controls
    # Determine base from radio/custom
    if base_choice.value == "e":
        _base = np.e
    elif base_choice.value == "10":
        _base = 10.0
    elif base_choice.value == "2":
        _base = 2.0
    else:
        _base = float(base_custom.value) if base_custom.value is not None else np.e

    # Validate base
    _valid_base = (isinstance(_base, (int, float))) and (_base > 0) and (abs(_base - 1.0) > 1e-12)
    mo.stop(not _valid_base, mo.md("Please choose a base > 0 and != 1."))

    # Label for titles/tooltips
    base_label_ = (
        "e" if abs(_base - np.e) < 1e-12 else ("10" if _base == 10.0 else ("2" if _base == 2.0 else f"{_base:g}"))
    )

    # X range and sampling
    x_min_, x_max_ = x_range.value
    mo.stop(x_max_ <= x_min_, mo.md("Increase the x range max to be larger than min."))

    # Use geometric spacing to cover wide ranges smoothly
    xs_ = np.geomspace(max(1e-6, x_min_), max(1e-6, x_max_), 400)

    # Change of base formula: log_base(x) = ln(x)/ln(base)
    ln_base_ = np.log(_base)
    ys_ = np.log(xs_) / ln_base_
    curve_df = pl.DataFrame({"x": xs_, "y": ys_})

    # Points a, b, and a*b
    _a = float(slider_a.value)
    _b = float(slider_b.value)
    ab_ = _a * _b
    points_df = pl.DataFrame({
        "x": [_a, _b, ab_],
        "which": ["a", "b", "a·b"],
        "y": list(np.log(np.array([_a, _b, ab_])) / ln_base_),
    })
    return base_label_, curve_df, points_df


@app.cell
def _(base_choice, base_custom, mo, np, pl, slider_a, slider_b, x_range):
    # Compute log curve and markers based on controls (linear x-axis sampling)
    # Determine base from radio/custom
    if base_choice.value == "e":
        _base = np.e
    elif base_choice.value == "10":
        _base = 10.0
    elif base_choice.value == "2":
        _base = 2.0
    else:
        _base = float(base_custom.value) if base_custom.value is not None else np.e

    # Validate base
    _valid_base = (isinstance(_base, (int, float))) and (_base > 0) and (abs(_base - 1.0) > 1e-12)
    mo.stop(not _valid_base, mo.md("Please choose a base > 0 and != 1."))

    # Label for titles/tooltips
    base_label_lin = (
        "e" if abs(_base - np.e) < 1e-12 else ("10" if _base == 10.0 else ("2" if _base == 2.0 else f"{_base:g}"))
    )

    # X range and sampling (linear)
    x_min_lin, x_max_lin = x_range.value
    mo.stop(x_max_lin <= x_min_lin, mo.md("Increase the x range max to be larger than min."))
    xs_lin = np.linspace(x_min_lin, x_max_lin, 500)

    # Change of base formula: log_base(x) = ln(x)/ln(base)
    ln_base_lin = np.log(_base)
    ys_lin = np.log(xs_lin) / ln_base_lin
    curve_df_lin = pl.DataFrame({"x": xs_lin, "y": ys_lin})

    # Points a, b, and a*b
    _a = float(slider_a.value)
    _b = float(slider_b.value)
    ab_lin = _a * _b
    points_df_lin = pl.DataFrame({
        "x": [_a, _b, ab_lin],
        "which": ["a", "b", "a·b"],
        "y": list(np.log(np.array([_a, _b, ab_lin])) / ln_base_lin),
    })
    return base_label_lin, curve_df_lin, points_df_lin


@app.cell
def _(alt, base_label_, curve_df, mo, pl, points_df):
    # Altair plot: log curve and markers
    # Combine curve and points into one chart with vlines
    base_title = f"log base {base_label_}"
    curve_chart = (
        alt.Chart(curve_df)
        .mark_line(color="#1f77b4")
        .encode(
            x=alt.X("x", type="quantitative", title="x", scale=alt.Scale(type="log", nice=False)),
            y=alt.Y("y", type="quantitative", title=base_title),
            tooltip=[alt.Tooltip("x:Q", format=".3g"), alt.Tooltip("y:Q", format=".3f", title=f"log_{base_label_}(x)")],
        )
        .properties(width=650, height=400)
    )

    # Vertical lines for a, b, ab
    vlines_df = points_df.select([pl.col("x"), pl.col("which")])

    vlines_chart = (
        alt.Chart(vlines_df)
        .mark_rule(strokeDash=[4,4], color="#888")
        .encode(x="x:Q")
    )

    # Circles at (a, log(a)), (b, log(b)), (ab, log(ab))
    points_chart = (
        alt.Chart(points_df)
        .mark_circle(size=100)
        .encode(
            x="x:Q",
            y="y:Q",
            color=alt.Color("which:N", title="Point"),
            tooltip=["which:N", alt.Tooltip("x:Q", format=".3g"), alt.Tooltip("y:Q", format=".3f")],
        )
    )

    # Labels for points
    labels_chart = (
        alt.Chart(points_df)
        .mark_text(dy=-12)
        .encode(x="x:Q", y="y:Q", text="which:N", color="which:N")
    )

    combined = curve_chart + vlines_chart + points_chart + labels_chart

    mo.ui.altair_chart(combined)
    return


@app.cell
def _(alt, base_label_lin, curve_df_lin, mo, pl, points_df_lin):
    # Altair plot with linear x-axis (curved log shape)
    base_title_lin = f"log base {base_label_lin}"
    curve_chart_lin = (
        alt.Chart(curve_df_lin)
        .mark_line(color="#1f77b4")
        .encode(
            x=alt.X("x", type="quantitative", title="x"),
            y=alt.Y("y", type="quantitative", title=base_title_lin),
            tooltip=[alt.Tooltip("x:Q", format=".3g"), alt.Tooltip("y:Q", format=".3f", title=f"log_{base_label_lin}(x)")],
        )
        .properties(width=650, height=400)
    )

    # Vertical lines for a, b, ab on linear axis
    vlines_lin = points_df_lin.select([pl.col("x"), pl.col("which")])

    vlines_chart_lin = (
        alt.Chart(vlines_lin)
        .mark_rule(strokeDash=[4,4], color="#888")
        .encode(x="x:Q")
    )

    # Circles at (a, log(a)), (b, log(b)), (ab, log(ab)) on linear axis
    points_chart_lin = (
        alt.Chart(points_df_lin)
        .mark_circle(size=100)
        .encode(
            x="x:Q",
            y="y:Q",
            color=alt.Color("which:N", title="Point"),
            tooltip=["which:N", alt.Tooltip("x:Q", format=".3g"), alt.Tooltip("y:Q", format=".3f")],
        )
    )

    labels_chart_lin = (
        alt.Chart(points_df_lin)
        .mark_text(dy=-12)
        .encode(x="x:Q", y="y:Q", text="which:N", color="which:N")
    )

    combined_lin = curve_chart_lin + vlines_chart_lin + points_chart_lin + labels_chart_lin

    mo.ui.altair_chart(combined_lin)
    return


@app.cell
def _(mo, os):
    chat = mo.ui.chat(
        mo.ai.llm.openai(
            model="gpt-oss-120b",
            api_key=os.environ.get("LITELLM_API_KEY"),
            base_url="https://api.ai.it.ufl.edu",
            system_message="You are a helpful assistant helping medical residents and fellows learn biostatistics.",
        ),
    )
    chat
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
