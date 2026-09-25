"""Tests for Layer 5: Root-Cause Analysis & Bayesian Inference."""
from rca.causal_graph import CausalGraphEngine
from rca.bayesian import BayesianRCAEngine
from rca.narrative import IncidentNarrativeGenerator


def test_causal_graph_and_bayesian():
    causal = CausalGraphEngine()
    # Spine-01 failure causes symptoms on Leaf-01 port eth1 and Leaf-02 port eth1
    causal.add_dependency("spine-01", "leaf-01:eth1")
    causal.add_dependency("spine-01", "leaf-02:eth1")

    candidates = causal.find_candidate_root_causes(["leaf-01:eth1", "leaf-02:eth1"])
    assert len(candidates) > 0
    assert candidates[0]["component"] == "spine-01"
    assert candidates[0]["explained_symptoms_count"] == 2

    # Bayesian inference
    bayesian = BayesianRCAEngine()
    causes = ["transceiver_laser_fault", "switch_asic_drop", "bgp_config_mismatch"]
    symptoms = ["optical_power_drop"]
    posteriors = bayesian.infer_root_cause(causes, symptoms)
    
    # Transceiver should have highest posterior due to optical_power_drop
    assert posteriors[0]["root_cause"] == "transceiver_laser_fault"
    assert posteriors[0]["probability"] > 0.5


def test_narrative_generator():
    narrative = IncidentNarrativeGenerator.generate_narrative(
        incident_id="INC-9821",
        top_root_cause={"root_cause": "transceiver_laser_fault", "probability": 0.88},
        observed_symptoms=["optical_power_drop", "packet_loss_spike"],
        remediation_action={"remediation_command": "interface eth1 shutdown"},
        recovery_time_sec=11.8,
    )
    assert "INC-9821" in narrative
    assert "transceiver_laser_fault" in narrative
    assert "11.80 seconds" in narrative
