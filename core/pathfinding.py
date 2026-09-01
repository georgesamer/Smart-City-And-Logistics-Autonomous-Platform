import heapq
from collections import deque
from typing import Tuple, List, Dict
from models.map_graph import CityGridMap

class AStarPlanner:
    def __init__(self, city_map: CityGridMap):
        self.city_map = city_map

    def Manhattan_heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_accessible_target(self, goal: Tuple[int, int]) -> Tuple[int, int]:
        """
        If the target cell is closed ('X'), find the nearest traversable neighboring
        cell to reach the incident location without entering the blocked cell.
        Note: "nearest" is measured in steps (grid distance), not traversal cost.
        """
        if self.city_map.is_valid_cell(*goal):
            return goal

        rows, cols = self.city_map.rows, self.city_map.cols
        visited = {goal}
        queue = deque([goal])
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        # BFS outward from the target to find the nearest valid cell (even if surrounded by 'X')
        while queue:
            r, c = queue.popleft()
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    if self.city_map.is_valid_cell(nr, nc):
                        print(f"[Pathfinder] Destination {goal} is blocked 'X'. "
                              f"Rerouting to nearest accessible cell: {(nr, nc)}")
                        return (nr, nc)
                    queue.append((nr, nc))

        # Target is completely isolated from the valid grid; return it so search fails safely
        return goal

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], float]:
        actual_goal = self._get_accessible_target(goal)

        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        while open_set:
            current = heapq.heappop(open_set)[1]

            if current == actual_goal:
                path = []
                curr = current
                while curr in came_from:
                    path.append(curr)
                    curr = came_from[curr]
                path.append(start)
                return path[::-1], g_score[actual_goal]

            for neighbor, cost in self.city_map.get_neighbors(current):
                tentative_g = g_score[current] + cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.Manhattan_heuristic(neighbor, actual_goal)
                    heapq.heappush(open_set, (f_score, neighbor))

        return [], float('inf')