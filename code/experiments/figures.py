"""Genera una figura PNG que superpone la evolución de cooperación (C_t,
línea sólida) y Gini de ventana (línea punteada) de uno o más parquets,
un color fijo por parquet (determinístico según el orden en que se
pasan como argumento), con una única leyenda por parquet que muestra
el color y el valor del parámetro que varía entre ellos.

El parámetro que varía se detecta automáticamente comparando los
metadatos (columnas constantes por corrida) entre los parquets pasados.
Si más de un parámetro varía entre ellos, se usa el primero detectado y
se avisa por consola.

Cada figura usa un tamaño en píxeles y una posición de ejes (Axes)
FIJOS, sin tight_layout, y límites de eje fijos: Y en [0, 1], X en
[0, max(round) entre todos los parquets pasados].

Uso:
python experiments/figures.py <plot_smoothing> [ ...]
python experiments/figures.py 20 results/e1/e1_tla_k4.parquet results/e1/e1_tla_k8.parquet results/e1/e1_tla_k12.parquet
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.metrics import moving_average  # noqa: E402

FIGURES_DIR = Path(__file__).resolve().parents[1] / "results" / "figures"

FIG_SIZE = (8, 5)
DPI = 150
AXES_RECT: tuple[float, float, float, float] = (0.12, 0.12, 0.83, 0.83)

# Columnas que identifican la configuración de una corrida.

METADATA_COLUMNS = [
    "topology",
    "n_agents",
    "k",
    "alpha",
    "epsilon",
    "gamma",
    "rho",
    "seed",
    "n_rounds",
    "reward_window",
    "sample_every",
    "coop_n_divisions",
    "reward_n_divisions",
    "ws_beta",
    "state_representation",
]

def _color_for_index(i: int, n: int) -> tuple:
    cmap = matplotlib.colormaps["tab10" if n <= 10 else "hsv"]
    return cmap(i / max(n - 1, 1))[:3] if n > 1 else cmap(0.0)[:3]


def _detect_varying_params(dfs: list[pd.DataFrame]) -> list[str]:
    """Devuelve las columnas de metadatos cuyos valores difieren entre parquets."""
    varying = []

    for col in METADATA_COLUMNS:
        if col not in dfs[0].columns:
            continue

        values = {df[col].to_numpy()[0] for df in dfs}

        if len(values) > 1:
            varying.append(col)

    if len(varying) > 1:
        print(
            f"Los parámetros que varían entre los parquets pasados son {varying}."
        )

    return varying


def _common_prefix(stems: list[str]) -> str:
    prefix = os.path.commonprefix(stems)
    return prefix.rstrip("_") or "figure"


def make_figure(parquet_paths: list[Path], smoothing: int) -> None:
    dfs = [
        pd.read_parquet(path).sort_values("round")
        for path in parquet_paths
    ]

    varying_params = _detect_varying_params(dfs)

    fig = plt.figure(figsize=FIG_SIZE)
    fig.patch.set_alpha(0.0)

    ax = fig.add_axes(AXES_RECT)
    ax.patch.set_alpha(0.0)

    min_round = None
    max_round = None
    n = len(dfs)

    for i, (path, df) in enumerate(zip(parquet_paths, dfs)):
        color = _color_for_index(i, n)

        rounds = df["round"].to_numpy()
        round_min = int(rounds.min())
        round_max = int(rounds.max())

        min_round = (
            round_min
            if min_round is None
            else min(min_round, round_min)
        )
        max_round = (
            round_max
            if max_round is None
            else max(max_round, round_max)
        )

        if varying_params:
            label = ", ".join(
                f"{param}={df[param].iat[0]}"
                for param in varying_params
            )
        else:
            label = path.stem

        ax.plot(
            rounds,
            moving_average(
                df["cooperation_rate"].to_numpy(),
                smoothing,
            ),
            color=color,
            linewidth=1,
            label=label,
        )

        ax.plot(
            rounds,
            moving_average(
                df["gini_window"].to_numpy(),
                smoothing,
            ),
            color=color,
            linewidth=1,
            linestyle="--",
        )

    ax.set_xlim(min_round, max_round)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Ronda")
    ax.set_ylabel("Valor")
    ax.legend()

    stems = [path.stem for path in parquet_paths]
    out_name = _common_prefix(stems)

    prefix = out_name.split("_")[0]
    out_dir = FIGURES_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"{out_name}.jpg"

    fig.savefig(
        out_path,
        dpi=DPI,
        transparent=True,
    )

    plt.close(fig)

    print(f"Guardada: {out_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    parquet_paths = [Path(arg) for arg in sys.argv[1:]]

    make_figure(parquet_paths, 100)


if __name__ == "__main__":
    main()
