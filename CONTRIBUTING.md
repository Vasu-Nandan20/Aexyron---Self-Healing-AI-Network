# Contributing to Aexyron

Thank you for your interest in contributing to **Aexyron**! As an autonomous systems research and engineering project targeting both enterprise datacenter networks and academic publications (NSDI, SIGCOMM, CoNEXT), we welcome contributions across software engineering, machine learning, and network systems.

---

## 🛠️ Development Workflow

1. **Fork & Branch**: Fork the repo and create a feature branch (`git checkout -b feature/what-if-enhancement`).
2. **Setup Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
3. **Local Infrastructure**:
   Launch dependencies using Docker Compose:
   ```bash
   docker-compose up -d
   ```
4. **Testing**:
   Ensure all unit and integration tests pass:
   ```bash
   pytest tests/ -v
   ```

---

## 📋 Architectural Layers

When submitting code, identify which of the 7 architectural layers your changes affect:
1. `telemetry/` — Streaming Telemetry (gNMI, eBPF, sFlow, Kafka)
2. `digital_twin/` — Live Graph Model (Neo4j, state synchronizer)
3. `ai_engine/` — Anomaly Detection & Time-Series Prediction
4. `what_if/` — Counterfactual Simulation & Redis Plan Cache
5. `rca/` — Causal Graph Traversal & Bayesian Inference
6. `decision_engine/` — OPA Guardrails, Autonomy Levels & Circuit Breakers
7. `black_box/` — Cryptographic Hash-Chained Audit Ledger & Replay

---

## 🧪 Submission Guidelines

- Include unit tests for all new models, policies, or graph algorithms.
- If introducing an OPA policy change, update `docs/SAFETY_AND_GUARDRAILS.md`.
- Document any benchmark performance changes in PR descriptions.
