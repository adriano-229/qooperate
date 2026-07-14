import networkx as nx
import numpy as np
import pytest

from qooperate.agent import COOPERATE
from qooperate.payoff import PayoffMatrix
from qooperate.simulation import Simulation


def test_simulation_two_agents_trivial_graph():
    graph = nx.Graph()
    graph.add_edge(0, 1)
    rng = np.random.default_rng(0)
    sim = Simulation(graph, {"alpha": 0.5, "gamma": 0.8, "epsilon": 0.0},
                     PayoffMatrix(), rng, [1 / 3, 2 / 3], [5 / 3, 10 / 3])
    sim.agents[0].last_action = COOPERATE
    sim.agents[1].last_action = COOPERATE
    result = sim.run(n_rounds=1)
    # epsilon=0, Q en ceros -> empate favorece C -> ambos cooperan -> reward=R=3
    assert result.mean_reward[0] == pytest.approx(3.0)


def test_simulation_reproducible_with_same_seed():
    graph = nx.erdos_renyi_graph(20, 0.3, seed=1)

    def run():
        rng = np.random.default_rng(7)
        sim = Simulation(graph, {"alpha": 0.1, "gamma": 0.9, "epsilon": 0.1},
                         PayoffMatrix(), rng, [1 / 3, 2 / 3], [5 / 3, 10 / 3])
        return sim.run(50).cooperation_rate

    np.testing.assert_array_equal(run(), run())
