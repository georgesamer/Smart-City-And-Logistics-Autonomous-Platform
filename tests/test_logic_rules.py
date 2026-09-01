from models.map_graph import CityGridMap
from models.vehicle import Vehicle
from models.task import Task
from core.logic_rules import LogicEngine


def _plan_validated(grid, destination, is_hazard):
    city_map = CityGridMap(grid)
    vehicle = Vehicle("V1", (0, 0), battery_level=90.0, capacity=50.0)
    task = Task("T1", destination, priority=1, required_capacity=20.0)
    return LogicEngine(city_map).validate_action_plan(vehicle, task, [], 0.0, is_hazard=is_hazard)


def test_blocked_destination_is_hazard_zone_and_rejects_non_emergency():
    # 'X' cell (closed) -> hazard zone: normal vehicle rejected
    assert _plan_validated([[".", "X"], [".", "."]], (0, 1), is_hazard=True) is False


def test_accessible_traffic_destination_is_not_hazard_zone():
    # 'T' cell (traffic) -> available and not a hazard zone: plan accepted
    assert _plan_validated([[".", "T"], [".", "."]], (0, 1), is_hazard=False) is True


def test_hazard_derivation_matches_accessible_cell_state():
    city_map = CityGridMap([[".", "X"], [".", "T"]])
    # Same derivation used in main.py and dispatch_pipeline.py
    assert not city_map.is_valid_cell(0, 1)   # 'X' -> hazard zone
    assert city_map.is_valid_cell(1, 1)       # 'T' -> traversable
