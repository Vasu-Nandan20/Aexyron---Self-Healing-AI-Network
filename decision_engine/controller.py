"""
Aexyron - Layer 6: Autonomy Controller (Levels L0 to L4).
"""

from enum import Enum
from typing import Dict, Any, Optional


class AutonomyLevel(str, Enum):
    L0_ALERT_ONLY = "L0_ALERT_ONLY"
    L1_OPERATOR_ASSISTED = "L1_OPERATOR_ASSISTED"
    L2_BOUNDED_AUTONOMOUS = "L2_BOUNDED_AUTONOMOUS"
    L3_CONDITIONAL_AUTONOMOUS = "L3_CONDITIONAL_AUTONOMOUS"
    L4_FULLY_AUTONOMOUS = "L4_FULLY_AUTONOMOUS"


class AutonomyController:
    """Manages system autonomy levels and authorizes execution based on configured mode."""

    def __init__(self, current_level: AutonomyLevel = AutonomyLevel.L4_FULLY_AUTONOMOUS):
        self.current_level = current_level

    def can_auto_execute(self, action_risk_score: float) -> Dict[str, Any]:
        """
        Determines whether the system may automatically dispatch commands
        without waiting for manual operator confirmation.
        """
        if self.current_level == AutonomyLevel.L0_ALERT_ONLY:
            return {"can_execute": False, "reason": "L0 active: Manual operator execution required"}

        if self.current_level == AutonomyLevel.L1_OPERATOR_ASSISTED:
            return {"can_execute": False, "reason": "L1 active: Requires 1-click human approval"}

        if self.current_level == AutonomyLevel.L2_BOUNDED_AUTONOMOUS:
            if action_risk_score <= 0.2:
                return {"can_execute": True, "mode": "BOUNDED_LOW_RISK"}
            return {"can_execute": False, "reason": "L2 active: Risk score exceeds bounded threshold"}

        if self.current_level == AutonomyLevel.L3_CONDITIONAL_AUTONOMOUS:
            if action_risk_score <= 0.5:
                return {"can_execute": True, "mode": "CONDITIONAL_AUTO_WITH_OVERRIDE_WINDOW"}
            return {"can_execute": False, "reason": "L3 active: Risk score exceeds conditional threshold"}

        if self.current_level == AutonomyLevel.L4_FULLY_AUTONOMOUS:
            return {"can_execute": True, "mode": "FULL_AUTONOMOUS_CLOSED_LOOP"}

        return {"can_execute": False, "reason": "Unknown autonomy level"}
