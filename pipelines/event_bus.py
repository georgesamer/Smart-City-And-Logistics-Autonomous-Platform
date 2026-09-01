from typing import Callable, Dict, List, Any
from enum import Enum

class EventType(Enum):
    INCIDENT_REPORTED = "INCIDENT_REPORTED"    # Text report received
    INCIDENT_VERIFIED = "INCIDENT_VERIFIED"    # Verified visually
    TASK_ASSIGNED = "TASK_ASSIGNED"            # Task assigned through CSP
    SAFETY_VIOLATION = "SAFETY_VIOLATION"      # Plan rejected by the logic engine
    REBALANCE_TRIGGERED = "REBALANCE_TRIGGERED" # Fleet rebalancing through RL

class EventBus:
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Any], None]]] = {
            event_type: [] for event_type in EventType
        }

    def subscribe(self, event_type: EventType, callback: Callable[[Any], None]):
        """Register a handler for a specific event."""
        self._subscribers[event_type].append(callback)

    def publish(self, event_type: EventType, data: Any):
        """Emit an event and notify all listeners."""
        print(f"\n[EventBus] Event Published: {event_type.value}")
        for callback in self._subscribers[event_type]:
            callback(data)