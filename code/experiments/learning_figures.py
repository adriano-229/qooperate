"""Genera heatmaps del proceso de aprendizaje a partir de los artefactos
`*_learning.npz` asociados a uno o más parquets.

Por cada corrida se genera una única figura con dos paneles:

- arriba: ΔQ(s) = Q(s, C) - Q(s, D)
- abajo: visitas acumuladas por estado

Uso:
    python experiments/learning_figures.py <parquet1> [<parquet2> ...]
    python experiments/learning_figures.py --label-style verbose results/exp4/exp4_s1234.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.utils import (  # noqa: E402
    StateRepresentation,
    decode_state,
    n_states as compute_n_states,
    parse_state_representation,
)

FIGURES_DIR = Path(__file__).resolve().parents[1] / "results" / "figures"
FIG_SIZE = (12, 8)
DPI = 150
AXES_RECT = [0.08, 0.08, 0.84, 0.86]


def _state_label(state: tuple[int, int, int, int], representation: StateRepresentation, style: str) -> str:
    s1, s2, s3, s4 = state
    names = [("s1", s1), ("s2", s2), ("s3", s3), ("s4", s4)]
    active = names[: representation.value]

    def fmt_value(key: str, value: int) -> str:
        if key in {"s1", "s2"}:
            return "C" if value == 0 else "D"
        return str(value)

    if style == "index":
        raise RuntimeError("'index' style is handled separately")

    if style == "verbose":
        return "\n".join(f"{key}={fmt_value(key, value)}" for key, value in active)

    if style == "tuple":
        return "(" + ",".join(fmt_value(key, value) for key, value in active) + ")"

    raise ValueError(f"Estilo de etiqueta desconocido: {style}")


def build_state_labels(
    representation: StateRepresentation,
    n_s3: int,
    n_s4: int,
    style: str = "tuple",
) -> list[str]:
    labels = []
    n = compute_n_states(representation, n_s3, n_s4)
    for idx in range(n):
        state = decode_state(idx, representation, n_s3, n_s4)
        if style == "index":
            labels.append(str(idx))
        else:
            labels.append(_state_label(state, representation, style))
    return labels


def _sparse_ticks(size: int, max_ticks: int = 12) -> list[int]:
    if size <= 0:
        return []
    if size <= max_ticks:
        return list(range(size))
    ticks = np.linspace(0, size - 1, max_ticks, dtype=int)
    return list(dict.fromkeys(ticks.tolist()))


def _format_round_ticks(rounds: np.ndarray, max_ticks: int = 12) -> tuple[list[int], list[str]]:
    if len(rounds) == 0:
        return [], []
    tick_idx = _sparse_ticks(len(rounds), max_ticks=max_ticks)
    return tick_idx, [str(int(rounds[i])) for i in tick_idx]


def _load_learning_artifacts(parquet_path: Path) -> tuple[pd.DataFrame, np.lib.npyio.NpzFile]:
    df = pd.read_parquet(parquet_path).sort_values("round")
    npz_path = parquet_path.with_name(f"{parquet_path.stem}_learning.npz")
    if not npz_path.exists():
        raise FileNotFoundError(f"No existe el artefacto de aprendizaje asociado: {npz_path}")
    return df, np.load(npz_path)


def _visit_array_to_plot(state_visits: np.ndarray, scale: str) -> np.ndarray:
    if scale == "linear":
        return state_visits.astype(float)
    if scale == "log":
        return np.log1p(state_visits.astype(float))
    raise ValueError(f"Escala desconocida: {scale}")


def make_figure(parquet_path: Path, label_style: str = "tuple", visit_scale: str = "linear") -> Path:
    df, npz = _load_learning_artifacts(parquet_path)

    state_representation = parse_state_representation(df["state_representation"].iloc[0])
    n_s3 = int(df["coop_n_divisions"].iloc[0]) + 1
    n_s4 = int(df["reward_n_divisions"].iloc[0]) + 1
    n_states = compute_n_states(state_representation, n_s3, n_s4)

    delta_q = np.asarray(npz["delta_q"], dtype=float)
    state_visits = np.asarray(npz["state_visits"], dtype=float)
    rounds = np.asarray(npz["rounds"], dtype=int)

    if delta_q.ndim != 2:
        raise ValueError(f"delta_q debe tener 2 dimensiones, recibió {delta_q.shape}")
    if state_visits.ndim != 2:
        raise ValueError(f"state_visits debe tener 2 dimensiones, recibió {state_visits.shape}")
    if delta_q.shape != state_visits.shape:
        raise ValueError(f"delta_q y state_visits deben tener la misma forma, recibieron {delta_q.shape} y {state_visits.shape}")
    if delta_q.shape[1] != n_states:
        raise ValueError(
            f"La cantidad de estados en los artefactos ({delta_q.shape[1]}) no coincide con n_states={n_states}"
        )
    if delta_q.shape[0] != len(rounds):
        raise ValueError(
            f"La cantidad de checkpoints en los artefactos ({delta_q.shape[0]}) no coincide con rounds={len(rounds)}"
        )

    state_labels = build_state_labels(state_representation, n_s3, n_s4, style=label_style)
    x_ticks = _sparse_ticks(n_states, max_ticks=12)
    y_ticks, y_tick_labels = _format_round_ticks(rounds, max_ticks=12)

    fig = plt.figure(figsize=FIG_SIZE)
    fig.patch.set_alpha(0.0)
    ax_delta = fig.add_axes((AXES_RECT[0], 0.56, AXES_RECT[2], 0.34))
    ax_visits = fig.add_axes((AXES_RECT[0], 0.10, AXES_RECT[2], 0.34))
    for ax in (ax_delta, ax_visits):
        ax.patch.set_alpha(0.0)

    if delta_q.size > 0:
        delta_max = float(np.max(np.abs(delta_q)))
    else:
        delta_max = 1.0
    if delta_max == 0:
        delta_max = 1.0
    delta_im = ax_delta.imshow(
        delta_q,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        cmap="coolwarm",
        vmin=-delta_max,
        vmax=delta_max,
    )
    ax_delta.set_title("ΔQ(s) = Q(s, C) - Q(s, D)")
    ax_delta.set_ylabel("Ronda")
    ax_delta.set_xticks(x_ticks)
    ax_delta.set_xticklabels([state_labels[i] for i in x_ticks], rotation=45, ha="right")
    ax_delta.set_yticks(y_ticks)
    ax_delta.set_yticklabels(y_tick_labels)
    cbar_delta = fig.colorbar(delta_im, ax=ax_delta, fraction=0.025, pad=0.02)
    cbar_delta.set_label("ΔQ")

    visits_plot = _visit_array_to_plot(state_visits, visit_scale)
    if visit_scale == "linear":
        visits_im = ax_visits.imshow(
            visits_plot,
            aspect="auto",
            origin="lower",
            interpolation="nearest",
            cmap="viridis",
        )
        cbar_label = "Visitas acumuladas"
    else:
        masked = np.ma.masked_where(state_visits <= 0, visits_plot)
        visits_im = ax_visits.imshow(
            masked,
            aspect="auto",
            origin="lower",
            interpolation="nearest",
            cmap="viridis",
        )
        visits_im.cmap.set_bad(color="white")
        cbar_label = "log1p(visitas acumuladas)"
    ax_visits.set_title("Frecuencia de visita acumulada de estados")
    ax_visits.set_xlabel("Estado")
    ax_visits.set_ylabel("Ronda")
    ax_visits.set_xticks(x_ticks)
    ax_visits.set_xticklabels([state_labels[i] for i in x_ticks], rotation=45, ha="right")
    ax_visits.set_yticks(y_ticks)
    ax_visits.set_yticklabels(y_tick_labels)
    cbar_visits = fig.colorbar(visits_im, ax=ax_visits, fraction=0.025, pad=0.02)
    cbar_visits.set_label(cbar_label)

    fig.suptitle(
        f"{parquet_path.stem} — {state_representation.name} — {visit_scale} / {label_style}",
        y=0.99,
    )

    prefix = parquet_path.stem.split("_")[0]
    out_dir = FIGURES_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{parquet_path.stem}_learning.png"
    fig.savefig(out_path, dpi=DPI, transparent=True)
    plt.close(fig)
    print(f"Guardada: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parquets", nargs="+", type=Path, help="Parquets de corridas a procesar")
    parser.add_argument(
        "--label-style",
        choices=("index", "tuple", "verbose"),
        default="tuple",
        help="Formato de etiquetas para los estados en el eje X",
    )
    parser.add_argument(
        "--visit-scale",
        choices=("linear", "log"),
        default="linear",
        help="Escala visual para el heatmap de visitas",
    )
    args = parser.parse_args()

    for parquet_path in args.parquets:
        make_figure(parquet_path, label_style=args.label_style, visit_scale=args.visit_scale)


if __name__ == "__main__":
    main()



