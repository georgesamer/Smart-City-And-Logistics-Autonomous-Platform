from typing import Dict, Tuple

# Default map dimensions (Rows, Cols)
GRID_SHAPE: Tuple[int, int] = (4, 5)

# Movement costs by cell type for A* pathfinding
CELL_COSTS: Dict[str, float] = {
    '.': 1.0,   # Normal road
    'T': 3.0,   # Visibly busy road or high delay probability
    'X': float('inf'), # Closed road / fire / obstacle
    'G': 1.0,   # Goal
    'V': 1.0    # Vehicle location
}

# Registry mapping known location names to map coordinates (NLP location registry)
DEFAULT_LOCATION_REGISTRY: Dict[str, Tuple[int, int]] = {
    "hospital": (0, 4),
    "main intersection": (1, 1),
    "station": (2, 3),
    "warehouse": (0, 0),
    "zone B": (3, 4)
}

# Default map used at startup
DEFAULT_GRID_MAP = [
    ['.', '.', '.', '.', 'G'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', 'T', '.'],
    ['V1', '.', 'X', '.', 'V2']
]