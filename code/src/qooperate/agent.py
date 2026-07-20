from collections import deque

import numpy as np

from qooperate.utils import encode_state, discretize

COOPERATE = 0
DEFECT = 1


class QLearningAgent:

    def __init__(
            self, alpha, gamma, epsilon, n_states, n_actions, reward_window, rng: np.random.Generator
    ):
        self.alpha, self.gamma, self.epsilon = alpha, gamma, epsilon
        self.rng = rng
        self.q_table = np.zeros((n_states, n_actions))
        self.last_action = rng.choice([COOPERATE, DEFECT])
        self.reward_history: deque[float] = deque(maxlen=reward_window)

    def select_action(self, state: int) -> int:
        if self.rng.random() < self.epsilon:
            return self.rng.choice([COOPERATE, DEFECT])
        q = self.q_table[state]
        if q[COOPERATE] == q[DEFECT]:
            return self.rng.choice([COOPERATE, DEFECT])
        return COOPERATE if q[COOPERATE] > q[DEFECT] else DEFECT

    def update(self, state, action, reward, next_state) -> None:
        current_q = self.q_table[state, action]
        target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state, action] = current_q + self.alpha * (target - current_q)

    def compute_state(
        self,
        neighbor_actions: list[int],
        coop_bins: list[float],
        reward_bins: list[float],
            last_action: int,
    ) -> int:
        """last_action se recibe como parámetro (no self.last_action) para
        poder calcular tanto el estado actual como el next_state dentro
        de la misma ronda, sin depender de cuándo se mute self.last_action.
        n_s3/n_s4 (cardinalidad de s3, s4) se derivan de len(bins)+1."""
        coop_fraction = (
            (sum(1 for a in neighbor_actions if a == COOPERATE) / len(neighbor_actions))
            if neighbor_actions
            else 1.0
        )
        s1 = COOPERATE if coop_fraction >= 0.5 else DEFECT
        s3 = discretize(coop_fraction, coop_bins)
        s2 = last_action
        mean_reward = np.mean(self.reward_history) if self.reward_history else 0.0
        s4 = discretize(mean_reward, reward_bins)
        n_s3, n_s4 = len(coop_bins) + 1, len(reward_bins) + 1
        return encode_state(s1, s2, s3, s4, n_s3=n_s3, n_s4=n_s4)
