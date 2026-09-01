import random
from typing import Dict, Any


class QLearningDispatcher:
    """
    Q-learning agent to improve vehicle assignment decisions for incidents (reinforcement learning).

    Note: implemented in pure Python (without numpy) to preserve the zero-dependency design —
    the same approach used by RLRebalancer (lists + random instead of numpy arrays).
    """

    def __init__(self, num_states: int = 5, num_actions: int = 3, lr: float = 0.1, gamma: float = 0.95, epsilon: float = 0.1):
        self.num_states = num_states
        self.num_actions = num_actions
        self.lr = lr            # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate
        # Q-table: [state][action] initialized to zero
        self.q_table = [[0.0] * num_actions for _ in range(num_states)]

    def _best_action(self, state: int) -> int:
        """Best action according to the current Q-table (first maximum, like np.argmax)."""
        q_values = self.q_table[state]
        return q_values.index(max(q_values))

    def choose_action(self, state: int) -> int:
        """Choose an action with epsilon-greedy: random exploration or best exploitation."""
        if random.random() < self.epsilon:
            return random.randrange(self.num_actions)  # Explore
        return self._best_action(state)                # Exploit

    def update_q_value(self, state: int, action: int, reward: float, next_state: int):
        """Standard Bellman equation for updating Q(s, a)."""
        best_next_action = self._best_action(next_state)
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_delta = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.lr * td_delta

    def train_simulation(self, episodes: int = 100) -> Dict[str, Any]:
        """Simulate the assignment environment and train the agent for several episodes."""
        for _ in range(episodes):
            state = random.randrange(self.num_states)
            steps = 0

            while steps < 10:
                action = self.choose_action(state)
                # Simulated reward: optimal vehicle assignment gives +10, an error gives -2
                next_state = (state + action) % self.num_states
                reward = 10.0 if action == 0 else -2.0

                self.update_q_value(state, action, reward, next_state)
                state = next_state
                steps += 1

        return {
            "status": "Training Completed",
            "episodes": episodes,
            "q_table_shape": (self.num_states, self.num_actions),
        }


if __name__ == "__main__":
    import sys
    stdout = sys.stdout
    reconfigure = getattr(stdout, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")

    rl_dispatcher = QLearningDispatcher(num_states=4, num_actions=3)
    train_status = rl_dispatcher.train_simulation(episodes=50)
    print("RL Dispatcher Status:", train_status)
    print("Learned Q-Table Matrix:")
    for row in rl_dispatcher.q_table:
        print(" ", [round(v, 2) for v in row])
