from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from PySide6 import QtCore, QtWidgets
import pyqtgraph as pg

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from qooperate.network import TopologyType, generate_network  # noqa: E402
from qooperate.utils import (  # noqa: E402
    StateRepresentation,
    decode_state,
    n_states as compute_n_states,
    parse_state_representation,
)


@dataclass
class ReplayData:
    parquet_path: Path
    df: pd.DataFrame
    graph: nx.Graph
    positions: np.ndarray
    rounds: np.ndarray
    cooperation_rate: np.ndarray
    gini_window: np.ndarray
    delta_q: np.ndarray
    state_visits: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    cumulative_reward_history: np.ndarray
    checkpoint_rounds: np.ndarray
    state_labels: list[str]
    reward_window: int


def _sparse_ticks(size: int, max_ticks: int = 12) -> list[int]:
    if size <= 0:
        return []
    if size <= max_ticks:
        return list(range(size))
    ticks = np.linspace(0, size - 1, max_ticks, dtype=int)
    return list(dict.fromkeys(ticks.tolist()))


def _format_state_label(values: tuple[int, int, int, int], representation: StateRepresentation) -> str:
    active = values[: representation.value]
    parts = []
    for i, value in enumerate(active):
        if i < 2:
            parts.append("C" if value == 0 else "D")
        else:
            parts.append(str(value))
    return "(" + ",".join(parts) + ")"


def build_state_labels(representation: StateRepresentation, n_s3: int, n_s4: int) -> list[str]:
    labels = []
    for idx in range(compute_n_states(representation, n_s3, n_s4)):
        labels.append(_format_state_label(decode_state(idx, representation, n_s3, n_s4), representation))
    return labels


def _color_lerp(start: tuple[int, int, int], end: tuple[int, int, int], t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0.0, 1.0)[:, None]
    start_arr = np.asarray(start, dtype=float)
    end_arr = np.asarray(end, dtype=float)
    return np.round(start_arr + (end_arr - start_arr) * t).astype(np.uint8)


def _load_replay_data(parquet_path: Path) -> ReplayData:
    df = pd.read_parquet(parquet_path).sort_values("round").reset_index(drop=True)
    if df.empty:
        raise ValueError(f"El parquet no tiene filas: {parquet_path}")

    learning_path = parquet_path.with_name(f"learning_{parquet_path.stem}.npz")
    replay_path = parquet_path.with_name(f"replay_{parquet_path.stem}.npz")
    if not learning_path.exists():
        raise FileNotFoundError(f"No existe el artefacto de aprendizaje asociado: {learning_path}")
    if not replay_path.exists():
        raise FileNotFoundError(f"No existe el replay asociado: {replay_path}")

    with np.load(learning_path) as learning, np.load(replay_path) as replay:
        delta_q = np.asarray(learning["delta_q"], dtype=float)
        state_visits = np.asarray(learning["state_visits"], dtype=float)
        checkpoint_rounds = np.asarray(learning["rounds"], dtype=int)

        actions = np.asarray(replay["actions"], dtype=np.int8)
        rewards = np.asarray(replay["rewards"], dtype=float)
        cumulative_reward_history = np.asarray(replay["cumulative_reward_history"], dtype=float)
        rounds = np.asarray(replay["rounds"], dtype=int)

    topology = TopologyType(df["topology"].iat[0])
    state_representation = parse_state_representation(df["state_representation"].iat[0])
    n_agents = int(df["n_agents"].iat[0])
    k = int(df["k"].iat[0])
    seed = int(df["seed"].iat[0])
    ws_beta = float(df.get("ws_beta", pd.Series([0.1])).iat[0])
    coop_n_divisions = int(df["coop_n_divisions"].iat[0])
    reward_n_divisions = int(df["reward_n_divisions"].iat[0])
    reward_window = int(df["reward_window"].iat[0])

    n_s3 = coop_n_divisions + 1
    n_s4 = reward_n_divisions + 1
    n_states = compute_n_states(state_representation, n_s3, n_s4)

    if delta_q.ndim != 2 or state_visits.ndim != 2:
        raise ValueError("Los artefactos de aprendizaje deben ser matrices 2D")
    if delta_q.shape != state_visits.shape:
        raise ValueError(f"delta_q y state_visits deben tener la misma forma, recibieron {delta_q.shape} y {state_visits.shape}")
    if delta_q.shape[1] != n_states:
        raise ValueError(f"La cantidad de estados en los artefactos ({delta_q.shape[1]}) no coincide con n_states={n_states}")
    if len(checkpoint_rounds) != delta_q.shape[0]:
        raise ValueError(f"Los checkpoints ({len(checkpoint_rounds)}) no coinciden con la cantidad de filas del learning ({delta_q.shape[0]})")
    if actions.ndim != 2 or rewards.ndim != 2 or cumulative_reward_history.ndim != 2:
        raise ValueError("El replay debe contener matrices 2D para acciones, rewards y acumulado")
    if actions.shape != rewards.shape or actions.shape != cumulative_reward_history.shape:
        raise ValueError("actions, rewards y cumulative_reward_history deben tener la misma forma")
    if actions.shape[0] != len(rounds):
        raise ValueError(f"El replay tiene {actions.shape[0]} rondas pero rounds tiene {len(rounds)} entradas")
    if actions.shape[1] != n_agents:
        raise ValueError(f"El replay tiene {actions.shape[1]} agentes pero el parquet declara n_agents={n_agents}")

    graph = generate_network(topology, n=n_agents, k=k, seed=seed, ws_beta=ws_beta)
    layout = nx.spring_layout(graph, seed=seed, dim=2)
    positions = np.array([layout[i] for i in range(n_agents)], dtype=float)

    state_labels = build_state_labels(state_representation, n_s3, n_s4)

    return ReplayData(
        parquet_path=parquet_path,
        df=df,
        graph=graph,
        positions=positions,
        rounds=rounds,
        cooperation_rate=np.asarray(df["cooperation_rate"], dtype=float),
        gini_window=np.asarray(df["gini_window"], dtype=float),
        delta_q=delta_q,
        state_visits=state_visits,
        actions=actions,
        rewards=rewards,
        cumulative_reward_history=cumulative_reward_history,
        checkpoint_rounds=checkpoint_rounds,
        state_labels=state_labels,
        reward_window=reward_window,
    )


class ReplayWindow(QtWidgets.QMainWindow):
    def __init__(self, data: ReplayData):
        super().__init__()
        self.data = data
        self.frame = 0
        self.playing = False
        self.base_interval_ms = 80
        self.speed = 1.0
        self.recent_window = max(1, data.reward_window)

        self.setWindowTitle(f"QOOPERATE Replay — {data.parquet_path.stem}")
        self.resize(1500, 900)

        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        root.addWidget(splitter, 1)

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground((255, 255, 255, 0))
        self.graph_widget.hideAxis("bottom")
        self.graph_widget.hideAxis("left")
        self.graph_widget.setAspectLocked(True)
        self.graph_widget.showGrid(x=False, y=False)
        self.graph_widget.setMenuEnabled(False)
        self.graph_widget.setMouseEnabled(x=False, y=False)
        splitter.addWidget(self.graph_widget)

        right = pg.GraphicsLayoutWidget()
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        self.coop_plot = right.addPlot(row=0, col=0)
        self.coop_plot.setTitle("Cooperación + Gini")
        self.coop_plot.setLabel("bottom", "Ronda")
        self.coop_plot.setLabel("left", "Valor")
        self.coop_plot.showGrid(x=True, y=True, alpha=0.2)
        self.coop_plot.addLegend(offset=(8, 8))
        self.coop_curve = self.coop_plot.plot(pen=pg.mkPen((46, 204, 113), width=2), name="Cooperación")
        self.gini_curve = self.coop_plot.plot(pen=pg.mkPen((231, 76, 60), width=2, style=QtCore.Qt.PenStyle.DashLine), name="Gini")
        self.coop_cursor = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen((80, 80, 80, 160), width=1))
        self.coop_plot.addItem(self.coop_cursor)

        self.delta_plot = right.addPlot(row=1, col=0)
        self.delta_plot.setTitle("Heatmap de aprendizaje")
        self.delta_plot.setLabel("bottom", "Ronda")
        self.delta_plot.setLabel("left", "Estado")
        self.delta_plot.showGrid(x=False, y=False)
        self.delta_image = pg.ImageItem()
        self.delta_plot.addItem(self.delta_image)
        self.delta_cursor = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen((80, 80, 80, 160), width=1))
        self.delta_plot.addItem(self.delta_cursor)

        self.visits_plot = right.addPlot(row=2, col=0)
        self.visits_plot.setTitle("Frecuencia de estados")
        self.visits_plot.setLabel("bottom", "Ronda")
        self.visits_plot.setLabel("left", "Estado")
        self.visits_plot.showGrid(x=False, y=False)
        self.visits_image = pg.ImageItem()
        self.visits_plot.addItem(self.visits_image)
        self.visits_cursor = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen((80, 80, 80, 160), width=1))
        self.visits_plot.addItem(self.visits_cursor)

        self._edge_item = None
        self._scatter = None
        self._setup_graph_items()
        self._setup_heatmaps()

        n_rounds = len(self.data.rounds)
        n_states = len(self.data.state_labels)
        self.coop_plot.setXRange(1, n_rounds, padding=0)
        self.coop_plot.setYRange(0, 1, padding=0.02)
        for plot in (self.delta_plot, self.visits_plot):
            plot.setXRange(1, n_rounds, padding=0)
            plot.setYRange(0, n_states, padding=0)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(10)
        root.addLayout(controls)

        self.play_button = QtWidgets.QPushButton("Play")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.pause_button.setEnabled(False)
        self.play_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        controls.addWidget(self.play_button)
        controls.addWidget(self.pause_button)

        controls.addWidget(QtWidgets.QLabel("Ronda"))
        self.round_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.round_slider.setMinimum(1)
        self.round_slider.setMaximum(len(self.data.rounds))
        self.round_slider.setValue(1)
        self.round_slider.valueChanged.connect(self.set_round_from_slider)
        controls.addWidget(self.round_slider, 1)
        self.round_label = QtWidgets.QLabel("1 / %d" % len(self.data.rounds))
        controls.addWidget(self.round_label)

        controls.addWidget(QtWidgets.QLabel("Velocidad"))
        self.speed_combo = QtWidgets.QComboBox()
        self.speed_options = [(0.25, "0.25×"), (0.5, "0.5×"), (1.0, "1×"), (2.0, "2×"), (4.0, "4×"), (8.0, "8×")]
        for value, label in self.speed_options:
            self.speed_combo.addItem(label, value)
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.currentIndexChanged.connect(self._speed_changed)
        controls.addWidget(self.speed_combo)

        self.hide_graph = QtWidgets.QCheckBox("Ocultar grafo")
        self.hide_graph.stateChanged.connect(self._toggle_graph)
        controls.addWidget(self.hide_graph)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.step)

        self._update_frame(0)

    def _setup_graph_items(self) -> None:
        positions = self.data.positions
        edges = list(self.data.graph.edges())
        if edges:
            xs = []
            ys = []
            for u, v in edges:
                xs.extend([positions[u, 0], positions[v, 0], np.nan])
                ys.extend([positions[u, 1], positions[v, 1], np.nan])
            self._edge_item = pg.PlotCurveItem(x=np.asarray(xs), y=np.asarray(ys), pen=pg.mkPen((150, 150, 150, 100), width=1))
            self.graph_widget.addItem(self._edge_item)

        self._scatter = pg.ScatterPlotItem(pxMode=True, pen=pg.mkPen(None))
        self.graph_widget.addItem(self._scatter)
        self.graph_widget.setXRange(float(np.min(positions[:, 0])) - 0.1, float(np.max(positions[:, 0])) + 0.1, padding=0)
        self.graph_widget.setYRange(float(np.min(positions[:, 1])) - 0.1, float(np.max(positions[:, 1])) + 0.1, padding=0)

    def _setup_heatmaps(self) -> None:
        n_states = len(self.data.state_labels)
        checkpoints = self.data.checkpoint_rounds
        x_ticks = _sparse_ticks(len(checkpoints), max_ticks=10)
        x_tick_positions = [float(checkpoints[i]) for i in x_ticks]
        x_tick_labels = [str(int(checkpoints[i])) for i in x_ticks]
        y_ticks = _sparse_ticks(n_states, max_ticks=12)
        y_tick_labels = [self.data.state_labels[i] for i in y_ticks]

        for plot in (self.delta_plot, self.visits_plot):
            plot.setLimits(xMin=0, xMax=max(int(self.data.rounds[-1]), 1), yMin=0, yMax=max(n_states, 1))
            plot.getAxis("bottom").setTicks([list(zip(x_tick_positions, x_tick_labels))])
            plot.getAxis("left").setTicks([list(zip(y_ticks, y_tick_labels))])

        self.delta_cmap = pg.ColorMap(
            [0.0, 0.5, 1.0],
            np.array([
                [59, 76, 192, 255],
                [255, 255, 255, 255],
                [180, 4, 38, 255],
            ], dtype=np.ubyte),
        )
        self.visits_cmap = pg.ColorMap(
            [0.0, 0.5, 1.0],
            np.array([
                [68, 1, 84, 255],
                [33, 145, 140, 255],
                [253, 231, 37, 255],
            ], dtype=np.ubyte),
        )
        self.delta_image.setLookupTable(self.delta_cmap.getLookupTable(0.0, 1.0, 256))
        self.visits_image.setLookupTable(self.visits_cmap.getLookupTable(0.0, 1.0, 256))

    def _checkpoint_index(self, round_index: int) -> int:
        checkpoint_round = round_index + 1
        return int(np.searchsorted(self.data.checkpoint_rounds, checkpoint_round, side="right") - 1)

    def _update_frame(self, frame: int) -> None:
        n_rounds = len(self.data.rounds)
        frame = max(0, min(frame, n_rounds - 1))
        self.frame = frame

        current_round = frame + 1
        self.round_slider.blockSignals(True)
        self.round_slider.setValue(current_round)
        self.round_slider.blockSignals(False)
        self.round_label.setText(f"{current_round} / {n_rounds}")

        actions = self.data.actions[: current_round]
        cumulative = self.data.cumulative_reward_history[frame]
        window_start = max(0, current_round - self.recent_window)
        recent = actions[window_start:current_round]
        mean_actions = recent.mean(axis=0) if len(recent) else np.zeros(actions.shape[1], dtype=float)
        colors = _color_lerp((46, 204, 113), (231, 76, 60), mean_actions)
        brushes = [pg.mkBrush(int(r), int(g), int(b), 230) for r, g, b in colors]

        if cumulative.size:
            max_reward = float(np.max(cumulative))
            if max_reward <= 0:
                sizes = np.full(cumulative.shape, 10.0)
            else:
                sizes = 8.0 + 18.0 * np.sqrt(cumulative / max_reward)
        else:
            sizes = np.full(actions.shape[1], 10.0)

        pos = self.data.positions
        self._scatter.setData(x=pos[:, 0], y=pos[:, 1], size=sizes, brush=brushes)

        checkpoint_index = self._checkpoint_index(frame)
        if checkpoint_index >= 0:
            rounds = self.data.checkpoint_rounds[: checkpoint_index + 1]
            self.coop_curve.setData(rounds, self.data.cooperation_rate[: checkpoint_index + 1])
            self.gini_curve.setData(rounds, self.data.gini_window[: checkpoint_index + 1])

            delta = self.data.delta_q[: checkpoint_index + 1].T
            visits = self.data.state_visits[: checkpoint_index + 1].T
            self._update_heatmap(self.delta_image, delta, self.delta_plot, self.data.checkpoint_rounds[0], rounds[-1])
            self._update_heatmap(self.visits_image, visits, self.visits_plot, self.data.checkpoint_rounds[0], rounds[-1])
            self.coop_cursor.setPos(current_round)
            self.delta_cursor.setPos(current_round)
            self.visits_cursor.setPos(current_round)
        else:
            self.coop_curve.setData([], [])
            self.gini_curve.setData([], [])
            blank = np.zeros((len(self.data.state_labels), 1), dtype=float)
            self._update_heatmap(self.delta_image, blank, self.delta_plot, 1, 1)
            self._update_heatmap(self.visits_image, blank, self.visits_plot, 1, 1)
            self.coop_cursor.setPos(current_round)
            self.delta_cursor.setPos(current_round)
            self.visits_cursor.setPos(current_round)

    def _update_heatmap(self, image: pg.ImageItem, data: np.ndarray, plot: pg.PlotItem, x0: int, x1: int) -> None:
        levels = None
        if data.size:
            low = float(np.nanmin(data))
            high = float(np.nanmax(data))
            if low == high:
                high = low + 1.0
            levels = (low, high)
        image.setImage(data, autoLevels=False, levels=levels)
        image.setRect(QtCore.QRectF(float(x0), 0.0, float(max(x1 - x0, 1)), float(data.shape[0])))

    def set_round_from_slider(self, value: int) -> None:
        self._update_frame(value - 1)

    def _speed_changed(self) -> None:
        self.speed = float(self.speed_combo.currentData())
        if self.playing:
            self.timer.start(self._timer_interval())

    def _timer_interval(self) -> int:
        return max(1, int(self.base_interval_ms / self.speed))

    def play(self) -> None:
        if self.playing:
            return
        self.playing = True
        self.play_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.timer.start(self._timer_interval())

    def pause(self) -> None:
        self.playing = False
        self.timer.stop()
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def step(self) -> None:
        if self.frame >= len(self.data.rounds) - 1:
            self.pause()
            return
        self._update_frame(self.frame + 1)

    def _toggle_graph(self, state: int) -> None:
        self.graph_widget.setVisible(state == QtCore.Qt.CheckState.Unchecked.value)


def launch_viewer(parquet_path: Path) -> None:
    pg.setConfigOptions(antialias=True, imageAxisOrder="row-major")
    data = _load_replay_data(Path(parquet_path))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = ReplayWindow(data)
    window.show()
    app.exec()


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python experiments/viewer.py <parquet>")
        raise SystemExit(1)
    launch_viewer(Path(sys.argv[1]))


if __name__ == "__main__":
    main()



