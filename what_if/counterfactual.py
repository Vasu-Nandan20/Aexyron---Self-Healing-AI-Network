"""
Aexyron - Layer 4: Counterfactual Reasoning Engine.
"""

from typing import Dict, Any, List, Optional
import copy
from digital_twin.graph_sync import DigitalTwinGraph
from digital_twin.models import OperationalStatus
from .risk_scorer import RiskScorer


class CounterfactualEngine:
    """
    Explores hypothetical failure states on an in-memory clone of the digital twin,
    computing optimal reroute plans and risk scores before real failures strike.
    """

    def __init__(self, digital_twin: DigitalTwinGraph):
        self.twin = digital_twin

    def evaluate_hypothetical_link_cut(self, link_id: str) -> Optional[Dict[str, Any]]:
        """
        Simulate cutting link_id, find alternative paths, and pre-compute recovery plan.
        """
        if link_id not in self.twin.links:
            return None

        sim_twin = self.twin.clone()
        target_link = sim_twin.links[link_id]
        sim_twin.set_link_status(link_id, OperationalStatus.DOWN)

        src = target_link.source_device
        tgt = target_link.target_device
        
        # In Clos fabric, evaluate remaining paths from source leaf to peer leaves
        leaf_nodes = [d.id for d in sim_twin.devices.values() if d.role.value == "leaf" and d.id != src]
        if leaf_nodes:
            leaf_paths = {leaf: sim_twin.get_ecmp_paths(src, leaf) for leaf in leaf_nodes}
            min_ecmp = min((len(p) for p in leaf_paths.values()), default=1)
            remaining_paths = list(leaf_paths.values())[0] if leaf_paths else []
        else:
            remaining_paths = sim_twin.get_ecmp_paths(src, tgt)
            min_ecmp = len(remaining_paths)

        total_cap = sum(l.capacity_gbps for l in self.twin.links.values())
        drained_cap = target_link.capacity_gbps

        risk_evaluation = RiskScorer.calculate_risk(
            total_capacity_gbps=total_cap,
            drained_capacity_gbps=drained_cap,
            affected_prefixes=1,
            min_remaining_ecmp=min_ecmp,
        )

        recovery_action = {
            "scenario": f"hypothetical_cut_{link_id}",
            "failed_link_id": link_id,
            "source_device": src,
            "target_device": tgt,
            "status": "PRECOMPUTED",
            "alternative_paths_count": len(remaining_paths),
            "alternative_paths": remaining_paths,
            "risk_assessment": risk_evaluation,
            "remediation_command": f"bgp route-map DRAIN-LINK permit 10 set community no-export; interface {target_link.source_interface} shutdown",
        }
        return recovery_action
