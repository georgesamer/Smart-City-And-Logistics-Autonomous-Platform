import importlib
from typing import Dict, Any

# Hazard categories supported by the detector
HAZARD_CLASSES = ["Fire", "Flood", "Road_Block", "Normal"]

_ML_DEPS_AVAILABLE = None


def ml_dependencies_available() -> bool:
    """
    Are optional dependencies (torch + torchvision + Pillow) installed?
    Used to skip tests and run safely in lightweight environments.
    """
    global _ML_DEPS_AVAILABLE
    if _ML_DEPS_AVAILABLE is None:
        try:
            importlib.import_module("torch")
            importlib.import_module("torchvision")
            importlib.import_module("PIL.Image")
            _ML_DEPS_AVAILABLE = True
        except ImportError:
            _ML_DEPS_AVAILABLE = False
    return _ML_DEPS_AVAILABLE


class HazardVisionDetector:
    """
    Scene hazard detector using a CNN (optional component).

    Important notes:
    - Requires: pip install -r requirements-ml.txt
    - Weights start randomly initialized; classifications are unreliable without training.
    - To keep the module importable without torch, the actual network
      (nn.Module) is built inside _load_model only when dependencies exist, and exposed through
      forward / __call__ / eval for nn.Module compatibility.
    """

    def __init__(self, num_classes: int = 4):
        # Limit the number of classes to those actually defined (avoid IndexError in argmax)
        self.num_classes = min(num_classes, len(HAZARD_CLASSES))
        self.classes = list(HAZARD_CLASSES[:self.num_classes])
        self._load_model()

    def _load_model(self):
        if not ml_dependencies_available():
            raise ImportError(
                "HazardVisionDetector requires 'torch', 'torchvision' and 'Pillow'. "
                "Install them with: pip install -r requirements-ml.txt"
            )
        torch = importlib.import_module("torch")
        nn = importlib.import_module("torch.nn")
        transforms = importlib.import_module("torchvision.transforms")
        importlib.import_module("PIL.Image")  # noqa: F401 (required by the conversion pipeline)

        self.torch = torch

        class HazardNet(nn.Module):
            """Simple CNN for extracting hazard/edge features from scenes."""

            def __init__(self, num_classes: int):
                super().__init__()
                self.features = nn.Sequential(
                    nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2, 2),
                    nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
                    nn.ReLU(),
                    nn.MaxPool2d(2, 2),
                )
                # After two MaxPools on a 224x224 input -> 56x56 maps
                self.classifier = nn.Sequential(
                    nn.Flatten(),
                    nn.Linear(32 * 56 * 56, 128),
                    nn.ReLU(),
                    nn.Linear(128, num_classes),
                )

            def forward(self, x: Any) -> Any:
                x = self.features(x)
                x = self.classifier(x)
                return x

        self.net = HazardNet(self.num_classes)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def forward(self, x) -> Any:
        """Delegate to the actual network (only works after dependencies are installed)."""
        return self.net(x)

    def __call__(self, x) -> Any:
        return self.forward(x)

    def eval(self) -> Any:
        return self.net.eval()

    def predict_image(self, image_path: str) -> Dict[str, Any]:
        """
        Load an image and classify the hazard detected in it.
        Returns: {"detected_hazard", "confidence"}
        """
        Image = importlib.import_module("PIL.Image")

        image = Image.open(image_path).convert("RGB")
        tensor_image = self.transform(image).unsqueeze(0)

        self.eval()
        with self.torch.no_grad():
            outputs = self.forward(tensor_image)
            probs = self.torch.softmax(outputs, dim=-1)
            pred_idx = self.torch.argmax(probs, dim=-1).item()

        return {
            "detected_hazard": self.classes[pred_idx],
            "confidence": probs[0][pred_idx].item(),
        }


if __name__ == "__main__":
    import sys
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8")

    if not ml_dependencies_available():
        print("[Vision ML] Dependencies are not installed. Install them with: pip install -r requirements-ml.txt")
    else:
        vision_engine = HazardVisionDetector()
        # Simulate execution with a random tensor without an external image file
        dummy_input = vision_engine.torch.randn(1, 3, 224, 224)
        vision_engine.eval()
        with vision_engine.torch.no_grad():
            out = vision_engine(dummy_input)
            pred_class = vision_engine.classes[vision_engine.torch.argmax(out, dim=-1).item()]
        print("Vision Engine Execution Test Successful. Simulated Output:", pred_class)
