import random
from typing import Tuple, List, Dict

class RLRebalancer:
    def __init__(
        self, 
        grid_shape: Tuple[int, int] = (4, 5), 
        learning_rate: float = 0.1, 
        discount_factor: float = 0.9, 
        epsilon: float = 0.2
    ):
        self.rows, self.cols = grid_shape
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Available actions for each vehicle: (0: Up, 1: Down, 2: Left, 3: Right, 4: Stay)
        self.actions = [( -1, 0 ), ( 1, 0 ), ( 0, -1 ), ( 0, 1 ), ( 0, 0 )]
        
        # Q-table: map each state (vehicle position) to available actions
        self.q_table: Dict[Tuple[int, int], List[float]] = {}
        self._init_q_table()

    def _init_q_table(self):
        """Initialize the Q-table for every map position."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.q_table[(r, c)] = [0.0] * len(self.actions)

    def select_action(self, state: Tuple[int, int]) -> int:
        """Choose an action using the epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, len(self.actions) - 1)  # Exploration
        
        # Exploitation
        q_values = self.q_table[state]
        return q_values.index(max(q_values))

    def get_next_state(self, current_state: Tuple[int, int], action_idx: int) -> Tuple[int, int]:
        """Calculate the new position and keep it within map bounds."""
        dr, dc = self.actions[action_idx]
        new_r = max(0, min(self.rows - 1, current_state[0] + dr))
        new_c = max(0, min(self.cols - 1, current_state[1] + dc))
        return (new_r, new_c)

    def update_q_value(
        self, 
        state: Tuple[int, int], 
        action_idx: int, 
        reward: float, 
        next_state: Tuple[int, int]
    ):
        """Update Q using Q(s,a) = Q(s,a) + lr * [R + gamma * max(Q(s',a')) - Q(s,a)]."""
        best_next_q = max(self.q_table[next_state])
        current_q = self.q_table[state][action_idx]
        
        new_q = current_q + self.lr * (reward + self.gamma * best_next_q - current_q)
        self.q_table[state][action_idx] = new_q

    def rebalance_idle_vehicle(
        self, 
        vehicle_loc: Tuple[int, int], 
        high_demand_zones: List[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """
        Find the best location to rebalance the currently available vehicle.
        """
        action_idx = self.select_action(vehicle_loc)
        next_loc = self.get_next_state(vehicle_loc, action_idx)

        # Calculate reward: increase it when approaching high-demand areas
        reward = -1.0  # Default movement cost
        if next_loc in high_demand_zones:
            reward = 20.0
        
        self.update_q_value(vehicle_loc, action_idx, reward, next_loc)

        print(f"\n[RL Engine] Autonomous Rebalancing Executed:")
        print(f" └─ Vehicle at {vehicle_loc} -> Selected Action: {action_idx} -> Repositioned to: {next_loc}")
        print(f" └─ Action Reward: {reward} | Updated Q-value: {self.q_table[vehicle_loc][action_idx]:.2f}")

        return next_loc