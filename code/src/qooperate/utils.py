from enum import Enum
from pathlib import Path

import numpy as np
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

    return list(np.linspace(0, hi, n_divisions + 2)[1:-1])


class StateRepresentation(Enum):
    S1 = 1
    S12 = 2
    S123 = 3
    S1234 = 4


def parse_state_representation(value: str | int | StateRepresentation) -> StateRepresentation:
    if isinstance(value, StateRepresentation):
        return value

    if isinstance(value, int):
        return StateRepresentation(value)

    key = str(value).strip().upper()
    aliases = {
        "1": StateRepresentation.S1,
        "S1": StateRepresentation.S1,
        "2": StateRepresentation.S12,
        "S12": StateRepresentation.S12,
        "3": StateRepresentation.S123,
        "S123": StateRepresentation.S123,
        "4": StateRepresentation.S1234,
        "S1234": StateRepresentation.S1234,
    }
    try:
        return aliases[key]
    except KeyError as exc:
        raise ValueError(f"Representación de estado desconocida: {value}") from exc


def encode_state(
        s1: int,
        s2: int,
        s3: int,
        s4: int,
        representation: StateRepresentation,
        n_s3: int,
        n_s4: int,
) -> int:
    match representation:

        case StateRepresentation.S1:
            return s1

        case StateRepresentation.S12:
            return s1 * 2 + s2

        case StateRepresentation.S123:
            return (s1 * 2 + s2) * n_s3 + s3

        case StateRepresentation.S1234:
            return ((s1 * 2 + s2) * n_s3 + s3) * n_s4 + s4

        case _:
            raise ValueError(f"Representación desconocida: {representation}")


def decode_state(
        idx: int,
        representation: StateRepresentation,
        n_s3: int,
        n_s4: int,
) -> tuple[int, int, int, int]:
    match representation:

        case StateRepresentation.S1:
            return idx, 0, 0, 0

        case StateRepresentation.S12:
            s1, s2 = divmod(idx, 2)
            return s1, s2, 0, 0

        case StateRepresentation.S123:
            x, s3 = divmod(idx, n_s3)
            s1, s2 = divmod(x, 2)
            return s1, s2, s3, 0

        case StateRepresentation.S1234:
            x, s4 = divmod(idx, n_s4)
            x, s3 = divmod(x, n_s3)
            s1, s2 = divmod(x, 2)
            return s1, s2, s3, s4

        case _:
            raise ValueError(f"Representación desconocida: {representation}")


def n_states(
        representation: StateRepresentation,
        n_s3: int,
        n_s4: int,
) -> int:
    match representation:

        case StateRepresentation.S1:
            return 2

        case StateRepresentation.S12:
            return 4

        case StateRepresentation.S123:
            return 2 * 2 * n_s3

        case StateRepresentation.S1234:
            return 2 * 2 * n_s3 * n_s4

        case _:
            raise ValueError(f"Representación desconocida: {representation}")


def discretize(value: float, bin_edges: list[float]) -> int:
    for i, edge in enumerate(bin_edges):
        if value < edge:
            return i
    return len(bin_edges)
