"""Genera, por cada .parquet pasado, dos figuras PNG transparentes (fondo
transparente, línea de color aleatorio): una de cooperación (C_t) y otra
de Gini de ventana. Pensadas para superponerse con overlay.py.

Para que la superposición quede alineada, cada figura usa un tamaño en
píxeles y una posición de ejes (Axes) FIJOS (sin tight_layout, que
recalcula márgenes según el ancho del texto y desalinea el área de
ploteo entre imágenes), y límites de ejes fijos: Y siempre en [0, 1]
(cooperación y Gini están acotados ahí por definición), X en
[0, max(round) de ESE parquet].

Uso:
    python experiments/figures.py <plot_smoothing> <parquet1> [<parquet2> ...]
    python experiments/figures.py 20 results/eX/eX_*.parquet
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.metrics import moving_average  # noqa: E402

FIGURES_DIR = Path(__file__).resolve().parents[1] / "results" / "figures"

FIG_SIZE = (8, 5)  # pulgadas
DPI = 150
AXES_RECT = [0.12, 0.12, 0.83, 0.83]  # [left, bottom, width, height] en fracción de figura, fijo


def _random_color() -> tuple[float, float, float]:
    return (random.random(), random.random(), random.random())


def _plot_single(
        rounds,
        cooperation,
        gini,
        smoothing: int,
        out_path: Path,
) -> None:
    fig = plt.figure(figsize=FIG_SIZE)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes(AXES_RECT)
    ax.patch.set_alpha(0.0)

    color = _random_color()

    ax.plot(
        rounds,
        moving_average(cooperation, smoothing),
        color=color,
        linewidth=2,
        label="C_t",
    )

    ax.plot(
        rounds,
        moving_average(gini, smoothing),
        color=color,
        linewidth=2,
        linestyle="--",
        label="Gini",
    )

    ax.set_xlim(0, max(rounds))
    ax.set_ylim(0, 1)
    ax.set_xlabel("Ronda")
    ax.set_ylabel("Valor")
    ax.legend()

    fig.savefig(out_path, dpi=DPI, transparent=True)
    plt.close(fig)
    print(f"Guardada: {out_path}")


def make_figures(parquet_path: Path, smoothing: int) -> None:
    df = pd.read_parquet(parquet_path).sort_values("round")

    prefix = parquet_path.stem.split("_")[0]
    out_dir = FIGURES_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = parquet_path.stem
    _plot_single(
        df["round"],
        df["cooperation_rate"].to_numpy(),
        df["gini_window"].to_numpy(),
        smoothing,
        out_dir / f"{stem}.png",
    )


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    smoothing = int(sys.argv[1])
    for arg in sys.argv[2:]:
        make_figures(Path(arg), smoothing)


if __name__ == "__main__":
    main()
