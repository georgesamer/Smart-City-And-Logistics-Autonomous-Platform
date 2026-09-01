"""Interactive dashboard tests (Streamlit AppTest) — run without a browser."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

# AppTest resolves paths relative to the calling file -> use an absolute app.py path
APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _make_app() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=60)


def test_dashboard_initial_render_with_dummy_data():
    at = _make_app()
    at.run()

    assert not at.exception
    assert len(at.tabs) == 3
    assert len(at.button) == 1


def test_dashboard_run_pipeline_button():
    at = _make_app()
    at.run()
    at.button[0].click()
    at.run()

    assert not at.exception
    # After running: display the real pipeline result (not dummy data)
    status_metrics = [m for m in at.metric if m.label == "Pipeline Status"]
    assert status_metrics and status_metrics[0].value == "SUCCESS"
    # Real Bayesian output (default Clear/Light conditions -> Low)
    risk_metrics = [m for m in at.metric if m.label == "Risk Level"]
    assert risk_metrics and risk_metrics[0].value in ("Low", "Medium", "High")
    assert len(at.dataframe) >= 3  # CSP, fleet, and Q-table tables
