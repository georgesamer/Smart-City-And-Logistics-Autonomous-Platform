from core.qlearning_dispatcher import QLearningDispatcher


def test_q_table_initialized_to_zeros():
    dispatcher = QLearningDispatcher(num_states=4, num_actions=3)

    assert len(dispatcher.q_table) == 4
    assert all(len(row) == 3 for row in dispatcher.q_table)
    assert all(value == 0.0 for row in dispatcher.q_table for value in row)


def test_choose_action_returns_valid_action():
    dispatcher = QLearningDispatcher(num_states=4, num_actions=3, epsilon=0.0)  # Full exploitation

    action = dispatcher.choose_action(2)

    assert 0 <= action < 3


def test_update_q_value_applies_bellman():
    dispatcher = QLearningDispatcher(num_states=4, num_actions=3, lr=1.0, gamma=0.0)

    dispatcher.update_q_value(state=1, action=2, reward=5.0, next_state=3)

    # With lr=1.0 and gamma=0.0: Q(s,a) = reward
    assert dispatcher.q_table[1][2] == 5.0


def test_train_simulation_returns_status():
    status = QLearningDispatcher(num_states=4, num_actions=3).train_simulation(episodes=50)

    assert status["status"] == "Training Completed"
    assert status["episodes"] == 50
    assert status["q_table_shape"] == (4, 3)


def test_training_learns_optimal_action_value():
    # Without exploration: optimal action (0) repeats and its value should grow from zero
    dispatcher = QLearningDispatcher(num_states=4, num_actions=3, epsilon=0.0, lr=0.5, gamma=0.9)
    dispatcher.train_simulation(episodes=200)

    assert dispatcher.q_table[0][0] > 0.0
