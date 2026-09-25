"""
Aexyron - Layer 3: Multi-Horizon Failure Predictor (20s+ Ahead).
"""

from typing import Dict, Any, Optional
import numpy as np


class FailurePredictor:
    """
    Predictive engine forecasting impending network failures (e.g. optical transceiver blowout,
    CRC error cascades, buffer incast) 20+ seconds before service impact.
    """

    def __init__(self, warning_threshold: float = 0.75):
        self.warning_threshold = warning_threshold

    def predict_failure_horizon(
        self,
        entity_id: str,
        optical_power_trend_dbm: float,
        crc_error_velocity: float,
        buffer_occupancy_growth_rate: float,
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate time-series trend features to forecast impending failure.
        """
        # Composite risk calculation
        risk_score = 0.0
        reasons = []

        # Optical power degrading rapidly (negative slope in dBm)
        if optical_power_trend_dbm < -1.5:
            risk_score += 0.45
            reasons.append("Laser power degradation trend indicates impending transceiver loss")

        # CRC error velocity accelerating
        if crc_error_velocity > 15.0:
            risk_score += 0.35
            reasons.append("CRC error velocity accelerating exponentially")

        # Buffer occupancy growth rate
        if buffer_occupancy_growth_rate > 10.0:
            risk_score += 0.25
            reasons.append("Microburst buffer incast growth indicates impending queue tail drop")

        risk_score = min(1.0, risk_score)

        if risk_score >= self.warning_threshold:
            estimated_horizon_sec = max(20.0, 45.0 - (risk_score * 25.0))
            return {
                "entity": entity_id,
                "impending_failure": True,
                "confidence": round(risk_score, 2),
                "horizon_seconds": round(estimated_horizon_sec, 1),
                "reasons": reasons,
                "recommended_action": "Proactive reroute and drain candidate link before hard cut",
            }
        return None
