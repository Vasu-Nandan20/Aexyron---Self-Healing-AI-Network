"""
Aexyron - Layer 6: Open Policy Agent (OPA) Integration Client.
"""

import time
from typing import Dict, Any, Optional
import requests
import json


class OPAClient:
    """
    Evaluates candidate remediation actions against OPA policies.
    Provides local deterministic fallback if OPA HTTP server is offline.
    """

    _server_reachable: Optional[bool] = None
    _last_check_timestamp: float = 0.0
    _COOLDOWN_SECONDS: float = 30.0

    def __init__(self, opa_url: str = "http://localhost:8181/v1/data/aexyron/guardrails/allow"):
        self.opa_url = opa_url

    def evaluate_policy(self, candidate_action: Dict[str, Any], recent_actions_count: int = 0) -> Dict[str, Any]:
        payload = {
            "input": {
                "candidate_action": {
                    "drained_capacity_ratio": candidate_action.get("drained_capacity_ratio", 0.0),
                    "affected_gpu_nodes": candidate_action.get("affected_gpu_nodes", 0),
                    "min_remaining_ecmp_paths": candidate_action.get("min_remaining_ecmp_paths", 2),
                },
                "recent_actions_count_60s": recent_actions_count,
            }
        }

        now = time.time()
        should_try_server = (
            OPAClient._server_reachable is not False
            or (now - OPAClient._last_check_timestamp > OPAClient._COOLDOWN_SECONDS)
        )

        if should_try_server:
            try:
                resp = requests.post(self.opa_url, json=payload, timeout=0.5)
                if resp.status_code == 200:
                    OPAClient._server_reachable = True
                    OPAClient._last_check_timestamp = now
                    result = resp.json().get("result", False)
                    return {"allowed": bool(result), "source": "OPA_SERVER"}
            except Exception:
                OPAClient._server_reachable = False
                OPAClient._last_check_timestamp = now

        # Fallback local policy evaluation matching Rego rules exactly
        allowed = (
            candidate_action.get("drained_capacity_ratio", 0.0) <= 0.25
            and candidate_action.get("affected_gpu_nodes", 0) == 0
            and candidate_action.get("min_remaining_ecmp_paths", 1) >= 1
            and recent_actions_count < 3
        )
        return {
            "allowed": allowed,
            "source": "LOCAL_POLICY_ENGINE",
            "drained_ratio_ok": candidate_action.get("drained_capacity_ratio", 0.0) <= 0.25,
            "redundancy_ok": candidate_action.get("min_remaining_ecmp_paths", 1) >= 1,
            "rate_limit_ok": recent_actions_count < 3,
        }
