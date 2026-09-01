from enum import Enum
from typing import Tuple

class VehicleStatus(Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    CHARGING = "CHARGING"

class Vehicle:
    def __init__(self, vehicle_id: str, location: Tuple[int, int], battery_level: float, capacity: float, vehicle_type: str = "general"):
        self.id = vehicle_id
        self.location = location
        self.battery_level = battery_level
        self.capacity = capacity
        self.vehicle_type = vehicle_type  # Vehicle type: general / medical / fire ... (for CSP constraints)
        self.status = VehicleStatus.IDLE

    def update_location(self, new_loc: Tuple[int, int]) -> None:
        self.location = new_loc

    def assign_task(self) -> None:
        self.status = VehicleStatus.BUSY

    def release(self) -> None:
        self.status = VehicleStatus.IDLE