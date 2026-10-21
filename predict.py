"""Forecast tomorrow's weather for a city, and show how accurate the model has been."""
import argparse

from weather import CITIES, TARGETS, backtest, forecast, load_city, scores, with_targets
from weather.data import DATA_DIR


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("city", choices=CITIES + ["all"], help="a city, or 'all' for the accuracy table only")
    parser.add_argument("--data-dir", default=DATA_DIR, help="folder with the city CSV files")
    parser.add_argument("--no-backtest", action="store_true", help="skip the accuracy check")
    args = parser.parse_args(argv)

    if args.city == "all":
        print(f"{'city':10} " + " ".join(f"{t:>20}" for t in TARGETS))
        for city in CITIES:
            frame = with_targets(load_city(city, args.data_dir))
            cells = []
            for t in TARGETS:
                s = scores(backtest(frame, t))
                cells.append(f"{s['model_mae']:7.2f} vs {s['persistence_mae']:7.2f}")
            print(f"{city:10} " + " ".join(f"{c:>20}" for c in cells))
        print("\nMean absolute error of the model vs 'tomorrow will be like today'.")
        return

    daily = load_city(args.city, args.data_dir)
    day, values = forecast(daily)
    print(f"{args.city.title()}: data runs to {daily.index[-1]:%d %b %Y}. Forecast for {day:%d %b %Y}:")
    for t, label in TARGETS.items():
        print(f"  {label:26} {values[t]:6.1f}")
    if not args.no_backtest:
        frame = with_targets(daily)
        print("\nMean absolute error over past days (model vs 'tomorrow will be like today'):")
        for t, label in TARGETS.items():
            s = scores(backtest(frame, t))
            print(f"  {label:26} {s['model_mae']:6.2f} vs {s['persistence_mae']:6.2f}   ({s['days']} days)")


if __name__ == "__main__":
    main()
