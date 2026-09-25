"""
Aexyron - Layer 7: Forensic Incident Replay Engine.
"""

from typing import Dict, Any, List, Optional
from .hash_chain import NetworkBlackBoxLedger, BlackBoxRecord


class ForensicReplayEngine:
    """
    Deterministic replay tool that steps through recorded events,
    allowing NOC engineers and auditors to reconstruct incident timelines second-by-second.
    """

    def __init__(self, ledger: NetworkBlackBoxLedger):
        self.ledger = ledger

    def replay_timeline(self, start_index: int = 0, event_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        timeline = []
        for record in self.ledger.chain[start_index:]:
            if event_filter and record.event_type != event_filter:
                continue

            entry = {
                "step": record.index,
                "timestamp": record.timestamp,
                "event_type": record.event_type,
                "payload": record.payload,
                "hash_verified": record.compute_hash() == record.hash,
            }
            timeline.append(entry)
        return timeline

    def find_incident_events(self, incident_id: str) -> List[BlackBoxRecord]:
        return [
            rec for rec in self.ledger.chain
            if rec.payload.get("incident_id") == incident_id
        ]
