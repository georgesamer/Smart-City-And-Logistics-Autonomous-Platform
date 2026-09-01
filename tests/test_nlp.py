from models.incident import IncidentStatus
from perception.nlp_engine import NLPEngine


def test_parse_report_extracts_priority_coordinates_and_capacity():
    engine = NLPEngine()

    task = engine.parse_report_to_task(
        "TASK_1",
        "Emergency report near (2, 3) requiring support with a capacity of 30 units",
    )

    assert task.task_id == "TASK_1"
    assert task.priority == 1
    assert task.destination == (2, 3)
    assert task.required_capacity == 30.0


def test_incident_conversion_preserves_report_details():
    engine = NLPEngine()
    incident = engine.parse_report_to_incident(
        "INC_1",
        "Incident at the hospital with a capacity of 15 units",
    )

    assert incident.location == (0, 4)
    assert incident.severity_priority == 1
    assert incident.required_capacity == 15.0
    assert incident.status is IncidentStatus.REPORTED

    task = engine.create_task_from_incident(incident)
    assert task.task_id == "TASK_INC_1"
    assert task.destination == incident.location