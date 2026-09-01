# 🚦 Smart City & Logistics Autonomous Platform

A **production-ready, full-stack monitoring and dispatch platform** for autonomous vehicle fleets in smart city ecosystems — combining classical search algorithms, probabilistic reasoning, reinforcement learning, computer vision, and NLP into a single Routing, Dispatch, and Risk Management system.

---

## 📖 Overview

The project is organized as a layered system, where each layer owns a specific part of the decision-making lifecycle for the smart city fleet:

1. **Perception** — detects incidents and hazards from images and text reports.
2. **Core Engine** — computes optimal routes, estimates risk, and assigns tasks to vehicles.
3. **Analytics** — forecasts future service demand.
4. **Pipelines** — wires all components together through an event bus.
5. **Interfaces (API + Dashboard)** — expose results and control the system.

---

## ✨ Key Features

| Component | Purpose | File |
|---|---|---|
| 🧭 A* Router | Finds the shortest safe path between two points on the city graph | `core/astar_router.py`, `core/pathfinding.py` |
| 📊 Bayesian Risk Estimator | Estimates the probability of risk along a route or area | `core/bayesian_risk_estimator.py` |
| 🧩 CSP Solver | Solves constraint-satisfaction problems (scheduling/resource allocation) | `core/csp_solver.py` |
| 📜 Logic Rules Engine | Applies logical rules to operational decisions | `core/logic_rules.py` |
| 🔮 Probabilistic Engine | General-purpose probabilistic inference for the system | `core/probabilistic_engine.py` |
| 🎮 Q-Learning Dispatcher | Assigns tasks to vehicles via reinforcement learning | `core/qlearning_dispatcher.py` |
| ⚖️ RL Rebalancer | Rebalances fleet distribution geographically | `core/rl_rebalancer.py` |
| 👁️ Hazard Vision Detector | Detects hazards from images (Computer Vision) | `perception/hazard_vision_detector.py`, `perception/vision_engine.py` |
| 🗣️ Incident NLP Processor | Extracts incident information from report text | `perception/incident_nlp_processor.py`, `perception/nlp_engine.py` |
| 📈 Demand Forecaster | Forecasts future service demand | `analytics/demand_forecaster.py` |
| 🔄 Dispatch Pipeline + Event Bus | Coordinates data flow across all modules | `pipelines/dispatch_pipeline.py`, `pipelines/event_bus.py` |
| 🌐 REST API | FastAPI interface for interacting with the system | `api/main.py` |
| 🖥️ Interactive Dashboard | Streamlit-based interactive control dashboard | `app.py` |

---

## 🗂️ Project Structure

```
Smart-City-And-Logistics-Autonomous-Platform/
├─ analytics/              # Demand forecasting
│  └─ demand_forecaster.py
├─ api/                    # FastAPI interface
│  └─ main.py
├─ app.py                  # Dashboard entry point (Streamlit)
├─ config/                 # Project and map settings
│  ├─ map_config.py
│  └─ settings.py
├─ core/                   # Planning, reasoning, and RL engines
│  ├─ astar_router.py
│  ├─ bayesian_risk_estimator.py
│  ├─ csp_solver.py
│  ├─ logic_rules.py
│  ├─ pathfinding.py
│  ├─ probabilistic_engine.py
│  ├─ qlearning_dispatcher.py
│  └─ rl_rebalancer.py
├─ data/
│  ├─ map_layouts/         # City network layouts
│  └─ trained_models/      # Saved trained models
├─ models/                 # Data models
│  ├─ incident.py
│  ├─ map_graph.py
│  ├─ task.py
│  └─ vehicle.py
├─ perception/              # Computer vision & NLP
│  ├─ hazard_vision_detector.py
│  ├─ incident_nlp_processor.py
│  ├─ nlp_engine.py
│  └─ vision_engine.py
├─ pipelines/               # Component orchestration
│  ├─ dispatch_pipeline.py
│  └─ event_bus.py
├─ tests/                   # Full test suite for every module
├─ main.py                  # Main project entry point
├─ conftest.py
├─ pytest.ini
├─ requirements.txt         # Core runtime dependencies
└─ requirements-ml.txt      # Optional ML/perception dependencies
```

---

## ⚙️ Requirements

- Python 3.10+
- Core dependencies (`requirements.txt`):
  - `fastapi>=0.100`
  - `uvicorn>=0.23`
  - `streamlit>=1.40`
  - `pytest>=7.0`
  - `httpx>=0.24`
- Optional deep-perception dependencies (`requirements-ml.txt`) — needed only if you use the computer-vision hazard detection or NLP incident processing:
  - `torch>=2.0`
  - `torchvision>=0.15`
  - `transformers>=4.30`
  - `Pillow>=10.0`

---

## 🚀 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/georgesamer/Smart-City-And-Logistics-Autonomous-Platform.git
cd Smart-City-And-Logistics-Autonomous-Platform
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt

# Optional: enable computer vision & NLP perception modules
pip install -r requirements-ml.txt
```

### 4. Run the API server

```bash
uvicorn api.main:app --reload
```

### 5. Run the interactive dashboard

```bash
streamlit run app.py
```

### 6. Or run the main entry point

```bash
python main.py
```

---

## 🧪 Running Tests

The project ships with a full test suite covering every module (routing, risk estimation, CSP, logic rules, NLP, vision, Q-learning, and more):

```bash
pytest
```

Or run a specific test file, for example:

```bash
pytest tests/test_astar_router.py
pytest tests/test_bayesian_risk.py
pytest tests/test_qlearning.py
```

---

## 🏗️ Architecture Flow

```
   [Incident report / image / text]
            │
            ▼
   ┌─────────────────┐
   │   Perception     │  ← Vision Engine + NLP Engine
   └────────┬─────────┘
            ▼
   ┌─────────────────┐
   │  Event Bus       │  ← Broadcasts the event to subscribers
   └────────┬─────────┘
            ▼
   ┌─────────────────┐
   │ Risk Estimation  │  ← Bayesian Risk Estimator
   │ + Logic Rules    │
   └────────┬─────────┘
            ▼
   ┌─────────────────┐
   │ Dispatch Pipeline│  ← A* Routing + CSP + Q-Learning Dispatcher
   └────────┬─────────┘
            ▼
   ┌─────────────────┐
   │ RL Rebalancer    │  ← Rebalances the fleet
   └────────┬─────────┘
            ▼
   [API + Dashboard: results & control]
```

---

## 🤝 Contributing

Contributions are welcome! To add an improvement or fix:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/my-feature`.
3. Make your changes with appropriate tests (`pytest`).
4. Open a Pull Request with a clear description of the change.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**George Samer** — [georgesamer](https://github.com/georgesamer)
