"""
Aexyron - Layer 4: Blast Radius and Operational Risk Scorer.
"""

from typing import Dict, Any, List
from digital_twin.models import OperationalStatus


class RiskScorer:
    """Scores candidate failure blast radius and operational disruption."""

    @staticmethod
    def calculate_risk(
        total_capacity_gbps: int,
        drained_capacity_gbps: int,
        affected_prefixes: int,
        min_remaining_ecmp: int,
    ) -> Dict[str, Any]:
        drained_ratio = (
            drained_capacity_gbps / total_capacity_gbps if total_capacity_gbps > 0 else 1.0
        )
        # Risk is elevated if capacity drained > 25% or remaining ECMP paths < 2
        capacity_risk = min(1.0, drained_ratio / 0.5)
        path_redundancy_risk = 0.0 if min_remaining_ecmp >= 1 else 1.0

        composite_risk = (capacity_risk * 0.6) + (path_redundancy_risk * 0.4)

        return {
            "drained_capacity_ratio": round(drained_ratio, 4),
            "min_remaining_ecmp_paths": min_remaining_ecmp,
            "affected_prefixes": affected_prefixes,
            "composite_risk_score": round(composite_risk, 3),
            "is_within_safety_limits": (drained_ratio <= 0.25 and min_remaining_ecmp >= 1),
        }
