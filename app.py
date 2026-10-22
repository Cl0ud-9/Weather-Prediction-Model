"""A small dashboard: tomorrow's forecast for a city, and how good the model's forecasts have been.

Run with `streamlit run app.py`.
"""
import altair as alt
import pandas as pd
import streamlit as st

from weather import (
    CITIES,
    RAIN_MM,
    TARGETS,
    backtest,
    forecast,
    load_city,
    rain_backtest,
    rain_chance,
    rain_scores,
    reliability,
    scores,
    with_targets,
)

# Categorical slots 1 and 2 of the chart palette (checked for colour-blind separation and contrast)
FORECAST_COLOUR, ACTUAL_COLOUR = "#2a78d6", "#eb6834"
UNITS = {"maxtempc": "°C", "mintempc": "°C", "precipmm": "mm", "uvindex": ""}


@st.cache_data(show_spinner="Training on the city's history...")
def city_results(city):
    daily = load_city(city)
    frame = with_targets(daily)
    day, values = forecast(daily)
    tests = {t: backtest(frame, t) for t in TARGETS}
    rain = rain_backtest(frame)
    return daily.index[-1], day, values, rain_chance(daily), tests, rain


st.set_page_config(page_title="Weather Prediction", page_icon="🌦️", layout="wide")
st.title("🌦️ Weather Prediction")
st.caption("Next-day forecasts for eight Indian cities from each city's own weather history, checked against "
           "'tomorrow will be like today'.")

city = st.selectbox("City", CITIES, index=CITIES.index("pune"), format_func=str.title)
last, day, values, chance, tests, rain = city_results(city)

st.subheader(f"Forecast for {day:%A %d %B %Y}")
st.caption(f"The data runs to {last:%d %B %Y}, so this is the day after the last day in the file.")
tiles = st.columns(5)
for column, (target, label) in zip(tiles, TARGETS.items()):
    s = scores(tests[target])
    unit = UNITS[target]
    column.metric(label, f"{values[target]:.1f} {unit}".strip(),
                  help=f"Over {s['days']:,} past days this forecast was off by {s['model_mae']:.2f} {unit} on average; "
                       f"'same as today' was off by {s['persistence_mae']:.2f}.")
    better = s["model_mae"] < s["persistence_mae"]
    column.caption(f"usually within ±{s['model_mae']:.1f} {unit}" + (" · beats 'same as today'" if better else ""))
r = rain_scores(rain)
tiles[4].metric("Chance of rain", f"{chance:.0%}", help=f"More than {RAIN_MM:g} mm in the day.")
tiles[4].caption(f"Brier score {r['model_brier']:.3f}, against {r['climatology_brier']:.3f} for the month's usual "
                 "chance (lower is better)")

st.divider()
left, right = st.columns([3, 2], gap="large")

with left:
    target = st.radio("Past forecasts", ["maxtempc", "mintempc"], format_func=TARGETS.get, horizontal=True)
    recent = tests[target].iloc[-120:].reset_index(names="date")
    long = recent.melt("date", ["prediction", "actual"], var_name="series", value_name="value")
    long["series"] = long["series"].map({"prediction": "Model's forecast", "actual": "What happened"})
    unit = UNITS[target]
    chart = (
        alt.Chart(long)
        .mark_line(strokeWidth=2)
        .encode(
            x=alt.X("date:T", title=None, axis=alt.Axis(format="%d %b", grid=False)),
            y=alt.Y("value:Q", title=f"{TARGETS[target]}", scale=alt.Scale(zero=False)),
            color=alt.Color("series:N", title=None,
                            scale=alt.Scale(domain=["Model's forecast", "What happened"],
                                            range=[FORECAST_COLOUR, ACTUAL_COLOUR]),
                            legend=alt.Legend(orient="top")),
            tooltip=[alt.Tooltip("date:T", format="%d %b %Y", title="Day"), alt.Tooltip("series:N", title=""),
                     alt.Tooltip("value:Q", format=".1f", title=unit or "value")],
        )
        .properties(height=320)
    )
    hover = alt.selection_point(fields=["date"], nearest=True, on="pointerover", empty=False)
    rule = (alt.Chart(recent).mark_rule(color="#8a8a85").encode(x="date:T", opacity=alt.condition(hover, alt.value(0.6),
                                                                                                   alt.value(0)))
            .add_params(hover))
    st.altair_chart(chart + rule, use_container_width=True)
    s = scores(tests[target])
    st.caption(f"The last 120 of {s['days']:,} days the model was tested on. Each forecast was made by a model "
               "trained only on the days before it.")

with right:
    st.markdown("**When it says rain, does it rain?**")
    table = reliability(rain).reset_index(drop=True)
    table = pd.DataFrame({
        "The model said": [f"{a:.0%}" for a in table["forecast"]],
        "It rained on": [f"{b:.0%}" for b in table["rained"]],
        "Days": table["days"].map("{:,}".format),
    })
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.caption(f"Over {r['days']:,} past days, grouped by the chance the model gave. When the two columns agree, a "
               f"'70%' can be taken at its word. Rain here means more than {RAIN_MM:g} mm.")

with st.expander("What this can and cannot tell you"):
    st.markdown("- It only knows this city's own past: no satellites, no pressure maps, no neighbouring regions.\n"
                "- The data ends in 2023, so the forecast is for the day after the file ends, not tomorrow.\n"
                "- Rain amounts are hard to forecast from one place's history; the chance of rain is much more "
                "useful than the amount.")
