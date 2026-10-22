"""The dashboard, run headless on the real data with Streamlit's test harness."""
import os

from streamlit.testing.v1 import AppTest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_dashboard_shows_a_forecast_and_its_track_record():
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=300).run()
    assert not at.exception
    labels = [m.label for m in at.metric]
    assert "Chance of rain" in labels and "Maximum temperature (°C)" in labels
    assert at.metric[labels.index("Chance of rain")].value.endswith("%")
    at.selectbox[0].set_value("jaipur").run()
    assert not at.exception
    assert any("Forecast for" in h.value for h in at.subheader)
