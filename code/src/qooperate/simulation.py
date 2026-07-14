from dataclasses import dataclass

import numpy as np

from qooperate.agent import QLearningAgent, COOPERATE
from qooperate.network import build_adjacency_list


@dataclass
class SimulationResult:
    cooperation_rate: np.ndarray
    mean_reward: np.ndarray


class Simulation:
    def __init__(self, graph, agent_params, payoff_matrix, rng,
                 coop_bins, reward_bins):
        self.adjacency = build_adjacency_list(graph)
        n = graph.number_of_nodes()
        self.agents = [
            QLearningAgent(agent_params["alpha"], agent_params["gamma"],
                           agent_params["epsilon"], 36, 2, rng,
                           initial_action=rng.integers(0, 2))
            for _ in range(n)
        ]
        self.payoff_matrix = payoff_matrix
        self.coop_bins, self.reward_bins = coop_bins, reward_bins

    def run(self, n_rounds: int) -> SimulationResult:
        n = len(self.agents)
        coop_rate = np.zeros(n_rounds)
        mean_reward = np.zeros(n_rounds)

        for t in range(n_rounds):

            # 1. observación
            states = []
            for i in range(n):
                neighbor_actions = []
                for j in self.adjacency[i]:
                    neighbor_actions.append(self.agents[j].last_action)

                state = self.agents[i].compute_state(
                    neighbor_actions,
                    self.coop_bins,
                    self.reward_bins
                )
                states.append(state)

            # 2. decisión
            actions = []
            for i in range(n):
                action = self.agents[i].select_action(states[i])
                actions.append(action)

            # 3. recompensa
            rewards = []
            for i in range(n):
                neighbor_rewards = []

                for j in self.adjacency[i]:
                    reward = self.payoff_matrix.payoff(actions[i], actions[j])
                    neighbor_rewards.append(reward)

                rewards.append(np.mean(neighbor_rewards))

            # 4. historial
            for i in range(n):
                self.agents[i].reward_history.append(rewards[i])

            # 5. siguiente estado
            next_states = []
            for i in range(n):
                neighbor_actions = []

                for j in self.adjacency[i]:
                    neighbor_actions.append(actions[j])

                next_state = self.agents[i].compute_state(
                    neighbor_actions,
                    self.coop_bins,
                    self.reward_bins
                )
                next_states.append(next_state)

            # 6. aprendizaje
            for i in range(n):
                self.agents[i].update(
                    states[i],
                    actions[i],
                    rewards[i],
                    next_states[i]
                )

            # 7. actualizar última acción
            for i in range(n):
                self.agents[i].last_action = actions[i]

            # 8. registro
            coop_count = 0
            for action in actions:
                if action == COOPERATE:
                    coop_count += 1

            coop_rate[t] = coop_count / n
            mean_reward[t] = np.mean(rewards)

        return SimulationResult(coop_rate, mean_reward)
