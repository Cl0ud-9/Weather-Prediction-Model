# Changelog

What changed in each version of Weather Prediction.

The format follows [Keep a Changelog](https://keepachangelog.com), and the versions follow
[Semantic Versioning](https://semver.org).

## [1.1.0] - 2026-10-22

### Added

- Chance of rain: logistic regression on the same features forecasts whether tomorrow brings more than 1 mm. Scored
  by the Brier score in a walk-forward backtest, it beats "rain if it rained today" and the month's usual share of
  rainy days in all eight cities, and its chances are well calibrated (in Pune, 70% meant rain on 75% of days).
  `predict.py` shows it, and `predict.py all` prints the comparison for every city.
- A dashboard, `streamlit run app.py`: a city's forecast with each number's typical error, the model's past forecasts
  against what happened, and how often it rained at each chance. Ready for Streamlit Community Cloud.

### Changed

- The README reports an experiment that did not help: adding the other cities' weather made forecasts slightly worse.

## [1.0.1] - 2026-10-22

### Changed

- Python 3.14 is supported: the tests pass on it, and continuous integration now runs on Python 3.11 to 3.14.

## [1.0.0] - 2026-10-21

The first complete version: a tested forecasting package and command line, with results measured honestly.

### Added

- `weather` package and `predict.py`: forecast the next day's maximum and minimum temperature, rain and UV index for
  any of the eight cities, and print the model's backtested error next to the "same as today" baseline.
- Recent history and time of year as features.
- Tests, continuous integration, and the license, notice, contributing, conduct and security files.

### Fixed

- The notebook predicted the next hourly row, one hour ahead, and three of its four targets are daily values repeated
  on every hourly row, so its reported accuracy was inflated. The data is now turned into one row per day and each
  day is paired with the next calendar day.
- Rows with no time, a day dated 29 February 2023 and repeated hours are dropped when a file is loaded.

### Changed

- The city files moved to `data/`, and the original notebook to `notebooks/original_notebook.ipynb`.

## Before 1.0.0

The repository held the notebook and the city files, published on 2024-04-02.
