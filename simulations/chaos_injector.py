"""
Aexyron - Benchmarking & Chaos Testing Fault Injector.
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time


class FailureType(str, Enum):
    PHYSICAL_LINK_CUT = "physical_link_cut"
    SILENT_PACKET_DROP = "silent_packet_drop"
    BGP_ROUTE_FLAP = "bgp_route_flap"
    ECMP_POLARIZATION = "ecmp_polarization"
    BUFFER_INCAST = "buffer_incast"


class ChaosFaultInjector:
    """
    Injects controlled network anomalies into the Containerlab testbed
    to evaluate detection, prediction, and automated self-healing.
    """

    def __init__(self):
        self.active_injections: List[Dict[str, Any]] = []

    def inject_fault(
        self,
        failure_type: FailureType,
        target_component: str,
        duration_seconds: int = 30,
        severity: float = 0.15,
    ) -> Dict[str, Any]:
        fault_record = {
            "injection_id": f"fault_{int(time.time() * 1000)}",
            "type": failure_type.value,
            "target": target_component,
            "timestamp": time.time(),
            "duration_seconds": duration_seconds,
            "severity": severity,
            "status": "ACTIVE",
        }
        self.active_injections.append(fault_record)
        return fault_record

    def clear_all(self):
        self.active_injections.clear()
