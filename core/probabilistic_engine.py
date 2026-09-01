from typing import Tuple, Dict, Any

class ProbabilisticEngine:
    def __init__(self):
        pass

    def calculate_traffic_delay_probability(
        self, 
        has_nearby_accident: bool, 
        is_rush_hour: bool, 
        is_bad_weather: bool
    ) -> float:
        """
        Calculate the probability of a major route delay from surrounding factors (Bayesian reasoning).
        P(Delay | Accident, RushHour, Weather)
        """
        # Base conditional probabilities
        base_prob = 0.10  # Initial delay probability under normal conditions

        if has_nearby_accident:
            base_prob += 0.50
        if is_rush_hour:
            base_prob += 0.25
        if is_bad_weather:
            base_prob += 0.15

        # Clamp the result between 0.0 and 1.0
        final_probability = min(1.0, base_prob)
        print(f"\n[Probabilistic Engine] Traffic Delay Inference:")
        print(f" └─ Factors: Accident={has_nearby_accident}, RushHour={is_rush_hour}, Weather={is_bad_weather}")
        print(f" └─ Calculated Delay Probability: {final_probability * 100:.1f}%")
        
        return final_probability

    def estimate_vehicle_location(
        self, 
        last_known_location: Tuple[int, int], 
        planned_direction: Tuple[int, int], 
        gps_signal_loss: bool = False
    ) -> Tuple[int, int]:
        """
        Estimate the vehicle's actual position when the GPS signal is lost or weak.
        """
        if not gps_signal_loss:
            return last_known_location

        # Estimate the next movement from the planned direction after signal loss
        r, c = last_known_location
        dr, dc = planned_direction
        estimated_loc = (r + dr, c + dc)

        print(f"[Probabilistic Engine] GPS Signal Lost!")
        print(f" └─ Estimating location based on trajectory: {last_known_location} -> {estimated_loc}")
        
        return estimated_loc