from models.map_graph import CityGridMap
from core.pathfinding import AStarPlanner


def test_astar_finds_low_cost_path_around_obstacle():
    city_map = CityGridMap(
        [
            [".", ".", "."],
            ["X", "X", "."],
            [".", ".", "."],
        ]
    )

    path, cost = AStarPlanner(city_map).find_path((0, 0), (2, 2))

    assert path == [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
    assert cost == 4.0


def test_astar_returns_no_path_for_unreachable_goal():
    city_map = CityGridMap(
        [
            [".", "X"],
            ["X", "."],
        ]
    )

    path, cost = AStarPlanner(city_map).find_path((0, 0), (1, 1))

    assert path == []
    assert cost == float("inf")


def test_astar_reroutes_to_nearest_accessible_cell_when_goal_blocked():
    # Target (1, 1) is closed 'X' -> redirect to the nearest valid neighboring cell
    city_map = CityGridMap(
        [
            [".", ".", "."],
            [".", "X", "X"],
            [".", ".", "."],
        ]
    )

    path, cost = AStarPlanner(city_map).find_path((0, 0), (1, 1))

    assert path
    assert cost != float("inf")
    assert path[-1] != (1, 1)                   # The vehicle must not stop in the blocked cell
    assert city_map.is_valid_cell(*path[-1])    # The final destination is traversable


def test_astar_reroutes_through_blocked_ring_to_accessible_cell():
    # Target (1, 1) is fully surrounded by 'X' -> BFS finds the nearest valid cell one step farther
    city_map = CityGridMap(
        [
            ["X", "X", "X"],
            ["X", "X", "."],
            [".", ".", "."],
        ]
    )

    path, cost = AStarPlanner(city_map).find_path((2, 0), (1, 1))

    assert path
    assert cost != float("inf")
    assert path[-1] == (2, 1)