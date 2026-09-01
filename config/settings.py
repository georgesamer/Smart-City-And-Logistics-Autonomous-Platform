from dataclasses import dataclass

@dataclass(frozen=True)
class SystemSettings:
    # 1. General System Configs
    APP_NAME: str = "Smart Emergency Dispatch & Fleet System"
    ENV: str = "development"  # development / production
    DEBUG: bool = True
    
    # 2. Logic & Safety Engine Rules
    BATTERY_DRAIN_PER_UNIT: float = 2.0  # Battery consumption per distance unit
    SAFETY_BATTERY_BUFFER: float = 1.2     # Safety factor for the return trip (20% reserve)
    MIN_BATTERY_THRESHOLD: float = 20.0   # Minimum battery before accepting a task

    # 3. Probabilistic Engine Thresholds
    DELAY_THRESHOLD_HIGH: float = 0.60    # Threshold at which a road is declared busy
    BASE_TRAFFIC_PROBABILITY: float = 0.10

    # 4. RL Rebalancer Hyperparameters (Q-Learning)
    RL_LEARNING_RATE: float = 0.1
    RL_DISCOUNT_FACTOR: float = 0.9
    RL_EPSILON: float = 0.2
    
    # 5. NLP & Capacity Defaults
    DEFAULT_REQUIRED_CAPACITY: float = 20.0


# Single instance shared across modules
settings = SystemSettings()