from typing import List, Dict, Tuple, Any
from collections import defaultdict
from models.incident import Incident

class DemandForecaster:
    def __init__(self, grid_shape: Tuple[int, int] = (4, 5)):
        self.rows, self.cols = grid_shape
        # Historical count of reports in each cell (r, c)
        self.historical_incidents_map: Dict[Tuple[int, int], int] = defaultdict(int)

    def fit_historical_data(self, incidents_history: List[Incident]):
        """Update historical readings based on previous reports."""
        for incident in incidents_history:
            self.historical_incidents_map[incident.location] += 1
        print(f"[Demand Forecaster] Ingested {len(incidents_history)} historical incidents.")

    def predict_high_demand_zones(
        self, 
        current_hour: int, 
        top_n: int = 2
    ) -> List[Tuple[int, int]]:
        """
        Predict the top N areas where future demand/incidents are expected.
        Takes peak hours and historical data into account.
        """
        is_rush_hour = 7 <= current_hour <= 10 or 16 <= current_hour <= 19
        rush_multiplier = 1.5 if is_rush_hour else 1.0

        scored_zones: Dict[Tuple[int, int], float] = {}

        for r in range(self.rows):
            for c in range(self.cols):
                loc = (r, c)
                base_demand = self.historical_incidents_map.get(loc, 0)
                # Calculate the forecast score
                score = base_demand * rush_multiplier
                scored_zones[loc] = score

        # Sort areas by forecast score
        sorted_zones = sorted(scored_zones.items(), key=lambda item: item[1], reverse=True)
        top_hotspots = [loc for loc, score in sorted_zones[:top_n]]

        print(f"\n[Demand Forecaster] Demand Prediction (Hour {current_hour}:00, RushHour={is_rush_hour}):")
        print(f" └─ Predicted High Demand Hotspots: {top_hotspots}")

        return top_hotspots