"""Corre una o más simulaciones atómicas (una corrida = un YAML = una
semilla). Cada YAML fija todos los parámetros como escalares, incluidos
coop_n_divisions/reward_n_divisions (cantidad de cortes de los bins de
estado; los bordes se generan equiespaciados en [0,1] y [0,5]). El
barrido de parámetros se hace armando varios YAML a mano, no dentro del
código. Ver README.md.

results/<prefijo>/<nombre_yaml>.parquet, donde <prefijo> es lo que
precede al primer "_" en el nombre del YAML (eX_1.yaml -> results/eX/).

Uso:
    python experiments/run.py config/eX_1.yaml config/eX_2.yaml ...
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.network import generate_network, TopologyType  # noqa: E402
from qooperate.payoff import PayoffMatrix  # noqa: E402
from qooperate.simulation import Simulation  # noqa: E402
from qooperate.utils import load_config, generate_bin_edges  # noqa: E402

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def run_one(yaml_path: Path) -> Path:
    cfg = load_config(yaml_path)

    topology = TopologyType(cfg["topology"])
    rng = np.random.default_rng(cfg["seed"])
    graph = generate_network(
        topology, n=cfg["n_agents"], k=cfg["k"], seed=cfg["seed"], ws_beta=cfg.get("ws_beta", 0.1)
    )

    coop_n_div = cfg.get("coop_n_divisions", 2)
    reward_n_div = cfg.get("reward_n_divisions", 2)
    coop_bins = generate_bin_edges(coop_n_div, hi=1.0)
    reward_bins = generate_bin_edges(reward_n_div, hi=5.0)

    sim = Simulation(
        graph=graph,
        agent_params={"alpha": cfg["alpha"], "gamma": cfg["gamma"], "epsilon": cfg["epsilon"]},
        payoff_matrix=PayoffMatrix(),
        rng=rng,
        coop_bins=coop_bins,
        reward_bins=reward_bins,
        reward_window=cfg["reward_window"],
        sample_every=cfg.get("sample_every", 1),
        rho=cfg.get("rho", 1),
    )
    result = sim.run(cfg["n_rounds"], show_progress=True)

    n_points = len(result.rounds)
    df = pd.DataFrame(
        {
            "topology": [topology.value] * n_points,
            "n_agents": [cfg["n_agents"]] * n_points,
            "k": [cfg["k"]] * n_points,
            "alpha": [cfg["alpha"]] * n_points,
            "epsilon": [cfg["epsilon"]] * n_points,
            "gamma": [cfg["gamma"]] * n_points,
            "rho": [cfg.get("rho", 1)] * n_points,
            "seed": [cfg["seed"]] * n_points,
            "n_rounds": [cfg["n_rounds"]] * n_points,
            "reward_window": [cfg["reward_window"]] * n_points,
            "sample_every": [cfg.get("sample_every", 1)] * n_points,
            "coop_n_divisions": [coop_n_div] * n_points,
            "reward_n_divisions": [reward_n_div] * n_points,
            "round": result.rounds,
            "cooperation_rate": result.cooperation_rate,
            "gini_window": result.gini_window,
            "mean_reward": result.mean_reward,
        }
    )

    prefix = yaml_path.stem.split("_")[0]
    out_dir = RESULTS_DIR / prefix
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{yaml_path.stem}.parquet"
    df.to_parquet(out_path, index=False)
    return out_path


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for arg in sys.argv[1:]:
        yaml_path = Path(arg)
        out_path = run_one(yaml_path)
        print(f"{yaml_path} -> {out_path}")


if __name__ == "__main__":
    main()
