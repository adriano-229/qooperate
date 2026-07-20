from dataclasses import dataclass, field

import numpy as np
from tqdm import tqdm

from qooperate.agent import QLearningAgent, COOPERATE
from qooperate.metrics import compute_gini
from qooperate.network import build_adjacency_list
from qooperate.utils import n_states as compute_n_states

N_ACTIONS = 2


@dataclass
class SimulationResult:
    """Serie sub-muestreada a los puntos de checkpoint (ver sample_every).

    gini_window es un Gini de ventana (resetea cada checkpoint), no el
    Gini acumulado histórico total. Ver NOTES.md.
    final_cumulative_reward sí es la recompensa acumulada total, nunca
    resetea, y no incluye rondas en que un agente quedó aislado.
    """

    rounds: np.ndarray
    cooperation_rate: np.ndarray
    gini_window: np.ndarray
    mean_reward: np.ndarray
    final_cumulative_reward: np.ndarray = field(repr=False)


class Simulation:
    """Ejecuta el IPD multiagente sobre una red fija (ver doc. sección 2.8)."""

    def __init__(
            self,
            graph,
            agent_params: dict,
            payoff_matrix,
            rng: np.random.Generator,
            coop_bins: list[float],
            reward_bins: list[float],
            reward_window: int,
            sample_every: int = 1,
            rho: int = 1,
    ):
        if sample_every < 1:
            raise ValueError("sample_every debe ser >= 1")
        if rho < 1:
            raise ValueError("rho debe ser >= 1")
        self.adjacency = build_adjacency_list(graph, rho=rho)
        n = graph.number_of_nodes()
        self.n = n
        n_s3, n_s4 = len(coop_bins) + 1, len(reward_bins) + 1
        n_states = compute_n_states(n_s3, n_s4)
        # Nodos sin vecinos (posibles en Erdős-Rényi/Watts-Strogatz, ver
        # NOTES.md): no juegan, se excluyen de coop_rate y gini_window.
        self.isolated = np.array([len(adj) == 0 for adj in self.adjacency])
        self.agents = [
            QLearningAgent(
                agent_params["alpha"],
                agent_params["gamma"],
                agent_params["epsilon"],
                n_states,
                N_ACTIONS,
                reward_window,
                rng,
            )
            for _ in range(n)
        ]
        self.payoff_matrix = payoff_matrix
        self.coop_bins = coop_bins
        self.reward_bins = reward_bins
        self.sample_every = sample_every
        self.cumulative_reward = np.zeros(n)

    def run(self, n_rounds: int, show_progress: bool = True) -> SimulationResult:
        n = self.n
        agents = self.agents
        sample_every = self.sample_every
        connected = ~self.isolated

        window_reward = np.zeros(n)
        checkpoint_rounds = []
        checkpoint_coop = []
        checkpoint_gini_window = []
        checkpoint_mean_reward = []

        last_actions = [a.last_action for a in agents]

        for t in tqdm(range(n_rounds), desc="Simulation", leave=False, disable=not show_progress):
            states = [
                agents[i].compute_state(
                    [last_actions[j] for j in self.adjacency[i]],
                    self.coop_bins,
                    self.reward_bins,
                    last_actions[i],
                )
                for i in range(n)
            ]
            actions = [agents[i].select_action(states[i]) for i in range(n)]

            # Recompensa promedio contra todos los vecinos (sección 2.1).
            # Nodos aislados no juegan: recompensa 0, no error/NaN.
            rewards = np.array(
                [
                    float(np.mean([self.payoff_matrix.payoff(actions[i], actions[j]) for j in self.adjacency[i]]))
                    if self.adjacency[i]
                    else 0.0
                    for i in range(n)
                ]
            )

            self.cumulative_reward += rewards
            window_reward += rewards

            # Estado siguiente: s2 debe ser la acción recién tomada
            # (actions[i]), no la de la ronda anterior.
            next_states = [
                agents[i].compute_state(
                    [actions[j] for j in self.adjacency[i]],
                    self.coop_bins,
                    self.reward_bins,
                    actions[i],
                )
                for i in range(n)
            ]

            for i in range(n):
                agents[i].update(states[i], actions[i], rewards[i], next_states[i])
            for i in range(n):
                agents[i].last_action = actions[i]
                agents[i].reward_history.append(rewards[i])
            last_actions = actions

            is_checkpoint = ((t + 1) % sample_every == 0) or (t == n_rounds - 1)
            if is_checkpoint:
                played_actions = [a for a, c in zip(actions, connected) if c]
                coop_rate_t = np.mean([a == COOPERATE for a in played_actions]) if played_actions else 0.0
                gini_window_t = compute_gini(window_reward[connected]) if connected.any() else 0.0

                checkpoint_rounds.append(t)
                checkpoint_coop.append(coop_rate_t)
                checkpoint_gini_window.append(gini_window_t)
                checkpoint_mean_reward.append(rewards[connected].mean() if connected.any() else 0.0)

                window_reward = np.zeros(n)

        return SimulationResult(
            rounds=np.array(checkpoint_rounds, dtype=int),
            cooperation_rate=np.array(checkpoint_coop),
            gini_window=np.array(checkpoint_gini_window),
            mean_reward=np.array(checkpoint_mean_reward),
            final_cumulative_reward=self.cumulative_reward.copy(),
        )
