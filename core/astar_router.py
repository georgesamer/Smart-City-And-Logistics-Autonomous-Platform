import heapq
import math
from typing import List, Tuple, Dict, Optional


class AStarRouter:
    """
    A* routing engine over a road graph:
    Works on nodes/edges with Lat/Lon coordinates and a Haversine heuristic.
    Used for geographic road-network modeling, while AStarPlanner works on a grid.
    """

    def __init__(self, graph: Dict[str, Dict[str, float]], coordinates: Dict[str, Tuple[float, float]]):
        """
        Note: coordinates must contain (lat, lon) for every graph node
        because the Haversine heuristic needs them for each explored node.
        """
        self.graph = graph  # Adjacency list with distances
        self.coordinates = coordinates  # Latitude/longitude for the heuristic

    def _haversine_distance(self, node1: str, node2: str) -> float:
        """Heuristic h(n): straight-line distance between nodes in kilometers."""
        lat1, lon1 = self.coordinates[node1]
        lat2, lon2 = self.coordinates[node2]

        R = 6371.0  # Earth's radius in kilometers
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        # max(0.0, 1 - a) avoids floating-point errors when a approaches 1
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return R * c

    def find_path(self, start: str, goal: str) -> Tuple[Optional[List[str]], float]:
        """
        Core A* algorithm: returns (optimal path, total cost).
        Returns (None, float('inf')) when no path exists.
        """
        if start not in self.graph or goal not in self.graph:
            return None, float('inf')

        open_set = []
        heapq.heappush(open_set, (0.0, start))

        came_from: Dict[str, str] = {}
        g_score: Dict[str, float] = {node: float('inf') for node in self.graph}
        g_score[start] = 0.0

        f_score: Dict[str, float] = {node: float('inf') for node in self.graph}
        f_score[start] = self._haversine_distance(start, goal)

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1], g_score[goal]

            for neighbor, weight in self.graph[current].items():
                tentative_g = g_score[current] + weight
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self._haversine_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None, float('inf')


if __name__ == "__main__":
    try:
        from core.csp_solver import CSPSolver
        from models.vehicle import Vehicle
        from models.task import Task
    except ModuleNotFoundError:
        # When run directly, add the project root to the path
        import os
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.csp_solver import CSPSolver
        from models.vehicle import Vehicle
        from models.task import Task


    # 1) Geographic routing test
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

    router = AStarRouter(graph=graph_data, coordinates=nodes_coords)
    path, cost = router.find_path("Base", "Target")
    print(f"Optimal Path: {path} with cost: {cost:.2f} km")

    # 2) CSP test (type matching + capacity)
    vehicles_data = [
        Vehicle("V_Ambulance_1", (0, 0), battery_level=80.0, capacity=100.0, vehicle_type="medical"),
        Vehicle("V_Fire_1", (0, 1), battery_level=80.0, capacity=200.0, vehicle_type="fire"),
    ]
    tasks_data = [
        Task("Task_Rescue_1", (1, 0), priority=1, required_capacity=40.0, required_type="medical"),
        Task("Task_Fire_1", (1, 1), priority=1, required_capacity=150.0, required_type="fire"),
    ]

    solver = CSPSolver(vehicles=vehicles_data, tasks=tasks_data)
    assignments = solver.solve_dispatch()
    print(f"CSP Task Assignments: {assignments}")
