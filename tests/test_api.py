from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Active"


def test_analyze_report_endpoint():
    response = client.post(
        "/api/v1/analyze-report",
        json={"report": "Urgent emergency report: a leak incident near (0, 4) with a capacity of 30 units"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["location"] == [0, 4]
    assert data["data"]["priority"] == 1


def test_assess_risk_endpoint():
    response = client.post(
        "/api/v1/assess-risk",
        json={"weather_severe": True, "traffic_heavy": False},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["delay_probability"] == 0.65
    assert data["risk_level"] == "High"


def test_dispatch_endpoint():
    response = client.post(
        "/api/v1/dispatch",
        json={"report": "Urgent emergency report: a leak incident near (0, 4) with a capacity of 30 units"},
    )

    assert response.status_code == 200
    result = response.json()["data"]
    assert result["status"] == "SUCCESS"
    assert result["vehicle_assigned"] == "V1"
