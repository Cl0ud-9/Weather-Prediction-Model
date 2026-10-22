import pandas as pd
import pytest

import predict
from weather import TARGETS, backtest, forecast, load_city, scores, with_targets


@pytest.fixture
def daily(data_dir):
    return load_city("pune", data_dir)


def test_targets_are_the_next_calendar_day(daily):
    gappy = daily.drop(pd.Timestamp("2015-03-10"))
    frame = with_targets(gappy)
    assert pd.Timestamp("2015-03-09") not in frame.index  # its next day is missing, so it cannot be a training row
    day = pd.Timestamp("2015-03-11")
    assert frame.loc[day, "next_maxtempc"] == gappy.loc[day + pd.Timedelta(days=1), "maxtempc"]


def test_backtest_only_learns_from_the_past(daily):
    frame = with_targets(daily)
    predictions = backtest(frame, "maxtempc", start_days=365, step_days=90)
    assert predictions.index.min() == frame.index[365]
    assert predictions.index.is_unique
    assert set(predictions.columns) == {"actual", "prediction", "persistence"}


def test_model_beats_persistence_on_a_seasonal_signal(daily):
    s = scores(backtest(with_targets(daily), "maxtempc", start_days=365))
    assert s["model_mae"] < s["persistence_mae"]


def test_backtest_needs_enough_days(daily):
    with pytest.raises(ValueError):
        backtest(with_targets(daily).iloc[:100], "maxtempc")


def test_forecast_is_for_the_day_after_the_data(daily):
    day, values = forecast(daily)
    assert day == daily.index[-1] + pd.Timedelta(days=1)
    assert set(values) == set(TARGETS)
    assert values["precipmm"] >= 0


def test_command_line(data_dir, capsys):
    predict.main(["pune", "--data-dir", str(data_dir), "--no-backtest"])
    out = capsys.readouterr().out
    assert "Forecast for" in out and "UV index" in out


def test_rain_backtest_only_learns_from_the_past(daily):
    from weather import rain_backtest, rain_scores, reliability

    frame = with_targets(daily)
    result = rain_backtest(frame, start_days=200, step_days=50)
    assert result.index.min() == frame.index[200]
    assert result["probability"].between(0, 1).all()
    assert set(result["rained"].unique()) <= {0, 1}
    s = rain_scores(result)
    assert 0 <= s["model_brier"] <= 1 and s["days"] == len(result)
    table = reliability(result)
    assert table["days"].sum() == len(result)


def test_rain_chance_is_a_probability(daily):
    from weather import rain_chance

    assert 0 <= rain_chance(daily) <= 1
