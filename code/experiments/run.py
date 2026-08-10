from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.network import generate_network, TopologyType  # noqa: E402
from qooperate.payoff import PayoffMatrix  # noqa: E402
from qooperate.simulation import Simulation  # noqa: E402
from qooperate.utils import (  # noqa: E402
    generate_bin_edges,
    load_config,
    parse_state_representation,
)

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results" / "data"


def run_one(yaml_path: Path) -> Path:
    cfg = load_config(yaml_path)

    topology = TopologyType(cfg["topology"])
    if "state_representation" not in cfg:
        raise KeyError(f"{yaml_path} no define state_representation")
    state_representation = parse_state_representation(cfg["state_representation"])

    rng = np.random.default_rng(cfg["seed"])

    graph = generate_network(
        topology,
        n=cfg["n_agents"],
        k=cfg["k"],
        seed=cfg["seed"],
        ws_beta=cfg.get("ws_beta", 0.1),
    )

    coop_n_div = cfg.get("coop_n_divisions", 2)
    reward_n_div = cfg.get("reward_n_divisions", 2)

    coop_bins = generate_bin_edges(coop_n_div, hi=1.0)
    reward_bins = generate_bin_edges(reward_n_div, hi=5.0)

    sim = Simulation(
        graph=graph,
        agent_params={
            "alpha": cfg["alpha"],
            "gamma": cfg["gamma"],
            "epsilon": cfg["epsilon"],
        },
        payoff_matrix=PayoffMatrix(),
        rng=rng,
        coop_bins=coop_bins,
        reward_bins=reward_bins,
        reward_window=cfg["reward_window"],
        state_representation=state_representation,
        sample_every=cfg.get("sample_every", 1),
        rho=cfg.get("rho", 1),
    )

    result = sim.run(cfg["n_rounds"], show_progress=True)

    n_points = len(result.rounds)

    df = pd.DataFrame(
        {
            "topology": [topology.value] * n_points,
            "state_representation": [state_representation.name] * n_points,
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

    np.savez_compressed(
        out_dir / f"learning_{yaml_path.stem}.npz",
        delta_q=result.delta_q,
        state_visits=result.state_visits,
        rounds=result.rounds,
    )

    np.savez_compressed(
        out_dir / f"replay_{yaml_path.stem}.npz",
        actions=result.actions,
        rewards=result.rewards,
        cumulative_reward_history=result.cumulative_reward_history,
        rounds=np.arange(1, cfg["n_rounds"] + 1, dtype=int),
    )

    return out_path


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    out_path = None
    for arg in sys.argv[1:]:
        yaml_path = Path(arg)
        out_path = run_one(yaml_path)
        print(f"{yaml_path} -> {out_path}")

    if out_path is not None and len(sys.argv[1:]) == 1 and os.environ.get("QOOPERATE_NO_VIEWER") != "1":
        try:
            from viewer import launch_viewer

            launch_viewer(out_path)
        except Exception as exc:
            print(f"No se pudo abrir el visor: {exc}")


if __name__ == "__main__":
    main()
