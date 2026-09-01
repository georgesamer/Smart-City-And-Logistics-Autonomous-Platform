from typing import Dict, Any


class BayesianRiskEstimator:
    """
    Bayesian risk estimator: uses an explicit conditional probability table (CPT)
    P(Delay | Weather, Traffic) to calculate delay probability and task success.

    Note: implemented in pure Python (without numpy) to preserve the zero-dependency design.
    """

    def __init__(self):
        # Prior probabilities: P(Weather = Severe), P(Traffic = Heavy)
        self.p_severe_weather = 0.2
        self.p_heavy_traffic = 0.3

        # Conditional probability table: P(Delay | Weather, Traffic)
        self.cpt_delay = {
            (True, True): 0.90,    # Severe weather and heavy traffic
            (True, False): 0.65,   # Severe weather and light traffic
            (False, True): 0.50,   # Clear weather and heavy traffic
            (False, False): 0.05,  # Clear weather and light traffic
        }

    def predict_delay_probability(self, weather_severe: bool, traffic_heavy: bool) -> Dict[str, Any]:
        """Calculate risk through Bayesian inference using the CPT."""
        delay_prob = self.cpt_delay.get((weather_severe, traffic_heavy), 0.1)
        success_prob = 1.0 - delay_prob

        return {
            "delay_probability": round(delay_prob, 4),
            "mission_success_probability": round(success_prob, 4),
            "risk_level": "High" if delay_prob > 0.6 else ("Medium" if delay_prob > 0.3 else "Low"),
        }


if __name__ == "__main__":
    import sys
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

    risk_engine = BayesianRiskEstimator()
    risk_res = risk_engine.predict_delay_probability(weather_severe=True, traffic_heavy=False)
    print("Bayesian Risk Assessment:", risk_res)
