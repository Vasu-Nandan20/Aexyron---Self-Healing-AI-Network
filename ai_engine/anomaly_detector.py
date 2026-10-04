"""
Aexyron - Layer 3: Fast-Path Anomaly Detection (< 5s Latency Window).
"""

from typing import Dict, Any, Optional
import numpy as np
from sklearn.ensemble import IsolationForest
from .features import WindowedFeatureExtractor


class FastAnomalyDetector:
    """
    Fast-path anomaly detector based on Isolation Forests and streaming features.
    Achieves detection within < 5 seconds of symptom emergence.
    """

    _cached_models: Dict[float, IsolationForest] = {}

    def __init__(self, contamination: float = 0.05):
        self.extractor = WindowedFeatureExtractor(window_size=10)
        self.contamination = contamination
        self.is_fitted = False
        self._warmup_baseline()

    def _warmup_baseline(self):
        """Fit with nominal baseline data so detector is active immediately."""
        if self.contamination in FastAnomalyDetector._cached_models:
            self.model = FastAnomalyDetector._cached_models[self.contamination]
            self.is_fitted = True
            return

        self.model = IsolationForest(
            n_estimators=50,
            contamination=self.contamination,
            random_state=42,
        )
        rng = np.random.RandomState(42)
        means = rng.normal(loc=0.001, scale=0.0003, size=(100, 1))
        stds = rng.normal(loc=0.0002, scale=0.00005, size=(100, 1))
        deltas = rng.normal(loc=0.0, scale=0.0001, size=(100, 1))
        latests = rng.normal(loc=0.001, scale=0.0003, size=(100, 1))
        nominal_data = np.hstack([means, stds, deltas, latests])
        nominal_data = np.clip(nominal_data, 0.0, None)
        self.model.fit(nominal_data)
        FastAnomalyDetector._cached_models[self.contamination] = self.model
        self.is_fitted = True

    def ingest_metric(self, key: str, value: float) -> Optional[Dict[str, Any]]:
        """
        Ingest a metric sample and evaluate if an anomaly is present.
        Returns anomaly dictionary if score indicates anomalous deviation, else None.
        """
        self.extractor.push_metric(key, value)
        features = self.extractor.compute_features(key)
        
        # Check rule-based fast trip for sudden extreme spikes (e.g. drop rate > 5%)
        latest_val = features[3]
        if latest_val > 0.05:  # Over 5% packet drops
            return {
                "entity": key,
                "is_anomaly": True,
                "anomaly_score": 0.99,
                "metric_value": latest_val,
                "reason": "Sudden severe packet drop spike detected",
            }

        if not self.is_fitted:
            return None

        # Isolation Forest prediction: -1 is anomaly, 1 is normal
        pred = self.model.predict([features])[0]
        score = -float(self.model.score_samples([features])[0])

        if pred == -1:
            return {
                "entity": key,
                "is_anomaly": True,
                "anomaly_score": round(score, 4),
                "metric_value": latest_val,
                "reason": "Statistical anomaly detected by Isolation Forest",
            }
        return None
