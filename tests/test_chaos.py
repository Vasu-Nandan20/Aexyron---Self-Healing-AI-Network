"""
Tests for Chaos Injection and 100-Failure Chaos Suite (§2.4 Objectives).
"""
import pytest
from simulations.chaos_injector import ChaosFaultInjector, FailureType


def test_single_fault_injection():
    injector = ChaosFaultInjector()
    fault = injector.inject_fault(
        failure_type=FailureType.PHYSICAL_LINK_CUT,
        target_component="spine-01:eth1",
        duration_seconds=15,
        severity=1.0,
    )
    assert fault["type"] == "physical_link_cut"
    assert fault["target"] == "spine-01:eth1"
    assert fault["status"] == "ACTIVE"
    assert len(injector.active_injections) == 1

    injector.clear_all()
    assert len(injector.active_injections) == 0


def test_100_failure_chaos_suite_execution():
    """
    Validates §2.4 objective:
    'Validate the system through a 100-failure chaos test in a Containerlab environment.'
    """
    injector = ChaosFaultInjector()
    report = injector.run_100_failure_chaos_suite(trials_per_type=20)

    assert report["status"] == "COMPLETED"
    assert report["total_injections"] == 100
    assert len(report["failure_types_tested"]) == 5
    assert len(report["injections"]) == 100

    # Ensure all 5 failure modes were tested evenly (20 each)
    counts = {}
    for inj in report["injections"]:
        counts[inj["type"]] = counts.get(inj["type"], 0) + 1

    for f_type in FailureType:
        assert counts[f_type.value] == 20
