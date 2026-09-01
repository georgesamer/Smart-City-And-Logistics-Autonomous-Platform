from typing import List, Dict, Callable, Optional
from models.vehicle import Vehicle
from models.task import Task

class CSPSolver:
    def __init__(self, vehicles: List[Vehicle], tasks: List[Task]):
        self.vehicles = vehicles
        self.tasks = tasks

    def is_consistent(self, vehicle: Vehicle, task: Task, current_load: float = 0.0) -> bool:
        # Capacity constraint: remaining capacity after the vehicle's existing tasks
        if current_load + task.required_capacity > vehicle.capacity:
            return False

        # Type-matching constraint: any vehicle can serve general tasks,
        # while specialized tasks require an exact type match
        if task.required_type != "general" and vehicle.vehicle_type != task.required_type:
            return False

        # Task-specific constraints
        for constraint in task.constraints:
            if not constraint(vehicle, task):
                return False
        return True

    def solve(self) -> Optional[Dict[str, str]]:
        """
        Backtracking CSP for optimal assignment:
        - Priority order: priority=1 means highest importance -> handled first
        - Cumulative load: a vehicle may handle multiple tasks within its capacity
        - Type matching (vehicle_type == required_type)
        - Task-specific constraints
        """
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority)
        loads = {v.id: 0.0 for v in self.vehicles}
        assignments: Dict[str, str] = {}

        def backtrack(task_index: int) -> bool:
            if task_index == len(sorted_tasks):
                return True  # All tasks assigned successfully

            current_task = sorted_tasks[task_index]

            for vehicle in self.vehicles:
                if self.is_consistent(vehicle, current_task, loads[vehicle.id]):
                    # Assign the task
                    assignments[current_task.task_id] = vehicle.id
                    loads[vehicle.id] += current_task.required_capacity

                    # Recurse into the remaining tasks
                    if backtrack(task_index + 1):
                        return True

                    # Backtrack the assignment
                    del assignments[current_task.task_id]
                    loads[vehicle.id] -= current_task.required_capacity

            return False

        if backtrack(0):
            return assignments
        return None

    def solve_dispatch(self) -> Dict[str, str]:
        """
        Compatibility interface for the pipeline:
        Returns a task_id -> vehicle_id map. All-or-nothing: if any task
        cannot be assigned, return an empty map (no partial assignment).
        """
        result = self.solve()
        return result if result is not None else {}