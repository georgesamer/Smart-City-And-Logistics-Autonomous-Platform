from typing import Dict, Any

# Map model severity to project priority (1 = highest importance)
SEVERITY_TO_PRIORITY = {"Low": 3, "Medium": 2, "High": 1}

_ML_DEPS_AVAILABLE = None


def ml_dependencies_available() -> bool:
    """
    Are optional dependencies (torch + transformers) installed?
    Used to skip tests and run safely in lightweight environments.
    """
    global _ML_DEPS_AVAILABLE
    if _ML_DEPS_AVAILABLE is None:
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
            _ML_DEPS_AVAILABLE = True
        except ImportError:
            _ML_DEPS_AVAILABLE = False
    return _ML_DEPS_AVAILABLE


class IncidentNLPProcessor:
    """
    Classify incident report severity with Transformers models (optional component).

    Important notes:
    - Requires: pip install -r requirements-ml.txt
    - The classification head starts randomly initialized; without fine-tuning
      on real incident data, outputs are unreliable (near-uniform distribution).
    - The default model (distilbert-base-uncased) is English; for Arabic reports,
      use an Arabic/multilingual model such as aubmindlab/bert-base-arabertv02.
    """

    def __init__(self, model_name: str = "distilbert-base-uncased"):
        self.model_name = model_name
        self.labels = {0: "Low", 1: "Medium", 2: "High"}
        self._load_model()

    def _load_model(self):
        if not ml_dependencies_available():
            raise ImportError(
                "IncidentNLPProcessor requires 'torch' and 'transformers'. "
                "Install them with: pip install -r requirements-ml.txt"
            )
        import torch  # noqa: F401
        from transformers import AutoTokenizer, AutoModelForSequenceClassification

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, num_labels=len(self.labels)
        )

    def analyze_report(self, text_report: str) -> Dict[str, Any]:
        """
        Classify the severity of a report's text.
        Returns: {"text", "predicted_severity", "confidence", "priority"}
        """
        import torch

        inputs = self.tokenizer(
            text_report, return_tensors="pt", truncation=True, padding=True, max_length=128
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()

        severity = self.labels[predicted_class]
        return {
            "text": text_report,
            "predicted_severity": severity,
            "confidence": probabilities[0][predicted_class].item(),
            "priority": SEVERITY_TO_PRIORITY[severity],
        }


if __name__ == "__main__":
    import sys
    if getattr(sys.stdout, "reconfigure", None) is not None:
        sys.stdout.reconfigure(encoding="utf-8")

    if not ml_dependencies_available():
        print("[NLP ML] Dependencies are not installed. Install them with: pip install -r requirements-ml.txt")
    else:
        nlp_engine = IncidentNLPProcessor()
        sample_text = "Severe multi-vehicle collision detected on highway with fire outbreak."
        print("NLP Analysis Result:", nlp_engine.analyze_report(sample_text))
