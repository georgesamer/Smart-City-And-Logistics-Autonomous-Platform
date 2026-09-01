from perception.incident_nlp_processor import (
    IncidentNLPProcessor,
    SEVERITY_TO_PRIORITY,
    ml_dependencies_available as nlp_deps,
)
from perception.hazard_vision_detector import (
    HazardVisionDetector,
    HAZARD_CLASSES,
    ml_dependencies_available as vision_deps,
)


def test_severity_labels_map_to_project_priority():
    # Model severity (High/Medium/Low) -> project priority (1 = highest importance)
    assert SEVERITY_TO_PRIORITY == {"Low": 3, "Medium": 2, "High": 1}


def test_hazard_classes_are_exposed():
    assert HAZARD_CLASSES == ["Fire", "Flood", "Road_Block", "Normal"]


def test_nlp_processor_guards_missing_dependencies():
    if not nlp_deps():
        # Dependencies are missing -> ImportError with a clear message is expected
        try:
            IncidentNLPProcessor()
        except ImportError:
            pass
        else:
            raise AssertionError("ImportError should be raised when dependencies are missing")
    else:
        # Dependencies are installed -> run the actual model
        result = IncidentNLPProcessor().analyze_report(
            "Severe multi-vehicle collision detected on highway with fire outbreak."
        )
        assert result["predicted_severity"] in ("Low", "Medium", "High")
        assert 0.0 <= result["confidence"] <= 1.0


def test_vision_detector_guards_missing_dependencies():
    if not vision_deps():
        try:
            HazardVisionDetector()
        except ImportError:
            pass
        else:
            raise AssertionError("ImportError should be raised when dependencies are missing")
    else:
        # Dependencies are installed -> test execution with a random tensor (4 classes)
        detector = HazardVisionDetector()
        dummy_input = detector.torch.randn(1, 3, 224, 224)
        detector.eval()
        with detector.torch.no_grad():
            out = detector(dummy_input)
        assert out.shape[-1] == 4
