# Aexyron — Self-Healing AI Network

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![Kafka](https://img.shields.io/badge/Streaming-Apache%20Kafka-231F20.svg?logo=apachekafka)](https://kafka.apache.org)
[![Neo4j](https://img.shields.io/badge/Digital%20Twin-Neo4j%20Graph-008CC1.svg?logo=neo4j)](https://neo4j.com)
[![Redis](https://img.shields.io/badge/Plan%20Cache-Redis-DC382D.svg?logo=redis)](https://redis.io)
[![OPA](https://img.shields.io/badge/Guardrails-Open%20Policy%20Agent-4078c0.svg)](https://www.openpolicyagent.org/)
[![Target Publication](https://img.shields.io/badge/Target-NSDI%20%7C%20SIGCOMM%20%7C%20CoNEXT-purple.svg)](docs/RESEARCH_NOVELTY.md)

**An Autonomous, Digital-Twin-Driven Network Operations System with Counterfactual Resilience Analysis and a Replayable Black Box Recorder.**

[Key Results](#-key-results--performance-targets) •
[Gap Analysis](#-autonomy-gap-analysis) •
[Technical Design](docs/TECHNICAL_DESIGN.md) •
[Architecture](#-seven-layer-system-architecture) •
[Autonomy Levels](#-autonomy-levels-l0--l4) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation)

</div>

---

## 📌 Executive Summary

Network outages cost enterprises an estimated **$300,000 per hour on average**, with critical datacenter and AI/GPU cluster infrastructure failures reaching into the millions. Despite decades of investment in monitoring tools, the gap between detecting a problem and resolving it remains stubbornly wide.

Today's network operations centers (NOCs) rely on human operators who must sift through thousands of alerts, mentally correlate events across dozens of dashboards, and manually execute recovery procedures—often under extreme time pressure.

**Aexyron** closes this gap by building an autonomous, AI-driven network operations system that continuously monitors, reasons about, and repairs a live network—**without waiting for a human to act**. 

---

## ⚡ Key Results & Performance Targets

In controlled Containerlab experiments on Clos leaf-spine fabrics, Aexyron is engineered to achieve:

| Metric | Industry Baseline (Manual NOC) | Aexyron Target | Improvement |
| :--- | :--- | :--- | :--- |
| **Mean Time to Recovery (MTTR)** | ~240 seconds (4 min) | **< 15 seconds** | **16× Faster** |
| **Anomaly Detection Latency** | ~30–90 seconds | **< 5 seconds** | **Up to 18× Faster** |
| **Failure Prediction Horizon** | None (purely reactive) | **20+ seconds ahead** | **Proactive Mitigation** |
| **False-Positive Rate (FPR)** | ~18% (alert fatigue) | **< 5%** | **> 3.5× Reduction** |
| **Recovery Success Rate** | 82% (manual configuration errors)| **> 90%** | **High-Yield Automation** |
| **Unintended Side-Effect Rate** | ~12% | **< 2%** | **Formally Gated by OPA** |

---

## 🔍 Autonomy Gap Analysis

| Capability | State of the Art | This Project (Aexyron) |
| :--- | :--- | :--- |
| **Prediction** | None / basic trending | **TFT / XGBoost ($\ge$ 20s horizon)** |
| **Root Cause** | Manual correlation across dashboards | **Causal graph + Bayesian inference** |
| **Simulation** | Offline batch verification (Batfish) | **Live digital twin, 30s what-if cycle** |
| **Recovery** | Manual runbooks / fragile scripts | **Auto-execute with OPA guardrails (L0–L4)** |
| **Audit** | Scattered logs and CLI histories | **Immutable Black Box + deterministic replay** |

*Table 1: Autonomy gap analysis — state of the art vs. this project.*

### Feature Comparison Matrix

| System / Approach | Live Twin | Prediction | Auto-Heal | What-If | Black Box |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AIOps Platforms** (Moogsoft, BigPanda) | ❌ None | Partial | ❌ None | ❌ None | ❌ None |
| **Batfish** (NSDI '15) | Offline | ❌ None | ❌ None | Offline | ❌ None |
| **Forward Networks** | Snapshot | ❌ None | ❌ None | Snapshot | ❌ None |
| **VeriFlow** (NSDI '13) | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| **Chaos Engineering** (Chaos Monkey) | ❌ None | ❌ None | ❌ None | Testing | ❌ None |
| **Aexyron (This Project)** | **✅ 30s Cycle** | **✅ $\ge$20s Horizon** | **✅ L0–L4 Autonomous** | **✅ Continuous Live** | **✅ Replayable Audit** |

*Table 2: Feature comparison with related work.*

> **Key Takeaway**: No existing system combines all five capabilities: a live, continuously-synchronized digital twin ($\ge 85\%$ fidelity); ML-driven failure prediction ($\ge 20\text{s}$ ahead); autonomous multi-level healing with guardrails (L0–L4); continuous what-if counterfactual reasoning ($< 2\text{ms}$ lookup); and an immutable, replayable event log. Aexyron is engineered specifically to fill this operational gap.

---

## 🎯 Objectives & Scope Boundary

As detailed in the [Technical Design Document](docs/TECHNICAL_DESIGN.md):
- **Autonomous Closed-Loop Control**: 7-layer architecture closing the gap from detection through automated recovery.
- **High-Fidelity Digital Twin**: Live graph mirroring topology with $\ge 85\%$ routing fidelity and serving as preflight simulation sandbox.
- **Sub-5s Anomaly & $\ge$20s Failure Forecasting**: Fast-path Isolation Forests and deep temporal forecasting.
- **Continuous Counterfactual Engine**: Continuous what-if exploration with $< 2\text{s}$ scenario simulation and $< 2\text{ms}$ plan cache lookup.
- **Causal Root Cause Analysis**: Disambiguating symptom cascades via Bayesian inference and generating LLM incident narratives.
- **Formal Policy & Guardrail Enforcement**: Five autonomy levels (L0–L4) gated by Open Policy Agent, canary deployments, and circuit breakers.
- **Cryptographic Flight Recorder**: Append-only, SHA-256 hash-chained immutable ledger with deterministic second-by-second replay.
- **Empirical Validation**: 500-trial benchmark suite and 100-failure chaos test suite in a Containerlab environment.

**Scope Boundary**: The prototype targets a leaf-spine CLOS topology (2 spines, 4 leaves, 6–8 servers) running BGP/OSPF on FRRouting within Containerlab. Production-grade HA, multi-vendor support, and WAN-scale testing are designated as future work.

---

## 🏗️ Seven-Layer System Architecture

Aexyron organizes autonomous network operations into seven coordinated layers:

```mermaid
flowchart TD
    subgraph L1 ["1. Streaming Telemetry Bus"]
        gNMI[gNMI Telemetry]
        eBPF[eBPF Kernel Probes]
        sFlow[sFlow / IPFIX]
        OTel[OpenTelemetry]
        Kafka[(Apache Kafka Event Bus)]
        gNMI & eBPF & sFlow & OTel --> Kafka
    end

    subgraph L2 ["2. Live Digital Twin"]
        Sync[Graph Synchronizer (30s Cycle)]
        Neo4j[(Neo4j Graph Database\nTopology • Metrics • Routing)]
        Kafka --> Sync --> Neo4j
    end

    subgraph L3 ["3. AI Anomaly & Prediction Engine"]
        IF[Isolation Forest\nAnomaly Detection (<5s)]
        TFT[XGBoost & TFT\nFailure Prediction (20s+ Ahead)]
        Kafka --> IF
        Kafka --> TFT
    end

    subgraph L4 ["4. What-If Counterfactual Engine"]
        Counterfactual[Hypothetical Failure Injection]
        RiskScore[Blast-Radius & Risk Scorer]
        RedisCache[(Redis Pre-Computed\nPlan Cache)]
        Neo4j --> Counterfactual --> RiskScore --> RedisCache
    end

    subgraph L5 ["5. Root-Cause Analysis (RCA)"]
        Causal[Causal Graph Traversal]
        Bayesian[Bayesian Inference Engine]
        LLM[LLM Incident Narrative Generator]
        Neo4j & IF & TFT --> Causal --> Bayesian --> LLM
    end

    subgraph L6 ["6. Decision Engine & Guardrails"]
        OPA[Open Policy Agent (OPA)\nAutonomy Gate L0-L4]
        Sim[Preflight Digital Twin Sim]
        Canary[Canary Deployment & Rollback]
        Breaker[Rate Limiter & Circuit Breaker]
        RedisCache -. Fast Hit .-> OPA
        Bayesian -. Candidate Plan .-> OPA
        OPA --> Sim --> Canary --> Breaker
    end

    subgraph L7 ["7. Network Black Box"]
        Ledger[SHA-256 Hash-Chained Append-Only Log]
        Replay[Deterministic Forensics Replay Tool]
        Kafka & OPA & Breaker -. Event Stream .-> Ledger --> Replay
    end

    Breaker ==>|Auto-Remediation| DataPlane[Data Plane Switches & NICs]
```

### 1. Streaming Telemetry
- Multi-modal ingestion across **gNMI** (interface counters, optical power), **eBPF** (host socket drops, TCP RTT distribution), **sFlow** (flow matrices), and **OpenTelemetry**.
- Real-time ingestion via **Apache Kafka** partitioned by device and interface at > 100k events/sec.

### 2. Live Digital Twin
- **Neo4j**-backed property graph mirroring network topology, device states, BGP peerings, and dynamic interface statistics.
- Continuous 30-second full reconciliation with sub-second event-driven delta updates.

### 3. AI Anomaly & Prediction Engine
- **Fast Anomaly Detection (< 5s)**: Unsupervised Isolation Forests evaluate rolling window statistics to catch microburst drops and grey degradation.
- **Predictive Failure Forecasting (20s+ ahead)**: XGBoost and Temporal Fusion Transformers forecast optical transceiver blowouts and buffer exhaustion during GPU incast traffic.

### 4. What-If Counterfactual Engine
- Continuously explores hypothetical failure branches on the digital twin *before* problems occur.
- Computes optimal reroutes, evaluates blast radius, and caches pre-computed recovery recipes in **Redis** for instant (< 2ms) execution.

### 5. Root-Cause Analysis (RCA)
- Causal graph traversal disambiguates symptom cascades from primary root causes.
- Bayesian inference calculates posterior probabilities $P(\text{Root Cause} \mid \text{Symptoms})$.
- LLM incident narrative generator synthesizes human-readable post-mortems for network engineers.

### 6. Decision Engine & Guardrails
- **Open Policy Agent (OPA)** policies enforce strict invariants (e.g., maximum drained capacity $\le 25\%$, preservation of redundant GPU paths).
- **Four-stage safety pipeline**: Preflight twin simulation $\to$ Canary traffic shift (5%) $\to$ Automated 10-second verification $\to$ Sub-1.5s automatic rollback if degradation occurs.
- Circuit breakers prevent cascading remediation storms.

### 7. Network Black Box
- Append-only, **SHA-256 hash-chained** event ledger mathematically guarantees audit immutability.
- CLI and Web forensics replay tool enables step-by-step incident scrubbing for compliance and post-mortem analysis.

---

## 🛡️ Autonomy Levels (L0 – L4)

| Level | Designation | Execution Mode | Operator Involvement | Safe Failure Mode |
| :---: | :--- | :--- | :--- | :--- |
| **L0** | Alert Only | Passive Monitoring | Manual resolution | System displays causal diagnosis |
| **L1** | Operator Assisted | Recommended Plan | 1-Click approval required | Plan expires after 60s if unapproved |
| **L2** | Bounded Autonomous | Low-Risk Auto-Fix | Post-action notification | Hard-bounded to non-disruptive actions |
| **L3** | Conditional Autonomous | High-Impact Auto-Fix | Alerted with 15s pause override | Strict blast-radius limit (< 15% fabric) |
| **L4** | Fully Autonomous | Zero-Touch Closed-Loop | Zero-touch; audited in Black Box | Canary validation + instant rollback |

---

## 🗓️ 13-Week Implementation Roadmap

| Phase | Weeks | Focus Area | Key Deliverables |
| :---: | :---: | :--- | :--- |
| **Phase 1** | **W1–W3** | Testbed & Telemetry Pipeline | Containerlab 3-tier fabric, gNMI/eBPF collectors, high-throughput Kafka bus |
| **Phase 2** | **W4–W5** | Live Digital Twin | Neo4j topology schema, 30s full synchronizer, sub-second delta updates |
| **Phase 3** | **W6–W7** | AI Anomaly & Prediction Engine | Isolation Forest (< 5s detection), XGBoost/TFT (20s+ predictive horizon) |
| **Phase 4** | **W8–W9** | What-If Counterfactual Engine | Counterfactual branch simulator, blast-radius scorer, Redis plan cache |
| **Phase 5** | **W10–W11**| RCA & Decision Guardrails | Bayesian causal graph, OPA Rego policies, L0–L4 controller, canary runner |
| **Phase 6** | **W12** | Network Black Box & Replay | SHA-256 hash-chained ledger, forensic replay CLI & visualization tool |
| **Phase 7** | **W13** | Benchmarks & Academic Paper | 100-trial Containerlab evaluation, MTTR validation, NSDI/SIGCOMM paper draft |

---

## 📂 Repository Structure

```
Aexyron/
├── .github/
│   ├── workflows/             # CI/CD workflows (linting, tests, docker validation)
│   ├── ISSUE_TEMPLATE/        # Standardized issue templates
│   └── pull_request_template.md
├── docs/                      # Comprehensive Documentation
│   ├── ARCHITECTURE.md        # 7-layer architecture deep dive
│   ├── ROADMAP.md             # Detailed 13-week milestone plan
│   ├── SAFETY_AND_GUARDRAILS.md # OPA policies, autonomy levels, canary & rollback
│   ├── EVALUATION_AND_BENCHMARKS.md # Containerlab testbed & failure profiles
│   └── RESEARCH_NOVELTY.md    # Academic contributions & publication targets
├── telemetry/                 # Layer 1: Streaming Telemetry & Kafka
│   ├── collectors/            # gNMI, eBPF, sFlow client wrappers
│   └── kafka_topics.py        # Topic schemas and serializers
├── digital_twin/              # Layer 2: Live Digital Twin
│   ├── models.py              # Network graph data structures
│   ├── graph_sync.py          # Neo4j synchronizer (30s periodic + deltas)
│   └── cypher/                # Neo4j Cypher queries & constraints
├── ai_engine/                 # Layer 3: AI Anomaly & Prediction Engine
│   ├── anomaly_detector.py    # Isolation Forest fast detector (< 5s)
│   ├── failure_predictor.py   # XGBoost & Temporal Fusion Transformer
│   └── features.py            # Streaming feature extraction
├── what_if/                   # Layer 4: Counterfactual Reasoning Engine
│   ├── counterfactual.py      # Hypothetical failure injector
│   ├── risk_scorer.py         # Blast-radius and capacity impact scoring
│   └── plan_cache.py          # Redis recovery plan cache manager
├── rca/                       # Layer 5: Root-Cause Analysis
│   ├── causal_graph.py        # Dependency graph traversal
│   ├── bayesian.py            # Probabilistic fault attribution
│   └── narrative.py           # LLM incident explanation generator
├── decision_engine/           # Layer 6: Decision Engine & Guardrails
│   ├── controller.py          # Autonomy Level (L0-L4) coordinator
│   ├── opa_client.py          # OPA evaluation client
│   ├── execution_guard.py     # Preflight simulation, canary, rollback & circuit breaker
│   └── policies/              # Rego guardrail definitions
├── black_box/                 # Layer 7: Network Black Box
│   ├── hash_chain.py          # Append-only SHA-256 cryptographic ledger
│   └── replay.py              # Forensic incident replay engine
├── simulations/               # Containerlab Testbed & Chaos Harness
│   ├── topologies/            # Containerlab YAML topology definitions
│   └── chaos_injector.py      # Link failure, packet drop & BGP flap harness
├── docker-compose.yml         # Local stack (Kafka, Neo4j, Redis, OPA)
├── pyproject.toml             # Python build & dependency metadata
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Vasu-Nandan20/Aexyron---Self-Healing-AI-Network.git
cd Aexyron---Self-Healing-AI-Network
```

### 2. Environment Setup
```bash
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 3. Spin Up Infrastructure Stack
Launch Kafka, Neo4j, Redis, and OPA in Docker:
```bash
docker-compose up -d
```

### 4. Run Verification Tests
```bash
pytest tests/ -v
```

---

## 🔬 Research & Publications

This project targets submission to top-tier computer networking venues:
- **USENIX NSDI** (Networked Systems Design and Implementation)
- **ACM SIGCOMM** (Special Interest Group on Data Communication)
- **ACM CoNEXT** (Conference on emerging Networking EXperiments and Technologies)

### Citation Stub
```bibtex
@misc{nandan2026aexyron,
  title={Aexyron: An Autonomous, Digital-Twin-Driven Network Operations System with Counterfactual Resilience Analysis and a Replayable Black Box Recorder},
  author={Nandan, Vasu},
  year={2026},
  publisher={GitHub},
  howpublished={\url{https://github.com/Vasu-Nandan20/Aexyron---Self-Healing-AI-Network}}
}
```

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
