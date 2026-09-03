"""
Genera un log en CSV con snapshots de la evolución del aprendizaje,
a partir de los artefactos `learning_*.npz` asociados a uno o más parquets.

Para una cantidad configurable de snapshots (por defecto 5, equiespaciados
entre 5% y 100% de las rondas simuladas), cada snapshot se mapea al
checkpoint disponible más cercano y se genera una tabla con una fila por
estado y columnas agrupadas por snapshot. Cada celda muestra:

- ΔQ: Q(s, C) - Q(s, D) promediado entre agentes, en ese checkpoint.
- F:  frecuencia relativa de visitas del estado en ese checkpoint,
      V(s) / sum(V) sobre todos los estados.
- P:  "potencia" del estado, ΔQ * F (cuánto pesa ese ΔQ dada la frecuencia
      con la que realmente se visitó ese estado).

Uso:
    python experiments/learning_log.py <parquet1> [<parquet2> ...]
    python experiments/learning_log.py --snapshots 8 <parquet1> [<parquet2> ...]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.utils import (  # noqa: E402
    n_states as compute_n_states,
    parse_state_representation,
)

from learning_figures import build_state_labels  # noqa: E402

LOGS_DIR = Path(__file__).resolve().parents[1] / "results" / "logs"
DEFAULT_N_SNAPSHOTS = 4
# Configuración de redondeo
ROUND_DELTA_Q = 1  # Decimales para ΔQ
ROUND_FREQ = 2     # Decimales para F (frecuencia)
ROUND_POWER = 2    # Decimales para P (potencia)


def _snapshot_percentages(n_snapshots: int) -> np.ndarray:
    if n_snapshots < 1:
        raise ValueError("n_snapshots debe ser >= 1")
    if n_snapshots == 1:
        return np.array([100.0])
    # Genera n_snapshots puntos equiespaciados entre START_PERCENT% y 100%
    return np.linspace(0, 100.0, n_snapshots)[1:]  # Excluye el primer punto si es START_PERCENT


def _snapshot_indices(rounds: np.ndarray, percentages: np.ndarray) -> list[int]:
    """Mapea cada porcentaje de rondas al índice de checkpoint disponible
    más cercano (por cercanía en cantidad de rondas)."""
    if len(rounds) == 0:
        return []
    max_round = float(rounds[-1])
    targets = (percentages / 100.0) * max_round
    return [int(np.argmin(np.abs(rounds - t))) for t in targets]


def make_log(parquet_path: Path, n_snapshots: int = DEFAULT_N_SNAPSHOTS) -> Path:
    df = pd.read_parquet(parquet_path).sort_values("round")
    if df.empty:
        raise ValueError(f"El parquet no tiene filas: {parquet_path}")

    npz_path = parquet_path.with_name(f"learning_{parquet_path.stem}.npz")
    if not npz_path.exists():
        raise FileNotFoundError(f"No existe el artefacto de aprendizaje asociado: {npz_path}")
    npz = np.load(npz_path)

    state_representation = parse_state_representation(df["state_representation"].iloc[0])
    n_s3 = int(df["coop_n_divisions"].iloc[0]) + 1
    n_s4 = int(df["reward_n_divisions"].iloc[0]) + 1
    n_states = compute_n_states(state_representation, n_s3, n_s4)

    delta_q = np.asarray(npz["delta_q"], dtype=float)
    state_visits = np.asarray(npz["state_visits"], dtype=float)
    rounds = np.asarray(npz["rounds"], dtype=int)

    if delta_q.ndim != 2 or state_visits.ndim != 2:
        raise ValueError("Los artefactos de aprendizaje deben ser matrices 2D")
    if delta_q.shape != state_visits.shape:
        raise ValueError(
            f"delta_q y state_visits deben tener la misma forma, recibieron {delta_q.shape} y {state_visits.shape}")
    if delta_q.shape[1] != n_states:
        raise ValueError(
            f"La cantidad de estados en los artefactos ({delta_q.shape[1]}) no coincide con n_states={n_states}")
    if delta_q.shape[0] != len(rounds):
        raise ValueError(
            f"La cantidad de checkpoints en los artefactos ({delta_q.shape[0]}) no coincide con rounds={len(rounds)}")

    state_labels = build_state_labels(state_representation, n_s3, n_s4)

    percentages = _snapshot_percentages(n_snapshots)
    snapshot_idx = _snapshot_indices(rounds, percentages)

    # Construir el DataFrame para CSV
    columns = ["Estado"]
    for pct in percentages:
        columns.extend([f"{pct:.0f}%_ΔQ", f"{pct:.0f}%_F", f"{pct:.0f}%_P"])

    data = []
    for state in range(n_states):
        row = [state_labels[state]]
        for idx in snapshot_idx:
            total_visits = float(state_visits[idx].sum())
            delta = float(delta_q[idx, state])
            freq = (float(state_visits[idx, state]) / total_visits) if total_visits > 0 else 0.0
            power = delta * freq
            if power == 0.0:
                power = 0.0

            # Redondear los valores
            delta = round(delta, ROUND_DELTA_Q)
            freq = round(freq, ROUND_FREQ)
            power = round(power, ROUND_POWER)

            row.extend([delta, freq, power])
        data.append(row)

    df_csv = pd.DataFrame(data, columns=columns)

    # Guardar CSV
    prefix = parquet_path.stem.split("_")[0]
    out_dir = LOGS_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"learning_log_{parquet_path.stem}.csv"

    # Guardar como CSV con separador punto y coma para mejor compatibilidad con Excel
    df_csv.to_csv(out_path, index=False, sep=';', decimal=',')

    print(f"Guardado: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera un log en CSV con snapshots del aprendizaje.")
    parser.add_argument("parquets", nargs="+", type=Path, help="Parquet(s) de resultados")
    parser.add_argument(
        "--snapshots", type=int, default=DEFAULT_N_SNAPSHOTS,
        help=f"Cantidad de snapshots equiespaciados a incluir (default: {DEFAULT_N_SNAPSHOTS})",
    )
    args = parser.parse_args()

    for parquet_path in args.parquets:
        make_log(parquet_path, args.snapshots)


if __name__ == "__main__":
    main()