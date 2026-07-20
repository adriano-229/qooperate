"""Genera YAMLs atómicos de forma interactiva: pregunta cada parámetro
uno por uno, acepta uno o más valores separados por espacio, valida
cada valor, y genera el producto cartesiano de todas las combinaciones
como archivos YAML en config/<experimento>/.

En cada prompt: Enter solo usa el valor por defecto (entre paréntesis).
Escribir "Q" en cualquier prompt cancela toda la sesión sin escribir nada.

Uso:
    python experiments/generate_yamls.py
"""

from __future__ import annotations

import sys
from math import isqrt
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"

TOPOLOGY_MAP = {"1": "lattice", "2": "watts_strogatz", "3": "erdos_renyi"}
TOPOLOGY_ABBR = {"lattice": "la", "watts_strogatz": "ws", "erdos_renyi": "er"}


class Cancelled(Exception):
    pass


def _positive_float(v: str) -> float:
    x = float(v)
    if x <= 0:
        raise ValueError("debe ser > 0")
    return x


def _positive_int(v: str) -> int:
    x = int(v)
    if x <= 0:
        raise ValueError("debe ser > 0")
    return x


def _nonneg_int(v: str) -> int:
    x = int(v)
    if x < 0:
        raise ValueError("debe ser >= 0")
    return x


def _k_value(v: str) -> int:
    x = int(v)
    if x not in (4, 8, 12):
        raise ValueError("debe ser 4, 8 o 12")
    return x


def _perfect_square(v: str) -> int:
    x = int(v)
    if x <= 0 or isqrt(x) ** 2 != x:
        raise ValueError("debe ser un cuadrado perfecto (ej. 100, 400, 900)")
    return x


def _topology(v: str) -> str:
    if v not in TOPOLOGY_MAP:
        raise ValueError("debe ser 1 (lattice), 2 (watts_strogatz) o 3 (erdos_renyi)")
    return TOPOLOGY_MAP[v]


def _rho_value(v: str) -> int:
    x = int(v)
    if x < 1:
        raise ValueError("debe ser >= 1")
    return x


def _seed_value(v: str) -> int:
    x = int(v)
    if x < 0:
        raise ValueError("debe ser >= 0")
    return x


def _ws_beta(v: str) -> float:
    x = float(v)
    if not (0.0 <= x <= 1.0):
        raise ValueError("debe estar en [0, 1]")
    return x


# (clave YAML, abreviatura para el nombre de archivo, texto del prompt,
#  default, validador de un único token)
PARAMETERS = [
    ("topology", "t", "topology (1 lattice, 2 watts_strogatz, 3 erdos_renyi)", "1", _topology),
    ("n_agents", "n", "n_agents (debe ser cuadrado perfecto)", "100", _perfect_square),
    ("k", "k", "k (must be 4, 8 or 12)", "8", _k_value),
    ("alpha", "a", "alpha (debe ser > 0)", "0.1", _positive_float),
    ("epsilon", "e", "epsilon (debe ser > 0)", "0.1", _positive_float),
    ("gamma", "g", "gamma (debe ser > 0)", "0.9", _positive_float),
    ("rho", "r", "rho (debe ser >= 1)", "1", _rho_value),
    ("seed", "s", "seed (debe ser >= 0)", "0", _seed_value),
    ("n_rounds", "nr", "n_rounds (debe ser > 0)", "2000", _positive_int),
    ("reward_window", "rw", "reward_window (debe ser >= 1)", "10", _positive_int),
    ("sample_every", "se", "sample_every (debe ser >= 1)", "10", _positive_int),
    ("coop_n_divisions", "cd", "coop_n_divisions (debe ser >= 0)", "2", _nonneg_int),
    ("reward_n_divisions", "rd", "reward_n_divisions (debe ser >= 0)", "2", _nonneg_int),
    ("ws_beta", "wb", "ws_beta (debe estar en [0,1])", "0.1", _ws_beta),
]


def ask_values(key: str, prompt_text: str, default: str, validator) -> list:
    while True:
        raw = input(f"{prompt_text} (default: {default}): ").strip()
        if raw.upper() == "Q":
            raise Cancelled
        if raw == "":
            raw = default
        tokens = raw.split()
        try:
            values = [validator(tok) for tok in tokens]
        except ValueError as exc:
            print(f"  Valor inválido para {key}: {exc}. Intentá de nuevo.")
            continue
        if not values:
            print(f"  Necesito al menos un valor para {key}. Intentá de nuevo.")
            continue
        return values


def format_value_for_name(key: str, value) -> str:
    if key == "topology":
        return TOPOLOGY_ABBR[value]
    if isinstance(value, float):
        return str(value).replace(".", "")
    return str(value)


def build_yaml_text(combo: dict) -> str:
    lines = [f"{k}: {v}" for k, v in combo.items()]
    return "\n".join(lines) + "\n"


def main() -> None:
    try:
        experiment_name = input("Nombre del experimento: ").strip()
        if experiment_name.upper() == "Q":
            raise Cancelled
        if not experiment_name:
            print("Nombre de experimento vacío, cancelando.")
            return

        answers: dict[str, list] = {}
        for key, abbr, prompt_text, default, validator in PARAMETERS:
            answers[key] = ask_values(key, prompt_text, default, validator)

        # Producto cartesiano manual (evita depender de itertools solo
        # por legibilidad del orden de combinación, aunque itertools.product
        # serviría igual).
        import itertools

        keys = [p[0] for p in PARAMETERS]
        abbrs = {p[0]: p[1] for p in PARAMETERS}
        varying_keys = [k for k in keys if len(answers[k]) > 1]

        combos = []
        for values in itertools.product(*(answers[k] for k in keys)):
            combos.append(dict(zip(keys, values)))

        # Nombre: solo incluye en el nombre los parámetros que realmente
        # varían entre combinaciones (los fijos no aportan información).
        names = []
        for combo in combos:
            parts = [
                f"{abbrs[k]}{format_value_for_name(k, combo[k])}" for k in varying_keys
            ]
            suffix = "_".join(parts) if parts else "base"
            names.append(f"{experiment_name}_{suffix}")

        print(f"\nSe generarán los siguientes yamls en config/{experiment_name}/:")
        for name, combo in zip(names, combos):
            summary = ", ".join(f"{k}={combo[k]}" for k in varying_keys) or "(sin variación)"
            print(f"  {name}.yaml  [{summary}]")
        print(f"\nTotal de yamls: {len(combos)}")

        confirm = input("\n¿Confirmar generación? (Y/n, Q para cancelar): ").strip()
        if confirm.upper() == "Q":
            raise Cancelled
        if confirm.upper() not in ("", "Y"):
            print("Cancelado por el usuario.")
            return

        out_dir = CONFIG_DIR / experiment_name
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, combo in zip(names, combos):
            out_path = out_dir / f"{name}.yaml"
            out_path.write_text(build_yaml_text(combo), encoding="utf-8")
            print(f"Escrito: {out_path}")

    except Cancelled:
        print("\nCancelado. No se generó ningún archivo.")
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelado. No se generó ningún archivo.")
        sys.exit(1)


if __name__ == "__main__":
    main()
