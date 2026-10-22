"""Next-day weather prediction for eight Indian cities."""
from .data import CITIES, load_city
from .model import (
           RAIN_MM,
           TARGETS,
           backtest,
           forecast,
           rain_backtest,
           rain_chance,
           rain_scores,
           reliability,
           scores,
           with_targets,
)

__all__ = ["CITIES", "TARGETS", "RAIN_MM", "load_city", "with_targets", "backtest", "scores", "forecast",
           "rain_backtest", "rain_scores", "reliability", "rain_chance"]
__version__ = "1.1.0"
