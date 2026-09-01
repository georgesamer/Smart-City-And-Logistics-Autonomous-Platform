from typing import Tuple, Dict, Any, List
from models.vehicle import Vehicle
from models.task import Task
from models.map_graph import CityGridMap
from config.settings import settings

class SafetyViolationException(Exception):
    """Exception raised when any safety or logic rule is violated."""
    pass

class LogicEngine:
    def __init__(self, city_map: CityGridMap):
        self.city_map = city_map

    def check_battery_distance_rule(self, vehicle: Vehicle, path_length: float) -> bool:
        required_battery = path_length * settings.BATTERY_DRAIN_PER_UNIT * settings.SAFETY_BATTERY_BUFFER
        if vehicle.battery_level < required_battery:
            print(f"[Logic Check] Battery insufficient: {vehicle.battery_level}% < {required_battery}% required.")
            return False
        return True

    def check_zone_entry_permissions(self, vehicle: Vehicle, destination: Tuple[int, int], is_hazard_zone: bool) -> bool:
        """
        Hazard-zone safety rule:
        Normal vehicles may not pass through incident or leak zones; reserve them for rescue vehicles.
        """
        if is_hazard_zone and not getattr(vehicle, 'is_emergency_vehicle', False):
            print(f"[Logic Check] RULE VIOLATION: Non-emergency vehicle {vehicle.id} prohibited from entering hazard zone {destination}.")
            return False
        return True

    def validate_action_plan(self, vehicle: Vehicle, task: Task, path: List[Tuple[int, int]], path_cost: float, is_hazard: bool = False) -> bool:
        """
        Model Checking Interface:
        Validate the complete action plan against all logic rules before approval.
        """
        print(f"\n[Logic Engine] Executing Model Checking on Proposed Action Plan for Vehicle {vehicle.id}...")
        
        # 1. Validate battery distance
        if not self.check_battery_distance_rule(vehicle, path_cost):
            return False

        # 2. Validate hazardous-zone permissions
        if not self.check_zone_entry_permissions(vehicle, task.destination, is_hazard):
            return False

        print(f" └─ ALL SAFETY & LOGIC RULES PASSED for Vehicle {vehicle.id}.")
        return True