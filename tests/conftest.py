import numpy as np
import pandas as pd
import pytest

COLUMNS = ["date_time", "maxtempC", "mintempC", "totalSnow_cm", "sunHour", "uvIndex", "uvIndex", "DewPointC",
           "FeelsLikeC", "HeatIndexC", "WindChillC", "WindGustKmph", "cloudcover", "humidity", "precipMM",
           "pressure", "tempC", "visibility", "winddirDegree", "windspeedKmph"]


def hourly_rows(days, start="2015-01-01", seed=0):
    """Hourly rows in the source's format: daily values repeated each hour, one header with uvIndex twice."""
    rng = np.random.default_rng(seed)
    rows = []
    for d in pd.date_range(start, periods=days, freq="D"):
        season = np.sin(2 * np.pi * d.dayofyear / 365.25)
        tmax, tmin = 30 + 5 * season + rng.normal(), 20 + 4 * season + rng.normal()
        uv = int(5 + 2 * season)
        for h in range(24):
            uv_now = uv if 8 < h < 17 else 1
            rain = 0.1 if h < 3 else 0.0
            rows.append([f"{d.month}/{d.day}/{d.year} {h}:00", round(tmax), round(tmin), 0, 11, uv, uv_now,
                         15, 25, 26, 24, 10, 20, 60, rain, 1012, (tmin + tmax) / 2, 10, 90, 5])
    return rows


@pytest.fixture
def data_dir(tmp_path):
    """A data folder holding a three-year 'pune.csv' with the source's quirks."""
    rows = hourly_rows(3 * 365)
    rows.insert(5, [""] * len(COLUMNS))                                   # an empty row
    rows.insert(10, list(rows[9]))                                        # a repeated hour
    rows.append(["2/29/2023  12:00:00 AM"] + rows[0][1:])                 # a date that does not exist
    lines = [",".join(COLUMNS)] + [",".join(str(v) for v in r) for r in rows]
    (tmp_path / "pune.csv").write_text("\n".join(lines) + "\n")
    return tmp_path
