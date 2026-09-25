"""
Aexyron - Layer 2: Live Digital Twin Synchronizer and Graph Engine.
"""

from typing import Dict, List, Optional, Tuple, Set
import networkx as nx
import copy
from .models import Device, Interface, NetworkLink, DeviceRole, OperationalStatus


class DigitalTwinGraph:
    """
    In-memory live graph engine for the network topology.
    Synchronizes state, provides fast path calculation, and supports cloning for sandbox simulation.
    """

    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.links: Dict[str, NetworkLink] = {}
        self.graph: nx.DiGraph = nx.DiGraph()

    def add_device(self, device: Device):
        self.devices[device.id] = device
        self.graph.add_node(
            device.id,
            role=device.role.value,
            hostname=device.hostname,
            status=device.status.value,
        )

    def add_link(self, link: NetworkLink):
        self.links[link.id] = link
        # Directed edges for both directions
        self.graph.add_edge(
            link.source_device,
            link.target_device,
            link_id=link.id,
            capacity_gbps=link.capacity_gbps,
            latency_ms=link.latency_ms,
            status=link.status.value,
        )
        self.graph.add_edge(
            link.target_device,
            link.source_device,
            link_id=f"{link.id}_rev",
            capacity_gbps=link.capacity_gbps,
            latency_ms=link.latency_ms,
            status=link.status.value,
        )

    def set_link_status(self, link_id: str, status: OperationalStatus):
        if link_id in self.links:
            self.links[link_id].status = status
            src = self.links[link_id].source_device
            tgt = self.links[link_id].target_device
            if self.graph.has_edge(src, tgt):
                self.graph[src][tgt]["status"] = status.value
            if self.graph.has_edge(tgt, src):
                self.graph[tgt][src]["status"] = status.value

    def get_ecmp_paths(self, src_device: str, dst_device: str) -> List[List[str]]:
        """Compute all shortest (ECMP) paths between source and destination considering active links."""
        active_subgraph = nx.DiGraph()
        for u, v, data in self.graph.edges(data=True):
            if data.get("status") == OperationalStatus.UP.value:
                active_subgraph.add_edge(u, v, weight=data.get("latency_ms", 1.0))

        try:
            shortest_length = nx.shortest_path_length(active_subgraph, src_device, dst_device)
            all_paths = [
                p for p in nx.all_shortest_paths(active_subgraph, src_device, dst_device)
                if len(p) - 1 == shortest_length
            ]
            return all_paths
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def clone(self) -> "DigitalTwinGraph":
        """Create a deep copy for what-if counterfactual sandbox simulation."""
        new_twin = DigitalTwinGraph()
        new_twin.devices = copy.deepcopy(self.devices)
        new_twin.links = copy.deepcopy(self.links)
        new_twin.graph = self.graph.copy()
        return new_twin

    def reconcile_30s_cycle(self) -> Dict[str, int]:
        """Periodic full 30-second reconciliation summary."""
        up_nodes = sum(1 for d in self.devices.values() if d.status == OperationalStatus.UP)
        up_links = sum(1 for l in self.links.values() if l.status == OperationalStatus.UP)
        return {
            "total_devices": len(self.devices),
            "up_devices": up_nodes,
            "total_links": len(self.links),
            "up_links": up_links,
        }
