"""Next-day weather prediction for eight Indian cities."""
from .data import CITIES, load_city
from .model import TARGETS, backtest, forecast, scores, with_targets

__all__ = ["CITIES", "TARGETS", "load_city", "with_targets", "backtest", "scores", "forecast"]
__version__ = "1.0.1"
