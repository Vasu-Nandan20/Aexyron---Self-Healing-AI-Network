"""Tests for Layer 7: Network Black Box & Replay."""
from black_box.hash_chain import NetworkBlackBoxLedger
from black_box.replay import ForensicReplayEngine


def test_black_box_cryptographic_integrity():
    ledger = NetworkBlackBoxLedger()
    ledger.append_event("TELEMETRY_SAMPLE", {"device": "spine-01", "loss": 0.0})
    ledger.append_event("ANOMALY_TRIGGERED", {"device": "spine-01", "loss": 0.12})
    ledger.append_event("REMEDIATION_DISPATCHED", {"command": "interface eth1 shutdown"})

    # Verify integrity of untampered chain
    verification = ledger.verify_integrity()
    assert verification["valid"] is True
    assert verification["total_records"] == 4  # Genesis + 3 events

    # Simulate malicious tampering with payload at index 2
    ledger.chain[2].payload["loss"] = 0.0  # Attempt to hide the anomaly
    tampered_verification = ledger.verify_integrity()
    assert tampered_verification["valid"] is False
    assert tampered_verification["corrupted_index"] == 2


def test_forensic_replay():
    ledger = NetworkBlackBoxLedger()
    ledger.append_event("INCIDENT_START", {"incident_id": "INC-100", "node": "leaf-01"})
    ledger.append_event("INCIDENT_RESOLVED", {"incident_id": "INC-100", "mttr": 13.2})

    replay_engine = ForensicReplayEngine(ledger)
    timeline = replay_engine.replay_timeline()
    assert len(timeline) == 3  # Genesis + 2 events
    assert all(t["hash_verified"] for t in timeline)

    incident_records = replay_engine.find_incident_events("INC-100")
    assert len(incident_records) == 2
