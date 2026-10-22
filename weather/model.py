"""Predict tomorrow's weather from today's with ridge regression, and measure it honestly."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TARGETS = {
    "maxtempc": "Maximum temperature (°C)",
    "mintempc": "Minimum temperature (°C)",
    "precipmm": "Precipitation (mm)",
    "uvindex": "UV index",
}


def add_season(daily):
    """Day of the year as a point on a circle, so 31 December sits next to 1 January."""
    angle = 2 * np.pi * daily.index.dayofyear / 365.25
    return daily.assign(season_sin=np.sin(angle), season_cos=np.cos(angle))


def add_history(daily):
    """Recent history of each predicted value: yesterday's, and the average of the last 7 and 30 days."""
    out = daily.copy()
    for t in TARGETS:
        yesterday = daily[t].reindex(daily.index - pd.Timedelta(days=1))
        out[f"{t}_yesterday"] = yesterday.to_numpy()
        out[f"{t}_mean7"] = daily[t].rolling("7D").mean()
        out[f"{t}_mean30"] = daily[t].rolling("30D").mean()
    # The first day has no yesterday; fall back to the same day
    for t in TARGETS:
        out[f"{t}_yesterday"] = out[f"{t}_yesterday"].fillna(out[t])
    return out


def with_targets(daily):
    """Pair each day's readings with the next calendar day's values. Days whose next day is missing are dropped."""
    features = add_season(add_history(daily))
    tomorrow = daily[list(TARGETS)].reindex(daily.index + pd.Timedelta(days=1))
    tomorrow.index = daily.index
    targets = tomorrow.add_prefix("next_")
    return features.join(targets).dropna(subset=list(targets.columns))


def feature_columns(frame):
    return [c for c in frame.columns if not c.startswith("next_")]


def new_model(alpha=1.0):
    return make_pipeline(StandardScaler(), Ridge(alpha=alpha))


def backtest(frame, target, start_days=730, step_days=90):
    """Walk forward through time: train on every day before a block, predict the block, move on.

    Returns each tested day's actual value, the model's prediction, and the persistence baseline
    ("tomorrow will be like today").
    """
    if target not in TARGETS:
        raise ValueError(f"unknown target {target!r}")
    features, label = feature_columns(frame), f"next_{target}"
    parts = []
    for start in range(start_days, len(frame), step_days):
        train, test = frame.iloc[:start], frame.iloc[start:start + step_days]
        model = new_model().fit(train[features], train[label])
        parts.append(pd.DataFrame({"actual": test[label], "prediction": model.predict(test[features]),
                                   "persistence": test[target]}, index=test.index))
    if not parts:
        raise ValueError(f"need more than {start_days} days to backtest; have {len(frame)}")
    return pd.concat(parts)


def scores(predictions):
    """Mean absolute error of the model and of the persistence baseline."""
    return {"model_mae": mean_absolute_error(predictions["actual"], predictions["prediction"]),
            "persistence_mae": mean_absolute_error(predictions["actual"], predictions["persistence"]),
            "days": len(predictions)}


def forecast(daily):
    """Train on all history and predict the day after the last day in the data."""
    frame = with_targets(daily)
    today = add_season(add_history(daily)).iloc[[-1]]
    features = feature_columns(frame)
    values = {t: float(new_model().fit(frame[features], frame[f"next_{t}"]).predict(today[features])[0])
              for t in TARGETS}
    values["precipmm"] = max(values["precipmm"], 0.0)  # rain cannot be negative
    return today.index[0] + pd.Timedelta(days=1), values


# ---------- Chance of rain

RAIN_MM = 1.0  # a "rainy day" has more than this much rain; lighter amounts are mostly drizzle and dew


def new_rain_model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=2000))


def rain_probabilities(train_x, train_rainy, test_x):
    """The chance of rain for each row of test_x. If the training days were all dry (or all wet) there is nothing to
    learn from, so every chance is that observed rate."""
    if train_rainy.nunique() < 2:
        return np.full(len(test_x), float(train_rainy.mean()))
    return new_rain_model().fit(train_x, train_rainy).predict_proba(test_x)[:, 1]


def rain_backtest(frame, start_days=730, step_days=90):
    """Walk forward through time like backtest(), forecasting the chance that tomorrow is rainy.

    Returns each tested day's outcome (1 if it rained more than RAIN_MM), the model's probability, and two baselines:
    persistence (rain tomorrow if it rained today) and climatology (the share of rainy days in that calendar month
    in the training years).
    """
    features = feature_columns(frame)
    rainy = (frame["next_precipmm"] > RAIN_MM).astype(int)
    parts = []
    for start in range(start_days, len(frame), step_days):
        train, test = frame.iloc[:start], frame.iloc[start:start + step_days]
        monthly = rainy.iloc[:start].groupby(train.index.month).mean()
        parts.append(pd.DataFrame({
            "rained": rainy.iloc[start:start + step_days],
            "probability": rain_probabilities(train[features], rainy.iloc[:start], test[features]),
            "persistence": (test["precipmm"] > RAIN_MM).astype(float),
            "climatology": test.index.month.map(monthly).astype(float),
        }, index=test.index))
    if not parts:
        raise ValueError(f"need more than {start_days} days to backtest; have {len(frame)}")
    return pd.concat(parts)


def rain_scores(predictions):
    """Brier score (mean squared error of the probability; 0 is perfect) of the model and both baselines."""
    brier = lambda column: float(np.mean((predictions[column] - predictions["rained"]) ** 2))  # noqa: E731
    return {"model_brier": brier("probability"), "persistence_brier": brier("persistence"),
            "climatology_brier": brier("climatology"), "rainy_share": float(predictions["rained"].mean()),
            "days": len(predictions)}


def reliability(predictions, bins=(0, 0.2, 0.4, 0.6, 0.8, 1.0)):
    """How often it rained when the model gave each range of chances: well calibrated if the two columns agree."""
    groups = pd.cut(predictions["probability"], bins, include_lowest=True)
    table = predictions.groupby(groups, observed=True).agg(forecast=("probability", "mean"),
                                                           rained=("rained", "mean"), days=("rained", "size"))
    return table


def rain_chance(daily):
    """Train on all history and give the chance that the day after the last day in the data is rainy."""
    frame = with_targets(daily)
    today = add_season(add_history(daily)).iloc[[-1]]
    features = feature_columns(frame)
    rainy = (frame["next_precipmm"] > RAIN_MM).astype(int)
    return float(rain_probabilities(frame[features], rainy, today[features])[0])
