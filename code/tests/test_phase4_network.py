import matplotlib.pyplot as plt
import networkx as nx
import pytest

from qooperate.network import _generate_lattice, _generate_erdos_renyi, _generate_watts_strogatz


def test_networks():
    for name, graph, tol in [
        ("LA", _generate_lattice(100, 4, 0), 0.0),
        ("WS", _generate_watts_strogatz(100, 4, 0.1, 0), 0.5),
        ("ER", _generate_erdos_renyi(100, 4, 0), 1.5),
    ]:
        nx.draw(
            graph,
            pos=nx.spring_layout(graph, seed=0),
            node_size=10,
            with_labels=False,
        )

        plt.title(name)
        plt.savefig(f"{name}.png", dpi=200, bbox_inches="tight")
        plt.close()

        mean_deg = sum(d for _, d in graph.degree()) / graph.number_of_nodes()
        assert mean_deg == pytest.approx(4, abs=tol)
