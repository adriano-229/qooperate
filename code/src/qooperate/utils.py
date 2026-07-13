from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    try:
        # Lee el archivo de texto y lo deserializa de forma segura
        return yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Error al cargar la configuración desde {path}: {e}")
        return {}


def encode_state(s1: int, s2: int, s3: int, s4: int) -> int:
    # s1,s2 ∈ {0,1}; s3,s4 ∈ {0,1,2}
    return s1 * 18 + s2 * 9 + s3 * 3 + s4


def decode_state(idx: int) -> tuple[int, int, int, int]:
    s1, rem = divmod(idx, 18)
    s2, rem = divmod(rem, 9)
    s3, s4 = divmod(rem, 3)
    return s1, s2, s3, s4


def discretize(value: float, bin_edges: list[float]) -> int:
    # bin_edges=[e1,e2] -> 3 bins: [0,e1), [e1,e2), [e2,+inf)
    # corte estrictamente "menor que" -> value == edge cae en el bin superior
    for i, edge in enumerate(bin_edges):
        if value < edge:
            return i
    return len(bin_edges)
