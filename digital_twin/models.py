"""
Aexyron - Layer 2: Live Digital Twin Models.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class DeviceRole(str, Enum):
    SPINE = "spine"
    LEAF = "leaf"
    HOST = "host"
    GATEWAY = "gateway"


class OperationalStatus(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    DEGRADED = "DEGRADED"


@dataclass
class Interface:
    id: str
    name: str
    device_id: str
    speed_gbps: int
    status: OperationalStatus = OperationalStatus.UP
    mtu: int = 9000
    rx_utilization_pct: float = 0.0
    tx_utilization_pct: float = 0.0
    drop_rate_pct: float = 0.0
    queue_occupancy_pct: float = 0.0


@dataclass
class NetworkLink:
    id: str
    source_device: str
    source_interface: str
    target_device: str
    target_interface: str
    capacity_gbps: int
    latency_ms: float = 0.1
    status: OperationalStatus = OperationalStatus.UP


@dataclass
class Device:
    id: str
    hostname: str
    role: DeviceRole
    management_ip: str
    status: OperationalStatus = OperationalStatus.UP
    asn: int = 65000
    interfaces: Dict[str, Interface] = field(default_factory=dict)
