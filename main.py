"""Command-line entry point for the complete autonomous dispatch system."""

import argparse
import sys
from typing import Any, Dict

from config.map_config import DEFAULT_GRID_MAP
from core.bayesian_risk_estimator import BayesianRiskEstimator
from core.qlearning_dispatcher import QLearningDispatcher
from models.map_graph import CityGridMap
from models.vehicle import Vehicle
from pipelines.dispatch_pipeline import DispatchPipeline


DEFAULT_REPORT = (
    "Urgent emergency report: a leak incident near (0, 4) "
    "requires support with a capacity of 30 units"
)


def run_system(
    report: str = DEFAULT_REPORT,
    incident_id: str = "INC_001",
    camera_image: str = "camera_feed_accident_block.png",
    current_hour: int = 14,
    training_episodes: int = 50,
) -> Dict[str, Any]:
    """Run perception, risk analysis, dispatch, routing, safety, and learning."""
    city_map = CityGridMap([row[:] for row in DEFAULT_GRID_MAP])
    vehicles = [
        Vehicle(
            vehicle_id="V1",
            location=(3, 0),
            battery_level=90.0,
            capacity=100.0,
        ),
        Vehicle(
            vehicle_id="V2",
            location=(3, 4),
            battery_level=80.0,
            capacity=50.0,
        ),
    ]

    pipeline = DispatchPipeline(city_map, vehicles)
    dispatch_result = pipeline.run_pipeline(
        incident_id=incident_id,
        raw_text_report=report,
        camera_image_mock=camera_image,
        current_hour=current_hour,
    )

    risk_result = BayesianRiskEstimator().predict_delay_probability(
        weather_severe=False,
        traffic_heavy=True,
    )

    qlearning = QLearningDispatcher(num_states=4, num_actions=3)
    learning_result = qlearning.train_simulation(episodes=training_episodes)

    result = {
        "dispatch": dispatch_result,
        "risk": risk_result,
        "learning": learning_result,
    }
    print(f"\n[Bayesian Risk Estimator] {risk_result}")
    print(f"[Q-Learning Dispatcher] {learning_result}")
    return result


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the complete smart-city logistics dispatch demo."
    )
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--incident-id", default="INC_001")
    parser.add_argument("--camera-image", default="camera_feed_accident_block.png")
    parser.add_argument("--hour", type=int, default=14)
    parser.add_argument("--training-episodes", type=int, default=50)
    return parser.parse_args()


def main() -> Dict[str, Any]:
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")

    args = _parse_args()
    return run_system(
        report=args.report,
        incident_id=args.incident_id,
        camera_image=args.camera_image,
        current_hour=args.hour,
        training_episodes=args.training_episodes,
    )


if __name__ == "__main__":
    main()
