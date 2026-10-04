"""Tests for Layer 2: Live Digital Twin."""
from digital_twin.models import Device, NetworkLink, DeviceRole, OperationalStatus
from digital_twin.graph_sync import DigitalTwinGraph


def test_digital_twin_topology_and_ecmp():
    twin = DigitalTwinGraph()

    # Create 2 Spines and 2 Leafs
    spine1 = Device(id="spine-01", hostname="spine1.lab", role=DeviceRole.SPINE, management_ip="192.168.1.1")
    spine2 = Device(id="spine-02", hostname="spine2.lab", role=DeviceRole.SPINE, management_ip="192.168.1.2")
    leaf1 = Device(id="leaf-01", hostname="leaf1.lab", role=DeviceRole.LEAF, management_ip="192.168.1.11")
    leaf2 = Device(id="leaf-02", hostname="leaf2.lab", role=DeviceRole.LEAF, management_ip="192.168.1.12")

    twin.add_device(spine1)
    twin.add_device(spine2)
    twin.add_device(leaf1)
    twin.add_device(leaf2)

    # Add interconnect links: Leaf1 -> Spine1, Leaf1 -> Spine2, Leaf2 -> Spine1, Leaf2 -> Spine2
    link1 = NetworkLink("L1", "leaf-01", "eth1", "spine-01", "eth1", capacity_gbps=100)
    link2 = NetworkLink("L2", "leaf-01", "eth2", "spine-02", "eth1", capacity_gbps=100)
    link3 = NetworkLink("L3", "spine-01", "eth2", "leaf-02", "eth1", capacity_gbps=100)
    link4 = NetworkLink("L4", "spine-02", "eth2", "leaf-02", "eth2", capacity_gbps=100)

    twin.add_link(link1)
    twin.add_link(link2)
    twin.add_link(link3)
    twin.add_link(link4)

    # ECMP Paths between leaf-01 and leaf-02: should have 2 distinct paths
    paths = twin.get_ecmp_paths("leaf-01", "leaf-02")
    assert len(paths) == 2
    assert ["leaf-01", "spine-01", "leaf-02"] in paths
    assert ["leaf-01", "spine-02", "leaf-02"] in paths

    # Cut link1: ECMP should reduce to 1 path
    twin.set_link_status("L1", OperationalStatus.DOWN)
    remaining = twin.get_ecmp_paths("leaf-01", "leaf-02")
    assert len(remaining) == 1
    assert remaining[0] == ["leaf-01", "spine-02", "leaf-02"]


def test_twin_clone_isolation():
    twin = DigitalTwinGraph()
    dev = Device(id="spine-01", hostname="spine1.lab", role=DeviceRole.SPINE, management_ip="192.168.1.1")
    twin.add_device(dev)

    cloned = twin.clone()
    assert "spine-01" in cloned.devices

    # Mutate clone, ensure original is unaffected
    cloned.devices["spine-01"].status = OperationalStatus.DOWN
    assert twin.devices["spine-01"].status == OperationalStatus.UP


def test_routing_fidelity_target():
    """Verify that digital twin achieves >= 85% routing fidelity against switch FIB state."""
    twin = DigitalTwinGraph()

    for dev in [
        Device(id="spine-01", hostname="s1", role=DeviceRole.SPINE, management_ip="10.0.0.1"),
        Device(id="spine-02", hostname="s2", role=DeviceRole.SPINE, management_ip="10.0.0.2"),
        Device(id="leaf-01", hostname="l1", role=DeviceRole.LEAF, management_ip="10.0.0.11"),
        Device(id="leaf-02", hostname="l2", role=DeviceRole.LEAF, management_ip="10.0.0.12"),
    ]:
        twin.add_device(dev)

    for link in [
        NetworkLink("L1", "leaf-01", "eth1", "spine-01", "eth1", capacity_gbps=100),
        NetworkLink("L2", "leaf-01", "eth2", "spine-02", "eth1", capacity_gbps=100),
        NetworkLink("L3", "spine-01", "eth2", "leaf-02", "eth1", capacity_gbps=100),
        NetworkLink("L4", "spine-02", "eth2", "leaf-02", "eth2", capacity_gbps=100),
    ]:
        twin.add_link(link)

    # Simulated ground truth routing table from physical/Containerlab switches
    ground_truth = {
        ("leaf-01", "leaf-02"): [
            ["leaf-01", "spine-01", "leaf-02"],
            ["leaf-01", "spine-02", "leaf-02"],
        ],
        ("leaf-02", "leaf-01"): [
            ["leaf-02", "spine-01", "leaf-01"],
            ["leaf-02", "spine-02", "leaf-01"],
        ],
        ("leaf-01", "spine-01"): [["leaf-01", "spine-01"]],
        ("leaf-01", "spine-02"): [["leaf-01", "spine-02"]],
    }

    result = twin.verify_routing_fidelity(ground_truth)
    assert result["passed"] is True
    assert result["fidelity"] >= 0.85
    assert result["fidelity_percentage"] == 100.0
