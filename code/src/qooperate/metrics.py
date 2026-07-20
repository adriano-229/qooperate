import numpy as np


def compute_gini(values: np.ndarray) -> float:
    """Índice de Gini, O(N log N) vía valores ordenados. G=0 si la media es 0."""
    values = np.asarray(values, dtype=float)
    n = len(values)
    mean = values.mean()
    if mean == 0:
        return 0.0
    sorted_values = np.sort(values)
    index = np.arange(1, n + 1)
    gini_sum = np.sum((2 * index - n - 1) * sorted_values)
    return gini_sum / (n**2 * mean)


def moving_average(series: np.ndarray, window: int) -> np.ndarray:
    """Media móvil causal, ventana parcial al inicio. Solo para graficar (plot_smoothing)."""
    series = np.asarray(series, dtype=float)
    if window <= 1:
        return series.copy()
    cumsum = np.cumsum(np.insert(series, 0, 0.0))
    result = np.empty_like(series)
    for t in range(len(series)):
        lo = max(0, t - window + 1)
        result[t] = (cumsum[t + 1] - cumsum[lo]) / (t + 1 - lo)
    return result


def temporal_stability(coop_rate: np.ndarray, window: int) -> float:
    return coop_rate[-window:].std()
