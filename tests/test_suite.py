"""
Comprehensive suite for all project engines:
routing, assignment, perception (optional ML), and probability/learning.
"""
import pytest

from core.astar_router import AStarRouter
from core.bayesian_risk_estimator import BayesianRiskEstimator
from core.csp_solver import CSPSolver
from core.qlearning_dispatcher import QLearningDispatcher
from models.task import Task
from models.vehicle import Vehicle

# --- 1. Routing and assignment engines ---


def test_astar_router():
    nodes_coords = {"A": (30.0, 31.0), "B": (30.1, 31.1)}
    graph = {"A": {"B": 5.0}, "B": {}}
    router = AStarRouter(graph=graph, coordinates=nodes_coords)

    path, cost = router.find_path("A", "B")

    assert path == ["A", "B"]
    assert cost == 5.0


def test_csp_solver():
    vehicles = [Vehicle("V1", (0, 0), battery_level=80.0, capacity=100.0, vehicle_type="medical")]
    tasks = [Task("T1", (1, 0), priority=1, required_capacity=50.0, required_type="medical")]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {"T1": "V1"}


# --- 2. Perception engines (optional; skipped when ML dependencies are absent) ---


def test_nlp_processor():
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from perception.incident_nlp_processor import IncidentNLPProcessor

    nlp = IncidentNLPProcessor()
    res = nlp.analyze_report("Car accident on main road")

    assert "predicted_severity" in res
    assert "confidence" in res


def test_vision_detector():
    torch = pytest.importorskip("torch")
    pytest.importorskip("torchvision")
    from perception.hazard_vision_detector import HazardVisionDetector

    vision = HazardVisionDetector()
    dummy_tensor = torch.randn(1, 3, 224, 224)
    vision.eval()
    with torch.no_grad():
        out = vision(dummy_tensor)

    assert out.shape == (1, 4)


# --- 3. Advanced engines (pure Python) ---


def test_bayesian_risk():
    bayes = BayesianRiskEstimator()
    res = bayes.predict_delay_probability(True, True)

    assert res["risk_level"] == "High"


def test_q_learning():
    ql = QLearningDispatcher(num_states=3, num_actions=2)
    train_res = ql.train_simulation(episodes=10)

    assert train_res["status"] == "Training Completed"
    assert len(ql.q_table) == 3 and all(len(row) == 2 for row in ql.q_table)
