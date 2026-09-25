"""
Aexyron - Layer 5: Bayesian Inference Engine for Root-Cause Identification.
"""

from typing import Dict, List, Any


class BayesianRCAEngine:
    """
    Computes posterior probabilities P(Fault_i | Observed_Symptoms)
    using prior fault distributions and symptom conditional likelihoods.
    """

    def __init__(self):
        # Default priors for failure modes
        self.priors: Dict[str, float] = {
            "transceiver_laser_fault": 0.40,
            "cable_physical_cut": 0.25,
            "switch_asic_drop": 0.20,
            "bgp_config_mismatch": 0.15,
        }

    def infer_root_cause(
        self,
        candidate_causes: List[str],
        observed_symptoms: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Evaluate candidate causes and return normalized posterior probabilities.
        """
        posteriors = {}
        for cause in candidate_causes:
            prior = self.priors.get(cause, 0.10)
            likelihood = 1.0

            # Conditional likelihood adjustments based on observed symptoms
            if "optical_power_drop" in observed_symptoms and cause == "transceiver_laser_fault":
                likelihood *= 4.0
            if "socket_retransmissions" in observed_symptoms and cause == "switch_asic_drop":
                likelihood *= 2.5
            if "bgp_notification" in observed_symptoms and cause == "bgp_config_mismatch":
                likelihood *= 3.5

            posteriors[cause] = prior * likelihood

        total = sum(posteriors.values()) if posteriors else 1.0
        normalized = [
            {"root_cause": cause, "probability": round(score / total, 4)}
            for cause, score in sorted(posteriors.items(), key=lambda x: x[1], reverse=True)
        ]
        return normalized
