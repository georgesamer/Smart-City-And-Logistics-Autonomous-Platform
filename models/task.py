from typing import Tuple, List, Callable, Optional

class Task:
    def __init__(self, task_id: str, destination: Tuple[int, int], priority: int, required_capacity: float, constraints: Optional[List[Callable]] = None, required_type: str = "general"):
        self.task_id = task_id
        self.destination = destination
        self.priority = priority
        self.required_capacity = required_capacity
        self.required_type = required_type  # Required type: general / medical / fire ... (for CSP constraints)
        self.constraints = constraints or []