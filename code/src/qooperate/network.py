from enum import Enum
from math import isqrt

import networkx as nx


class TopologyType(str, Enum):
    LATTICE = "lattice"
    WATTS_STROGATZ = "watts_strogatz"
    ERDOS_RENYI = "erdos_renyi"


# Offsets (dr, dc) por nivel de conectividad k en la lattice toroidal.
# k=4: Von Neumann r=1 · k=8: Moore r=1 · k=12: Von Neumann r=2
_LATTICE_OFFSETS = {
    4: [(-1, 0), (1, 0), (0, -1), (0, 1)],
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


def _generate_lattice(n: int, k: int) -> nx.Graph:
    side = isqrt(n)
    if side * side != n:
        raise ValueError("n debe ser un cuadrado perfecto")
    if k not in _LATTICE_OFFSETS:
        raise ValueError(f"k={k} no soportado en lattice (valores válidos: 4, 8, 12)")

    graph = nx.Graph()
    graph.add_nodes_from(range(n))

    def node(row: int, col: int) -> int:
        return row * side + col

    for row in range(side):
        for col in range(side):
            u = node(row, col)
            for dr, dc in _LATTICE_OFFSETS[k]:
                v = node((row + dr) % side, (col + dc) % side)
                graph.add_edge(u, v)

    return graph


def generate_network(
        topology: TopologyType, n: int, k: int, seed: int, ws_beta: float = 0.1
) -> nx.Graph:
    """Genera la red. No reintenta ni corrige conexidad: Erdős-Rényi y
    Watts-Strogatz pueden devolver redes con más de una componente
    conexa (ver NOTES.md, sección "Conexidad de redes"). Simulation
    debe poder operar sobre esas redes tal cual.
    """
    match topology:
        case TopologyType.LATTICE:
            return _generate_lattice(n, k)
        case TopologyType.WATTS_STROGATZ:
            return nx.watts_strogatz_graph(n, k, ws_beta, seed=seed)
        case TopologyType.ERDOS_RENYI:
            return nx.erdos_renyi_graph(n, k / (n - 1), seed=seed)
        case _:
            raise ValueError(f"Unknown topology: {topology}")


def build_adjacency_list(graph: nx.Graph, rho: int = 1) -> list[list[int]]:
    """Vecinos de orden rho: nodos a distancia 1..rho en el grafo (BFS),
    excluyendo al propio nodo. rho=1 (default) es el vecindario directo
    de siempre. rho>1 expande con quién juega el agente (ver NOTES.md,
    experimento EA1)."""
    n = graph.number_of_nodes()
    if rho == 1:
        return [list(graph.neighbors(i)) for i in range(n)]
    adjacency = []
    for i in range(n):
        distances = nx.single_source_shortest_path_length(graph, i, cutoff=rho)
        adjacency.append([j for j in distances if j != i])
    return adjacency
