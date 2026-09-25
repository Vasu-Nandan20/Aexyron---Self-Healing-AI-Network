"""Tests for Layer 4: What-If Counterfactual Engine."""
from digital_twin.models import Device, NetworkLink, DeviceRole
from digital_twin.graph_sync import DigitalTwinGraph
from what_if.counterfactual import CounterfactualEngine
from what_if.plan_cache import PlanCache


def test_what_if_counterfactual_and_plan_cache():
    twin = DigitalTwinGraph()
    dev_s1 = Device(id="spine-01", hostname="s1", role=DeviceRole.SPINE, management_ip="1.1.1.1")
    dev_s2 = Device(id="spine-02", hostname="s2", role=DeviceRole.SPINE, management_ip="1.1.1.2")
    dev_l1 = Device(id="leaf-01", hostname="l1", role=DeviceRole.LEAF, management_ip="1.1.1.11")
    dev_l2 = Device(id="leaf-02", hostname="l2", role=DeviceRole.LEAF, management_ip="1.1.1.12")

    twin.add_device(dev_s1)
    twin.add_device(dev_s2)
    twin.add_device(dev_l1)
    twin.add_device(dev_l2)

    link1 = NetworkLink("L1", "leaf-01", "eth1", "spine-01", "eth1", capacity_gbps=100)
    link2 = NetworkLink("L2", "leaf-01", "eth2", "spine-02", "eth1", capacity_gbps=100)
    link3 = NetworkLink("L3", "spine-01", "eth2", "leaf-02", "eth1", capacity_gbps=100)
    link4 = NetworkLink("L4", "spine-02", "eth2", "leaf-02", "eth2", capacity_gbps=100)

    twin.add_link(link1)
    twin.add_link(link2)
    twin.add_link(link3)
    twin.add_link(link4)

    engine = CounterfactualEngine(twin)
    plan = engine.evaluate_hypothetical_link_cut("L1")
    assert plan is not None
    assert plan["status"] == "PRECOMPUTED"
    assert "remediation_command" in plan

    # Test Plan Cache storage and retrieval
    cache = PlanCache()
    cache.store_plan("fault_L1", plan)
    cached_plan = cache.get_plan("fault_L1")
    assert cached_plan is not None
    assert cached_plan["failed_link_id"] == "L1"
