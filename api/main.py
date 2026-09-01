"""
FastAPI layer: connect all integrated engines through one RESTful interface.

Usage:
    python -m api.main
    Or: uvicorn api.main:app --reload --port 8000
"""
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.map_config import DEFAULT_GRID_MAP
from core.bayesian_risk_estimator import BayesianRiskEstimator
from models.map_graph import CityGridMap
from models.vehicle import Vehicle
from perception.incident_nlp_processor import (
    IncidentNLPProcessor,
    ml_dependencies_available as nlp_ml_available,
)
from perception.nlp_engine import NLPEngine
from pipelines.dispatch_pipeline import DispatchPipeline

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Smart Logistics & Emergency Dispatch Platform",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Engines that are always available (pure Python, no heavy dependencies)
risk_engine = BayesianRiskEstimator()
nlp_engine = NLPEngine()

# Optional ML engine: lazy initialization on first use —
# missing dependencies do not prevent the server from running, and the model (~250MB) is not loaded on import.
_ml_nlp_processor = None
_ml_nlp_processor_attempted = False


def _get_ml_nlp_processor():
    """Return the ML engine with lazy initialization (loaded only for the first request that needs it)."""
    global _ml_nlp_processor, _ml_nlp_processor_attempted
    if _ml_nlp_processor_attempted:
        return _ml_nlp_processor
    _ml_nlp_processor_attempted = True
    if nlp_ml_available():
        try:
            _ml_nlp_processor = IncidentNLPProcessor()
        except Exception as exc:
            print(f"[API] Could not load the ML engine: {exc}")
            _ml_nlp_processor = None
    return _ml_nlp_processor


class AnalyzeReportRequest(BaseModel):
    report: str
    incident_id: str = "API_INC_001"


class AssessRiskRequest(BaseModel):
    weather_severe: bool
    traffic_heavy: bool


class DispatchRequest(BaseModel):
    report: str
    incident_id: str = "API_INC_001"
    camera_image_mock: str = "camera_feed_accident_block.png"
    current_hour: int = 14


@app.get("/")
def read_root() -> Dict[str, Any]:
    return {
        "status": "Active",
        "system": "Autonomous Dispatch Engine Core",
        "ml_engines_available": nlp_ml_available(),
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index_enhanced.html")


@app.post("/api/v1/analyze-report")
def analyze_report(req: AnalyzeReportRequest) -> Dict[str, Any]:
    """
    Parse a text report through the integrated NLP engine: extract location/priority/capacity (always available).
    Note: when ML dependencies are available, an additional severity classification (ml_severity) is added.
    """
    incident = nlp_engine.parse_report_to_incident(req.incident_id, req.report)
    result = incident.to_dict()
    ml = _get_ml_nlp_processor()
    if ml is not None:
        result["ml_severity"] = ml.analyze_report(req.report)
    return {"status": "success", "data": result}


@app.post("/api/v1/assess-risk")
def assess_risk(req: AssessRiskRequest) -> Dict[str, Any]:
    """Evaluate delay risk through the Bayesian engine (conditional probability table, CPT)."""
    result = risk_engine.predict_delay_probability(req.weather_severe, req.traffic_heavy)
    return {"status": "success", "data": result}


@app.post("/api/v1/dispatch")
def dispatch(req: DispatchRequest) -> Dict[str, Any]:
    """
    Execute the complete pipeline:
    NLP -> Vision -> Bayesian -> CSP -> Pathfinding (A*) -> Logic Rules -> RL Rebalancing.
    """
    city_map = CityGridMap([row[:] for row in DEFAULT_GRID_MAP])
    vehicles = [
        Vehicle(vehicle_id="V1", location=(3, 0), battery_level=90.0, capacity=100.0),
        Vehicle(vehicle_id="V2", location=(3, 4), battery_level=80.0, capacity=50.0),
    ]
    pipeline = DispatchPipeline(city_map, vehicles)
    result = pipeline.run_pipeline(
        incident_id=req.incident_id,
        raw_text_report=req.report,
        camera_image_mock=req.camera_image_mock,
        current_hour=req.current_hour,
    )
    return {"status": "success", "data": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
