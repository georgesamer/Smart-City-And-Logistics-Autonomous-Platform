from core.csp_solver import CSPSolver
from models.task import Task
from models.vehicle import Vehicle


def test_dispatch_prioritizes_tasks_and_respects_capacity():
    vehicles = [
        Vehicle("small", (0, 0), battery_level=80.0, capacity=10.0),
        Vehicle("large", (0, 1), battery_level=80.0, capacity=50.0),
    ]
    tasks = [
        Task("normal", (1, 1), priority=3, required_capacity=10.0),
        Task("urgent", (1, 0), priority=1, required_capacity=40.0),
    ]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {"urgent": "large", "normal": "small"}


def test_dispatch_applies_custom_constraints():
    vehicle = Vehicle("V1", (0, 0), battery_level=80.0, capacity=50.0)
    task = Task(
        "restricted",
        (1, 1),
        priority=1,
        required_capacity=20.0,
        constraints=[lambda candidate, _: candidate.id == "allowed"],
    )

    assert CSPSolver([vehicle], [task]).solve_dispatch() == {}


def test_dispatch_assigns_multiple_tasks_with_cumulative_loads():
    # One vehicle handles two tasks: cumulative load 20+20 <= 50
    vehicles = [Vehicle("V1", (0, 0), battery_level=80.0, capacity=50.0)]
    tasks = [
        Task("urgent", (1, 0), priority=1, required_capacity=20.0),
        Task("normal", (1, 1), priority=3, required_capacity=20.0),
    ]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {"urgent": "V1", "normal": "V1"}


def test_dispatch_does_not_drop_urgent_task_for_normal_task():
    # Both tasks cannot fit (30+30 > 50) -> the urgent task must not be sacrificed for the normal one
    vehicles = [Vehicle("V1", (0, 0), battery_level=80.0, capacity=50.0)]
    tasks = [
        Task("urgent", (1, 0), priority=1, required_capacity=30.0),
        Task("normal", (1, 1), priority=3, required_capacity=30.0),
    ]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {}


def test_dispatch_enforces_vehicle_type_match():
    vehicles = [
        Vehicle("V_amb", (0, 0), battery_level=80.0, capacity=100.0, vehicle_type="medical"),
        Vehicle("V_fire", (0, 1), battery_level=80.0, capacity=200.0, vehicle_type="fire"),
    ]
    tasks = [
        Task("fire_task", (1, 1), priority=1, required_capacity=150.0, required_type="fire"),
        Task("med_task", (1, 0), priority=1, required_capacity=40.0, required_type="medical"),
    ]

    assignments = CSPSolver(vehicles, tasks).solve_dispatch()

    assert assignments == {"fire_task": "V_fire", "med_task": "V_amb"}


def test_dispatch_rejects_type_mismatch():
    # Only a medical vehicle plus a fire task -> no solution (type mismatch rejected)
    vehicles = [Vehicle("V_amb", (0, 0), battery_level=80.0, capacity=200.0, vehicle_type="medical")]
    tasks = [Task("fire_task", (1, 1), priority=1, required_capacity=50.0, required_type="fire")]

    assert CSPSolver(vehicles, tasks).solve_dispatch() == {}


def test_dispatch_serves_general_task_with_specialized_vehicle():
    # General tasks can be served by any specialized vehicle
    vehicles = [Vehicle("V_amb", (0, 0), battery_level=80.0, capacity=200.0, vehicle_type="medical")]
    tasks = [Task("general_task", (1, 0), priority=1, required_capacity=50.0, required_type="general")]

    assert CSPSolver(vehicles, tasks).solve_dispatch() == {"general_task": "V_amb"}