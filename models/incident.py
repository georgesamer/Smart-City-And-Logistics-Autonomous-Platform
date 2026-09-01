from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class IncidentStatus(Enum):
    REPORTED = "REPORTED"          # Report received as text
    VERIFIED = "VERIFIED"          # Verified visually through the camera
    DISPATCHED = "DISPATCHED"      # Vehicle dispatched to its location
    REJECTED = "REJECTED"          # Report rejected (false or unverified)
    RESOLVED = "RESOLVED"          # Problem resolved successfully


@dataclass
class Incident:
    incident_id: str
    raw_text: str                                # Raw report text from NLP
    location: Tuple[int, int]                    # Incident location on the map (r, c)
    severity_priority: int = 3                   # Priority (1: highest, 2: medium, 3: normal)
    required_capacity: float = 0.0               # Required capacity or support
    
    # Vision engine data
    verified_by_vision: bool = False
    confidence_score: float = 0.0
    camera_image_ref: Optional[str] = None
    
    # Status and creation timestamp
    status: IncidentStatus = IncidentStatus.REPORTED
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def mark_verified(self, confidence: float, image_ref: Optional[str] = None):
        """Update the report status after visual verification."""
        self.verified_by_vision = True
        self.confidence_score = confidence
        self.camera_image_ref = image_ref
        self.status = IncidentStatus.VERIFIED

    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for API or JSON serialization."""
        return {
            "incident_id": self.incident_id,
            "raw_text": self.raw_text,
            "location": self.location,
            "priority": self.severity_priority,
            "required_capacity": self.required_capacity,
            "verified": self.verified_by_vision,
            "confidence": self.confidence_score,
            "status": self.status.value,
            "created_at": self.created_at
        }