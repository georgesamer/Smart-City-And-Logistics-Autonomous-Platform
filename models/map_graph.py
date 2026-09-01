from typing import Tuple, List, Dict

class CityGridMap:
    def __init__(self, grid: List[List[str]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def is_valid_cell(self, r: int, c: int) -> bool:
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] != 'X'

    def get_cell_cost(self, r: int, c: int) -> float:
        val = self.grid[r][c]
        if val == 'T':  # Traffic Jam
            return 3.0
        elif val in ('.', 'S', 'G', 'V'):
            return 1.0
        return float('inf')

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[Tuple[int, int], float]]:
        r, c = pos
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_valid_cell(nr, nc):
                cost = self.get_cell_cost(nr, nc)
                neighbors.append(((nr, nc), cost))
        return neighbors