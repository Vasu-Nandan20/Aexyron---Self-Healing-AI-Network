"""Tests for Layer 6: Decision Engine, OPA Guardrails & Circuit Breaker."""
from digital_twin.models import Device, NetworkLink, DeviceRole
from digital_twin.graph_sync import DigitalTwinGraph
from decision_engine.opa_client import OPAClient
from decision_engine.controller import AutonomyController, AutonomyLevel
from decision_engine.execution_guard import ExecutionGuard


def test_opa_and_safety_guardrails():
    client = OPAClient()

    # Safe action (drained ratio <= 25%, min paths >= 2, rate limit ok)
    safe_action = {"drained_capacity_ratio": 0.20, "affected_gpu_nodes": 0, "min_remaining_ecmp_paths": 2}
    res = client.evaluate_policy(safe_action, recent_actions_count=1)
    assert res["allowed"] is True

    # Unsafe action (drained ratio 40% > 25%)
    unsafe_action = {"drained_capacity_ratio": 0.40, "affected_gpu_nodes": 0, "min_remaining_ecmp_paths": 2}
    res_unsafe = client.evaluate_policy(unsafe_action, recent_actions_count=1)
    assert res_unsafe["allowed"] is False


def test_canary_and_circuit_breaker():
    twin = DigitalTwinGraph()
    dev = Device(id="s1", hostname="s1", role=DeviceRole.SPINE, management_ip="1.1.1.1")
    twin.add_device(dev)

    guard = ExecutionGuard(twin)
    plan = {
        "remediation_command": "ip link set eth1 down",
        "risk_assessment": {
            "drained_capacity_ratio": 0.10,
            "affected_gpu_nodes": 0,
            "min_remaining_ecmp_paths": 2,
            "composite_risk_score": 0.15,
        },
    }

    # Simulate healthy execution
    exec_res = guard.validate_and_execute(plan, simulate_telemetry_healthy=True)
    assert exec_res["success"] is True

    # Simulate 2 consecutive canary failures to trigger circuit breaker
    fail_res1 = guard.validate_and_execute(plan, simulate_telemetry_healthy=False)
    assert fail_res1["success"] is False
    assert fail_res1["stage"] == "CANARY_ROLLBACK"

    fail_res2 = guard.validate_and_execute(plan, simulate_telemetry_healthy=False)
    assert fail_res2["circuit_breaker_tripped"] is True

    # Subsequent call should be blocked by circuit breaker
    blocked_res = guard.validate_and_execute(plan, simulate_telemetry_healthy=True)
    assert blocked_res["stage"] == "CIRCUIT_BREAKER"
