"""
Aexyron - Layer 1: Streaming Telemetry Bus Definitions and Schemas.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import json
import time

# Kafka Topic Definitions
TOPIC_TELEMETRY_RAW = "aexyron.telemetry.raw"
TOPIC_TELEMETRY_AGGREGATED = "aexyron.telemetry.aggregated"
TOPIC_ANOMALIES = "aexyron.anomalies"
TOPIC_REMEDIATION_COMMANDS = "aexyron.remediation.commands"
TOPIC_BLACK_BOX_LOGS = "aexyron.blackbox.logs"


@dataclass
class InterfaceMetricSample:
    """Telemetry sample collected via gNMI / sFlow."""
    device_id: str
    interface_id: str
    timestamp: float
    octets_rx: int
    octets_tx: int
    packets_rx: int
    packets_tx: int
    errors_rx: int
    errors_tx: int
    drops_rx: int
    drops_tx: int
    queue_occupancy_pct: float
    optical_power_dbm: float
    carrier_transitions: int = 0

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "InterfaceMetricSample":
        parsed = json.loads(data)
        return cls(**parsed)


@dataclass
class EBPFDropSample:
    """Socket-level kernel drop sample collected via eBPF."""
    host_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    drop_reason: str
    tcp_rtt_us: float
    retransmissions: int
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, data: str) -> "EBPFDropSample":
        parsed = json.loads(data)
        return cls(**parsed)
