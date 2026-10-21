import pandas as pd
import pytest

from weather.data import load_city, read_hourly, to_daily


def test_bad_rows_are_dropped(data_dir):
    hourly = read_hourly(data_dir / "pune.csv")
    assert hourly.index.notna().all()
    assert not hourly.index.duplicated().any()
    assert len(hourly) == 3 * 365 * 24


def test_one_row_per_day(data_dir):
    daily = load_city("pune", data_dir)
    assert len(daily) == 3 * 365
    assert daily.index.is_unique and daily.index.is_monotonic_increasing


def test_daily_values_are_taken_once_and_rain_is_summed(data_dir):
    hourly = read_hourly(data_dir / "pune.csv")
    daily = to_daily(hourly)
    first = hourly.loc["2015-01-01"]
    assert daily.iloc[0]["maxtempc"] == first["maxtempc"].iloc[0]
    assert daily.iloc[0]["precipmm"] == pytest.approx(first["precipmm"].sum())
    assert daily.iloc[0]["uvindex_hourly_max"] == first["uvindex_hourly"].max()


def test_incomplete_days_are_left_out(data_dir):
    hourly = read_hourly(data_dir / "pune.csv")
    short = hourly[~((hourly.index.normalize() == pd.Timestamp("2015-02-01")) & (hourly.index.hour >= 10))]
    assert pd.Timestamp("2015-02-01") not in to_daily(short).index


def test_unknown_city(data_dir):
    with pytest.raises(ValueError):
        load_city("mumbai", data_dir)
