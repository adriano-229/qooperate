from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def generate_bin_edges(n_divisions: int, hi: float) -> list[float]:
    """n_divisions cortes equiespaciados en (0, hi), dando n_divisions+1
    bins. n_divisions=0 -> sin cortes (todo cae en un único bin)."""
    if n_divisions < 0:
        raise ValueError("n_divisions debe ser >= 0")
    if n_divisions == 0:
        return []
    import numpy as np

    return list(np.linspace(0, hi, n_divisions + 2)[1:-1])


def encode_state(s1: int, s2: int, s3: int, s4: int, n_s3: int, n_s4: int) -> int:
    """n_s3, n_s4: cardinalidad de s3 y s4 (n_divisions + 1 de cada bin)."""
    return s1 * (2 * n_s3 * n_s4) + s2 * (n_s3 * n_s4) + s3 * n_s4 + s4


def decode_state(idx: int, n_s3: int, n_s4: int) -> tuple[int, int, int, int]:
    s1, rem = divmod(idx, 2 * n_s3 * n_s4)
    s2, rem = divmod(rem, n_s3 * n_s4)
    s3, s4 = divmod(rem, n_s4)
    return s1, s2, s3, s4


def n_states(n_s3: int, n_s4: int) -> int:
    return 2 * 2 * n_s3 * n_s4


def discretize(value: float, bin_edges: list[float]) -> int:
    for i, edge in enumerate(bin_edges):
        if value < edge:
            return i
    return len(bin_edges)
