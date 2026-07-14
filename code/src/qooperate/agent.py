from collections import deque

import numpy as np

from qooperate.utils import encode_state, discretize

COOPERATE = 0
DEFECT = 1


class QLearningAgent:

    def __init__(
        self, alpha, gamma, epsilon, n_states, n_actions, rng: np.random.Generator
    ):
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.rng = rng
        self.q_table = np.zeros((n_states, n_actions))
        initial_action = rng.choice([COOPERATE, DEFECT])
        self.last_action = initial_action
        self.reward_history: deque[float] = deque(maxlen=10)

    def select_action(self, state: int) -> int:
        if self.rng.random() < self.epsilon:
            return self.rng.choice([COOPERATE, DEFECT])
        q = self.q_table[state]
        return COOPERATE if q[COOPERATE] >= q[DEFECT] else DEFECT  # empate -> C

    def update(self, state, action, reward, next_state) -> None:
        current_q = self.q_table[state, action]
        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state, action] = current_q + self.alpha * (target - current_q)

    def compute_state(
        self,
        neighbor_actions: list[int],
        coop_bins: list[float],
        reward_bins: list[float],
    ) -> int:
        coop_fraction = (
            (sum(1 for a in neighbor_actions if a == COOPERATE) / len(neighbor_actions))
            if neighbor_actions
            else 1.0
        )
        s1 = COOPERATE if coop_fraction >= 0.5 else DEFECT
        s3 = discretize(coop_fraction, coop_bins)
        s2 = self.last_action
        mean_reward = np.mean(self.reward_history) if self.reward_history else 0.0
        s4 = discretize(mean_reward, reward_bins)
        return encode_state(s1, s2, s3, s4)
