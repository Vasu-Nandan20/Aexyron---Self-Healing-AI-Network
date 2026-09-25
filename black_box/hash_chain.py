"""
Aexyron - Layer 7: Cryptographic SHA-256 Hash-Chained Audit Ledger.
"""

from typing import Dict, Any, List, Optional
import hashlib
import json
import time


class BlackBoxRecord:
    """An individual immutable entry in the Black Box ledger."""

    def __init__(self, index: int, prev_hash: str, event_type: str, payload: Dict[str, Any], timestamp: Optional[float] = None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.prev_hash = prev_hash
        self.event_type = event_type
        self.payload = payload
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        serialized_payload = json.dumps(self.payload, sort_keys=True)
        block_string = f"{self.index}|{self.timestamp}|{self.prev_hash}|{self.event_type}|{serialized_payload}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "event_type": self.event_type,
            "payload": self.payload,
            "hash": self.hash,
        }


class NetworkBlackBoxLedger:
    """
    Append-only, cryptographically linked flight recorder for all network events,
    model predictions, counterfactual evaluations, and remediation commands.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self):
        self.chain: List[BlackBoxRecord] = []
        self._create_genesis()

    def _create_genesis(self):
        genesis = BlackBoxRecord(
            index=0,
            prev_hash=self.GENESIS_HASH,
            event_type="GENESIS",
            payload={"system": "Aexyron Self-Healing AI Network", "version": "1.0.0"},
            timestamp=0.0,
        )
        self.chain.append(genesis)

    def append_event(self, event_type: str, payload: Dict[str, Any]) -> BlackBoxRecord:
        prev_record = self.chain[-1]
        record = BlackBoxRecord(
            index=len(self.chain),
            prev_hash=prev_record.hash,
            event_type=event_type,
            payload=payload,
        )
        self.chain.append(record)
        return record

    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify mathematical integrity of the hash chain.
        Returns valid=True if no records have been altered, inserted, or omitted.
        """
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            if curr.prev_hash != prev.hash:
                return {
                    "valid": False,
                    "error": f"Hash chain broken at index {i}: prev_hash mismatch",
                    "corrupted_index": i,
                }

            if curr.compute_hash() != curr.hash:
                return {
                    "valid": False,
                    "error": f"Tampering detected at index {i}: payload altered",
                    "corrupted_index": i,
                }

        return {"valid": True, "total_records": len(self.chain)}
