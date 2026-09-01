from typing import Tuple, Dict, Any, Optional
from models.map_graph import CityGridMap

class VisionEngine:
    def __init__(self, city_map: CityGridMap):
        self.city_map = city_map

    def process_camera_feed(self, location: Tuple[int, int], mock_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate analysis of a camera stream near a location.
        In production, this would be replaced by PyTorch / YOLO / CNN code.
        """
        print(f"\n[Vision Engine] Scanning camera feed at location {location}...")
        
        # Simulated image-processing results from a CNN
        # Covers: Blocked (X), Heavy Traffic (T), Clear (.)
        img_path = (mock_image_path or "").lower()
        if "accident" in img_path or "block" in img_path:
            detected_status = "BLOCKED"
            grid_value = "X"
            confidence = 0.95
        elif "traffic" in img_path or "jam" in img_path:
            detected_status = "TRAFFIC"
            grid_value = "T"
            confidence = 0.88
        else:
            detected_status = "CLEAR"
            grid_value = "."
            confidence = 0.99

        print(f" └─ Visual Detection -> Status: {detected_status}, Confidence: {confidence*100:.1f}%")
        
        return {
            "status": detected_status,
            "grid_value": grid_value,
            "confidence": confidence,
            "location": location
        }

    def verify_and_update_map(self, nlp_task_destination: Tuple[int, int], camera_image_mock: str) -> bool:
        """
        Verify the NLP report through vision and update the map dynamically.
        Note: do not close the task target itself as a hard obstacle ('X'), making it unreachable;
        classify it as heavy traffic ('T'), which remains traversable at a higher cost.
        """
        vision_result = self.process_camera_feed(nlp_task_destination, camera_image_mock)
        r, c = nlp_task_destination

        # Update the map when a road-state change is detected
        if vision_result["status"] in ["BLOCKED", "TRAFFIC"]:
            old_val = self.city_map.grid[r][c]
            if vision_result["status"] == "BLOCKED":
                # Convert a blockage at the target to heavy traffic ('T') instead of closing it ('X')
                # so the target cell remains reachable by the planner.
                print(f"[Vision Engine] Blockage confirmed at destination {nlp_task_destination}. "
                      f"Marking as Traffic High ('T') instead of hard-blocking ('X') to keep the target accessible.")
            self.city_map.grid[r][c] = "T"
            print(f"[Vision Engine] Map updated at {nlp_task_destination}: '{old_val}' -> 'T'")
            return True

        return False