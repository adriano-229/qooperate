from dataclasses import dataclass, field

import numpy as np
from tqdm import tqdm

from qooperate.agent import QLearningAgent, COOPERATE, DEFECT
from qooperate.metrics import compute_gini
from qooperate.network import build_adjacency_list
from qooperate.utils import StateRepresentation, n_states as compute_n_states

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

    delta_q: np.ndarray
    state_visits: np.ndarray
    actions: np.ndarray = field(repr=False)
    rewards: np.ndarray = field(repr=False)
    cumulative_reward_history: np.ndarray = field(repr=False)


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
            state_representation: StateRepresentation,
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
        n_states = compute_n_states(
            state_representation,
            n_s3,
            n_s4,
        )
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
                state_representation,
            )
            for _ in range(n)
        ]
        self.payoff_matrix = payoff_matrix
        self.coop_bins = coop_bins
        self.reward_bins = reward_bins
        self.sample_every = sample_every
        self.cumulative_reward = np.zeros(n)
        self.state_representation = state_representation

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

        checkpoint_delta_q = []
        checkpoint_state_visits = []

        round_actions = []
        round_rewards = []

        last_actions = [a.last_action for a in agents]

        for t in tqdm(range(n_rounds), desc="Simulation", leave=False, disable=not show_progress):
            # 1. Estado actual (basado en la ronda anterior)
            states = [
                agents[i].compute_state(
                    [last_actions[j] for j in self.adjacency[i]],
                    self.coop_bins,
                    self.reward_bins,
                    last_actions[i],
                    count_visit=True,
                )
                for i in range(n)
            ]
            # 2. Seleccionar acción
            actions = [agents[i].select_action(states[i]) for i in range(n)]

            # 3. Calcular recompensa media contra vecinos
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

            round_actions.append(np.asarray(actions, dtype=np.int8))
            round_rewards.append(rewards.astype(np.float32, copy=True))

            for i in range(n):
                agents[i].last_action = actions[i]
                agents[i].reward_history.append(rewards[i])

            # 4. Estado siguiente (ya con el historial actualizado)
            next_states = [
                agents[i].compute_state(
                    [actions[j] for j in self.adjacency[i]],
                    self.coop_bins,
                    self.reward_bins,
                    actions[i],
                    count_visit=False,
                )
                for i in range(n)
            ]

            # 5. Actualizar Q-table
            for i in range(n):
                agents[i].update(states[i], actions[i], rewards[i], next_states[i])

            # 6. Guardar las acciones de esta ronda para el cálculo del próximo estado
            last_actions = actions

            # Checkpoint
            is_checkpoint = ((t + 1) % sample_every == 0) or (t == n_rounds - 1)
            if is_checkpoint:
                played_actions = [a for a, c in zip(actions, connected) if c]
                coop_rate_t = np.mean([a == COOPERATE for a in played_actions]) if played_actions else 0.0
                gini_window_t = compute_gini(window_reward[connected]) if connected.any() else 0.0

                checkpoint_rounds.append(t + 1)
                checkpoint_coop.append(coop_rate_t)
                checkpoint_gini_window.append(gini_window_t)
                checkpoint_mean_reward.append(rewards[connected].mean() if connected.any() else 0.0)

                window_reward = np.zeros(n)

                delta_q = np.mean(
                    [
                        agent.q_table[:, COOPERATE] - agent.q_table[:, DEFECT]
                        for agent in agents
                    ],
                    axis=0,
                )

                checkpoint_delta_q.append(delta_q)

                visits = np.sum(
                    [agent.state_visits for agent in agents],
                    axis=0,
                )

                checkpoint_state_visits.append(visits.copy())

        actions_history = np.asarray(round_actions, dtype=np.int8) if round_actions else np.zeros((0, n), dtype=np.int8)
        rewards_history = np.asarray(round_rewards, dtype=np.float32) if round_rewards else np.zeros((0, n), dtype=np.float32)
        cumulative_reward_history = np.cumsum(rewards_history, axis=0, dtype=np.float32) if len(rewards_history) else np.zeros((0, n), dtype=np.float32)

        return SimulationResult(
            rounds=np.array(checkpoint_rounds, dtype=int),
            cooperation_rate=np.array(checkpoint_coop),
            gini_window=np.array(checkpoint_gini_window),
            mean_reward=np.array(checkpoint_mean_reward),
            delta_q=np.array(checkpoint_delta_q),
            state_visits=np.array(checkpoint_state_visits),
            final_cumulative_reward=self.cumulative_reward.copy(),
            actions=actions_history,
            rewards=rewards_history,
            cumulative_reward_history=cumulative_reward_history,
        )
