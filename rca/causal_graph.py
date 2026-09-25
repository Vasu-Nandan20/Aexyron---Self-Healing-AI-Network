"""
Aexyron - Layer 5: Causal Graph Traversal for Root-Cause Analysis.
"""

from typing import Dict, List, Set, Any
import networkx as nx


class CausalGraphEngine:
    """
    Constructs a causal dependency Directed Acyclic Graph (DAG)
    and propagates symptomatic alerts to isolate primary failure origins.
    """

    def __init__(self):
        self.causal_dag = nx.DiGraph()

    def add_dependency(self, parent_component: str, dependent_component: str, weight: float = 1.0):
        """parent failure can cause symptoms on dependent_component."""
        self.causal_dag.add_edge(parent_component, dependent_component, weight=weight)

    def find_candidate_root_causes(self, active_symptoms: List[str]) -> List[Dict[str, Any]]:
        """
        Given a list of symptomatic alerts, find the ancestral nodes that explain the highest number of symptoms.
        """
        candidate_scores: Dict[str, int] = {}
        for symptom in active_symptoms:
            if symptom not in self.causal_dag:
                candidate_scores[symptom] = candidate_scores.get(symptom, 0) + 1
                continue

            # Ancestors of symptom in the causal graph
            ancestors = nx.ancestors(self.causal_dag, symptom)
            if not ancestors:
                candidate_scores[symptom] = candidate_scores.get(symptom, 0) + 1
            else:
                for anc in ancestors:
                    candidate_scores[anc] = candidate_scores.get(anc, 0) + 1

        # Rank candidates by symptom coverage
        ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [{"component": comp, "explained_symptoms_count": count} for comp, count in ranked]
