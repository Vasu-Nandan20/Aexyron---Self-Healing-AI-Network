"""
Aexyron - Layer 3: Feature Engineering Pipeline for Streaming Metrics.
"""

from typing import List, Dict, Any
import numpy as np


class WindowedFeatureExtractor:
    """Extracts sliding window statistical features for fast anomaly detection."""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.history: Dict[str, List[float]] = {}

    def push_metric(self, key: str, value: float):
        if key not in self.history:
            self.history[key] = []
        self.history[key].append(value)
        if len(self.history[key]) > self.window_size:
            self.history[key].pop(0)

    def compute_features(self, key: str) -> np.ndarray:
        series = self.history.get(key, [])
        if not series:
            return np.zeros(4)
        arr = np.array(series)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr)) if len(arr) > 1 else 0.0
        delta = float(arr[-1] - arr[0]) if len(arr) > 1 else 0.0
        latest = float(arr[-1])
        return np.array([mean_val, std_val, delta, latest])
