from enum import Enum
from math import isqrt

import networkx as nx


class TopologyType(Enum):
    LATTICE = "lattice"
    WATTS_STROGATZ = "watts_strogatz"
    ERDOS_RENYI = "erdos_renyi"


MAX_CONNECTIVITY_RETRIES = 10


def _generate_lattice(n: int, k: int) -> nx.Graph:
    side = isqrt(n)
    if side * side != n:
        raise ValueError("n debe ser un cuadrado perfecto")
    offsets = {
        4: [
            (-1, 0), (1, 0),
            (0, -1), (0, 1),
        ],
        8: [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1),
        ],
        12: [
            (-2, 0), (-1, -1), (-1, 0), (-1, 1),
            (0, -2), (0, -1), (0, 1), (0, 2),
            (1, -1), (1, 0), (1, 1), (2, 0),
        ],
    }

    if k not in offsets:
        raise ValueError(f"k={k} no soportado")

    graph = nx.Graph()
    graph.add_nodes_from(range(n))

    def node(row: int, col: int) -> int:
        return row * side + col

    for row in range(side):
        for col in range(side):
            u = node(row, col)

            for dr, dc in offsets[k]:
                vr = (row + dr) % side
                vc = (col + dc) % side
                v = node(vr, vc)

                graph.add_edge(u, v)

    return graph


def _generate_watts_strogatz(n, k, beta, seed) -> nx.Graph:
    return nx.watts_strogatz_graph(n, k, beta, seed=seed)


def _generate_erdos_renyi(n, k, seed) -> nx.Graph:
    return nx.erdos_renyi_graph(n, k / (n - 1), seed=seed)


def generate_network(topology, n, k, seed, ws_beta=0.1):

    for attempt in range(MAX_CONNECTIVITY_RETRIES):
        current_seed = seed + attempt * 1000

        match topology:
            case TopologyType.LATTICE:
                graph = _generate_lattice(n, k)
            case TopologyType.WATTS_STROGATZ:
                graph = _generate_watts_strogatz(n, k, ws_beta, current_seed)
            case TopologyType.ERDOS_RENYI:
                graph = _generate_erdos_renyi(n, k, current_seed)
            case _:
                raise ValueError(f"Unknown topology: {topology}")

        if nx.is_connected(graph):
            return graph

    raise RuntimeError(f"Red no conexa tras {MAX_CONNECTIVITY_RETRIES} intentos")


def build_adjacency_list(graph: nx.Graph) -> list[list[int]]:
    return [list(graph.neighbors(i)) for i in range(graph.number_of_nodes())]
