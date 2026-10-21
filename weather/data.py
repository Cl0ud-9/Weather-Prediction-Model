"""Load a city's hourly weather file and turn it into one row per day."""
from pathlib import Path

import numpy as np
import pandas as pd

CITIES = ["bengaluru", "bombay", "delhi", "hyderabad", "jaipur", "kanpur", "nagpur", "pune"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Values the source repeats on every hour of a day: take them once
DAILY = {"maxtempc": "maxtempc", "mintempc": "mintempc", "sunhour": "sunhour", "uvindex": "uvindex"}
# Hourly readings: average them over the day
HOURLY_MEAN = ["tempc", "dewpointc", "feelslikec", "heatindexc", "windchillc", "windgustkmph", "cloudcover",
               "humidity", "pressure", "visibility", "windspeedkmph"]
MIN_HOURS = 20  # a day with fewer readings than this is too incomplete to use


def read_hourly(path):
    """Read an hourly file, dropping rows whose time is missing or not a real date, and repeated hours."""
    raw = pd.read_csv(path)
    raw.columns = raw.columns.str.lower()
    # The file has two uvIndex columns: the day's value first, then the hourly reading
    raw = raw.rename(columns={"uvindex.1": "uvindex_hourly"})
    times = pd.to_datetime(raw.pop("date_time"), format="%m/%d/%Y %H:%M", errors="coerce")
    raw.index = times
    raw = raw[raw.index.notna()]
    return raw[~raw.index.duplicated(keep="first")].sort_index()


def to_daily(hourly):
    """One row per calendar day: daily values once, hourly readings averaged, rain summed."""
    days = hourly.index.normalize()
    grouped = hourly.groupby(days)
    daily = grouped[list(DAILY)].first()
    daily[HOURLY_MEAN] = grouped[HOURLY_MEAN].mean()
    daily["precipmm"] = grouped["precipmm"].sum()
    daily["uvindex_hourly_max"] = grouped["uvindex_hourly"].max()
    # Wind direction is an angle, so average it as a vector
    radians = np.deg2rad(hourly["winddirdegree"])
    daily["wind_dir_sin"] = np.sin(radians).groupby(days).mean()
    daily["wind_dir_cos"] = np.cos(radians).groupby(days).mean()
    daily = daily[grouped.size() >= MIN_HOURS]
    daily.index.name = "date"
    return daily


def load_city(city, data_dir=DATA_DIR):
    """Daily weather for one city."""
    if city not in CITIES:
        raise ValueError(f"unknown city {city!r}; choose one of {', '.join(CITIES)}")
    return to_daily(read_hourly(Path(data_dir) / f"{city}.csv"))
