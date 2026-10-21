# Changelog

What changed in each version of Weather Prediction.

The format follows [Keep a Changelog](https://keepachangelog.com), and the versions follow
[Semantic Versioning](https://semver.org).

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
