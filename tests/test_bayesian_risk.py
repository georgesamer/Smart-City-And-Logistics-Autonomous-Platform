from typing import cast

from core.bayesian_risk_estimator import BayesianRiskEstimator


def test_delay_probability_from_cpt():
    estimator = BayesianRiskEstimator()

    assert estimator.predict_delay_probability(True, True)["delay_probability"] == 0.9
    assert estimator.predict_delay_probability(True, False)["delay_probability"] == 0.65
    assert estimator.predict_delay_probability(False, True)["delay_probability"] == 0.5
    assert estimator.predict_delay_probability(False, False)["delay_probability"] == 0.05


def test_mission_success_complements_delay():
    result = BayesianRiskEstimator().predict_delay_probability(True, True)

    # success = 1 - delay
    assert abs(result["delay_probability"] + result["mission_success_probability"] - 1.0) < 1e-9


def test_risk_level_thresholds():
    estimator = BayesianRiskEstimator()

    assert estimator.predict_delay_probability(True, True)["risk_level"] == "High"      # 0.90
    assert estimator.predict_delay_probability(False, True)["risk_level"] == "Medium"   # 0.50
    assert estimator.predict_delay_probability(False, False)["risk_level"] == "Low"     # 0.05


def test_unknown_combination_uses_default():
    # Any combination absent from the CPT returns the default probability 0.1
    assert BayesianRiskEstimator().predict_delay_probability(False, cast(bool, None))["delay_probability"] == 0.1
