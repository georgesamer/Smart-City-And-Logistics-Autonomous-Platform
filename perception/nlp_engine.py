import re
from typing import Tuple, Dict, Any, Optional
from models.incident import Incident, IncidentStatus
from models.task import Task

class NLPEngine:
    def __init__(self, map_location_registry: Optional[Dict[str, Tuple[int, int]]] = None):
        # Simple registry mapping landmark names to map coordinates
        self.location_registry = map_location_registry or {
            "hospital": (0, 4),
            "main intersection": (1, 1),
            "station": (2, 3),
            "warehouse": (0, 0),
            "zone B": (3, 4)
        }

    def _extract_priority(self, text: str) -> int:
        """Extract task priority from keywords."""
        high_priority_words = ["urgent", "emergency", "incident", "ambulance", "dangerous", "fire"]
        medium_priority_words = ["fast", "important", "traffic"]
        normalized_text = text.lower()
        
        for word in high_priority_words:
            if word in normalized_text:
                return 1  # Highest priority
        for word in medium_priority_words:
            if word in normalized_text:
                return 2  # Medium priority
        return 3      # Normal priority

    def _extract_destination(self, text: str) -> Tuple[int, int]:
        """Extract the destination or specified location from the text."""
        for loc_name, coords in self.location_registry.items():
            if loc_name in text:
                return coords
        
        # Look for direct coordinates such as (0, 4) or [0, 4]
        coords_match = re.search(r'\(?\s*(\d+)\s*,\s*(\d+)\s*\)?', text)
        if coords_match:
            return (int(coords_match.group(1)), int(coords_match.group(2)))
            
        # Default when no location is specified
        return (0, 0)

    def _extract_capacity(self, text: str) -> float:
        """Extract the requested transport size/capacity, if present."""
        capacity_match = re.search(r'(\d+)\s*(ton|kilo|capacity|unit)s?', text, re.IGNORECASE)
        if capacity_match:
            return float(capacity_match.group(1))
        return 20.0  # Default for emergency tasks

    def parse_report_to_task(self, task_id: str, report_text: str) -> Task:
        """Parse raw text and return a Task ready for the CSP engine."""
        priority = self._extract_priority(report_text)
        destination = self._extract_destination(report_text)
        required_capacity = self._extract_capacity(report_text)

        print(f"\n[NLP Engine] Parsing Report: '{report_text}'")
        print(f" └─ extracted -> Priority: {priority}, Target: {destination}, Required Capacity: {required_capacity}")

        return Task(
            task_id=task_id,
            destination=destination,
            priority=priority,
            required_capacity=required_capacity
        )

    def parse_report_to_incident(self, incident_id: str, report_text: str) -> Incident:
        """Parse raw text and return an Incident."""
        priority = self._extract_priority(report_text)
        destination = self._extract_destination(report_text)
        capacity = self._extract_capacity(report_text)

        return Incident(
            incident_id=incident_id,
            raw_text=report_text,
            location=destination,
            severity_priority=priority,
            required_capacity=capacity
        )

    def create_task_from_incident(self, incident: Incident) -> Task:
        """Convert the verified Incident into a Task for the CSP engine."""
        return Task(
            task_id=f"TASK_{incident.incident_id}",
            destination=incident.location,
            priority=incident.severity_priority,
            required_capacity=incident.required_capacity
        )