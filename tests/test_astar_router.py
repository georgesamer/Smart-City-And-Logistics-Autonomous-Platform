from core.astar_router import AStarRouter
from core.csp_solver import CSPSolver
from models.vehicle import Vehicle
from models.task import Task


def test_astar_router_picks_cheaper_route():
    coords = {
        "Base": (30.00, 31.00),
        "A": (30.01, 31.00),
        "B": (30.02, 31.00),
        "Target": (30.05, 31.00),
    }
    graph = {
        "Base": {"A": 1.0, "B": 2.0},
        "A": {"Target": 5.0},
        "B": {"Target": 2.0},
        "Target": {},
    }

    path, cost = AStarRouter(graph=graph, coordinates=coords).find_path("Base", "Target")

    # Cheapest route: Base -> B (2.0) + B -> Target (2.0) = 4.0
    assert path == ["Base", "B", "Target"]
    assert abs(cost - 4.0) < 1e-9


def test_astar_router_handles_equal_cost_routes():
    nodes_coords = {
        "Base": (30.0444, 31.2357),
        "Point_A": (30.0500, 31.2400),
        "Point_B": (30.0600, 31.2500),
        "Target": (30.0700, 31.2600),
    }
    graph_data = {
        "Base": {"Point_A": 2.5, "Point_B": 5.0},
        "Point_A": {"Target": 4.0},
        "Point_B": {"Target": 1.5},
        "Target": {},
    }

    path, cost = AStarRouter(graph=graph_data, coordinates=nodes_coords).find_path("Base", "Target")

    # Both routes cost 6.5 (2.5+4.0 == 5.0+1.5) -> optimal path is valid and cost is correct
    assert path is not None
    assert path[0] == "Base" and path[-1] == "Target"
    assert abs(cost - 6.5) < 1e-9


def test_astar_router_returns_none_for_missing_nodes():
    router = AStarRouter({"A": {}, "B": {}}, {"A": (0.0, 0.0), "B": (1.0, 1.0)})

    assert router.find_path("A", "Missing") == (None, float("inf"))


def test_astar_router_returns_none_for_disconnected_goal():
    router = AStarRouter(
        {"A": {"B": 1.0}, "B": {}, "C": {}},
        {"A": (0.0, 0.0), "B": (0.01, 0.0), "C": (1.0, 1.0)},
    )

    assert router.find_path("A", "C") == (None, float("inf"))


def test_integration_routing_and_csp_dispatch():
    # 1) Geographic routing (AStarRouter)
    nodes_coords = {
        "Base": (30.0444, 31.2357),
        "Point_A": (30.0500, 31.2400),
        "Point_B": (30.0600, 31.2500),
        "Target": (30.0700, 31.2600),
    }
    graph_data = {
        "Base": {"Point_A": 2.5, "Point_B": 5.0},
        "Point_A": {"Target": 4.0},
        "Point_B": {"Target": 1.5},
        "Target": {},
    }

    path, cost = AStarRouter(graph=graph_data, coordinates=nodes_coords).find_path("Base", "Target")
    assert path is not None and cost < float("inf")

    # 2) Task assignment through CSP (type matching + capacity)
    vehicles = [
        Vehicle("V_Ambulance_1", (0, 0), battery_level=80.0, capacity=100.0, vehicle_type="medical"),
        Vehicle("V_Fire_1", (0, 1), battery_level=80.0, capacity=200.0, vehicle_type="fire"),
    ]
    tasks = [
        Task("Task_Rescue_1", (1, 0), priority=1, required_capacity=40.0, required_type="medical"),
        Task("Task_Fire_1", (1, 1), priority=1, required_capacity=150.0, required_type="fire"),
    ]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {"Task_Rescue_1": "V_Ambulance_1", "Task_Fire_1": "V_Fire_1"}
