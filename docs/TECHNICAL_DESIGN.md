# Aexyron: Self-Healing AI Network — Technical Design Document

---

## 1. Executive Summary

Network outages cost enterprises an estimated **$300,000 per hour on average**, with critical infrastructure failures reaching into the millions. Despite decades of investment in monitoring tools, the gap between detecting a problem and resolving it remains stubbornly wide.

Today's network operations centers (NOCs) rely on human operators who must sift through thousands of alerts, mentally correlate events across dozens of dashboards, and manually execute recovery procedures—often under extreme time pressure.

The **Self-Healing AI Network (Aexyron)** closes this gap by building an autonomous, AI-driven network operations system that continuously monitors, reasons about, and repairs a live network—**without waiting for a human to act**.

The system integrates seven architectural layers:
- **Layer 1: Streaming Telemetry** — gNMI, OpenTelemetry, sFlow, and eBPF feed real-time data into a high-throughput Kafka bus.
- **Layer 2: Live Digital Twin** — A Neo4j-backed property graph mirrors network topology and state with continuous 30-second reconciliation and sub-second delta updates.
- **Layer 3: AI Anomaly & Prediction Engine** — Unsupervised Isolation Forests detect anomalies in $< 5\text{s}$, while XGBoost and Temporal Fusion Transformers forecast failures $\ge 20\text{s}$ ahead.
- **Layer 4: What-If Counterfactual Engine** — Continuous branch exploration simulates hypothetical failure scenarios ($< 2\text{s}$ simulation time) and caches verified recovery plans in Redis for $< 2\text{ms}$ retrieval.
- **Layer 5: Root-Cause Analysis (RCA)** — Causal graph traversal and Bayesian inference isolate true root causes from symptom cascades, generating structured incident narratives.
- **Layer 6: Decision Engine & Guardrails** — Open Policy Agent (OPA) formally validates safety invariants across five autonomy levels (L0–L4), backed by preflight simulation, canary rollouts, and circuit breakers.
- **Layer 7: Network Black Box** — An append-only, SHA-256 hash-chained flight recorder enables deterministic second-by-second incident replay and cryptographic auditability.

---

## 2. Motivation, Problem Statement & Autonomy Gap Analysis

### 2.1 Cost of Network Outages

The Uptime Institute's 2023 Annual Outage Analysis reports that over **60% of outages cost more than $100,000**, with **15% exceeding $1 million**. For hyperscale AI training clusters—where a single GPU node rents at $2–$3/hour and jobs span thousands of GPUs—even a 10-minute network partition can waste tens of thousands of dollars in lost compute, idle GPUs, and checkpoint-restart overhead. The financial pressure to minimize **Mean Time to Recovery (MTTR)** is immense.

Beyond direct costs, outages erode customer trust, trigger SLA penalties, and—in regulated industries—can result in compliance violations. The total economic impact of network downtime in the U.S. alone is estimated at **$70+ billion annually**.

### 2.2 Why Traditional Monitoring Fails

Traditional network monitoring operates on a **detect-alert-escalate** model: SNMP polling or syslog collection triggers threshold-based alerts, which are routed to a human operator. This model has three fundamental weaknesses:

1. **Alert Fatigue**: Large networks generate thousands of alerts per day. Studies show that up to 95% of security and operational alerts are false positives (Ponemon Institute, 2019). Operators learn to ignore alerts or miss critical warnings amidst the noise.
2. **Reactive, Not Proactive**: Threshold-based detection fires only *after* a metric crosses a static boundary. By then, the failure has already impacted users and applications. There is no prediction, no early warning, and no pre-positioning of recovery plans.
3. **No Causal Reasoning**: A single root cause (e.g., a failing optical transceiver) may generate dozens of correlated alerts across multiple layers (interface CRC errors, link down, BGP neighbor teardown, ECMP rebalance, application socket timeout). Traditional tools cannot distinguish root cause from downstream symptom.

### 2.3 Autonomy Gap Analysis

| Capability | State of the Art | This Project (Aexyron) |
| :--- | :--- | :--- |
| **Prediction** | None / basic linear trending | **TFT / XGBoost ($\ge$ 20s horizon)** |
| **Root Cause** | Manual correlation across dashboards | **Causal graph + Bayesian inference** |
| **Simulation** | Offline batch verification (e.g., Batfish) | **Live twin, continuous 30s what-if cycle** |
| **Recovery** | Manual runbooks / fragile bash scripts | **Auto-execute with OPA guardrails (L0–L4)** |
| **Audit** | Scattered syslogs and CLI histories | **Immutable hash-chained Black Box + replay** |

*Table 1: Autonomy gap analysis — state of the art vs. this project.*

### 2.4 Objectives and Scope

This project aims to:
1. **Design and implement a 7-layer self-healing network architecture** that closes the autonomy gap from real-time detection through automated recovery.
2. **Build a live digital twin** that mirrors network state with $\ge 85\%$ routing fidelity and serves as a safety layer for preflight simulation.
3. **Develop an AI anomaly and prediction engine** achieving $< 5\text{s}$ detection latency and $\ge 20\text{s}$ prediction horizon.
4. **Implement a what-if engine** performing continuous counterfactual reasoning with $< 2\text{s}$ simulation time per scenario and $< 2\text{ms}$ plan cache lookup.
5. **Create a root-cause analysis module** using causal graphs and Bayesian inference to eliminate alert storms and generate LLM post-mortems.
6. **Build a decision engine** with OPA-enforced policies across five autonomy levels (L0–L4) and comprehensive guardrails (canary deployment, rollback, circuit breaker).
7. **Implement a Network Black Box**—an append-only, SHA-256 hash-chained, deterministic replayable event log.
8. **Validate the system through a 100-failure chaos test and 500-trial benchmark loop** in a Containerlab environment.

**Scope Boundary**: The prototype targets a leaf-spine CLOS topology (2 spines, 4 leaves, 6–8 server/GPU endpoints) running BGP/OSPF on FRRouting within Containerlab. Production-grade HA, multi-vendor ASIC drivers, and WAN-scale testing are designated as future work.

---

## 3. Related Work

### 3.1 AIOps and Intent-Based Networking

The term **AIOps** (Artificial Intelligence for IT Operations) was coined by Gartner in 2017 to describe platforms that combine big data, machine learning, and automation to enhance IT operations. Major commercial vendors (Moogsoft, BigPanda, Datadog) offer anomaly detection and event correlation, but their scope typically ends at alert enrichment, deduplication, and ticket routing—**not autonomous remediation**.

**Intent-Based Networking (IBN)**, championed by Cisco (DNA Center / Catalyst Center), Apstra (now Juniper Apstra), and the IETF's Network Management Research Group (NMRG), aims to translate high-level business intent into network configuration. While IBN systems can validate that configuration matches declarative intent, they generally lack real-time streaming anomaly detection, predictive multi-horizon forecasting, and closed-loop automated healing.

### 3.2 Digital Twin Approaches

Network digital twins create a virtual replica of the network for testing and verification:
- **Batfish** (Fogel et al., NSDI 2015): An open-source network configuration analysis tool that models the control plane offline. It can answer reachability, policy compliance, and routing simulation queries, but it does not incorporate live telemetry or perform continuous what-if resilience analysis.
- **Forward Networks**: A commercial platform that builds a mathematical model of the network for verification. It operates on periodic configuration and state snapshots rather than live sub-second streaming data.
- **VeriFlow / VMware NSX Intelligence** (Khurshid et al., NSDI 2013): Real-time verification of network forwarding invariants by checking the data plane after each update. Focuses strictly on correctness verification rather than predictive or automated healing.
- **Digital Twin Network (DTN)** (IETF `draft-irtf-nmrg-network-digital-twin`): Defines a reference architecture for network digital twins, but does not specify ML-driven anomaly detection, causal root-cause analysis, or autonomous remediation.

### 3.3 Chaos Engineering and Self-Healing

Netflix's **Chaos Monkey** (2011) pioneered the practice of deliberately injecting failures to test distributed system resilience. Gremlin and LitmusChaos extended this to network-layer faults (latency, packet loss, interface corruptions). However, chaos engineering is a testing and validation methodology, not an active production healing system—it identifies weaknesses but does not autonomously repair them.

Self-healing systems in the literature (e.g., IBM's Autonomic Computing manifesto, Kephart & Chess, 2003) define the classical **MAPE-K** loop (*Monitor, Analyze, Plan, Execute, Knowledge*). Our architecture directly implements MAPE-K but extends it with:
1. A **digital twin as a safety layer** ($\ge 85\%$ routing fidelity) serving as a preflight simulation sandbox;
2. **Continuous counterfactual reasoning** exploring failure permutations before incidents occur;
3. **Pre-computed recovery plans** cached in Redis for $< 2\text{ms}$ retrieval; and
4. An **immutable audit trail** via a SHA-256 hash-chained Black Box recorder with deterministic second-by-second forensic replay.

### 3.4 Gap Analysis

| System / Approach | Live Twin | Prediction | Auto-Heal | What-If | Black Box |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AIOps Platforms** | ❌ None | Partial | ❌ None | ❌ None | ❌ None |
| **Batfish** | Offline | ❌ None | ❌ None | Offline | ❌ None |
| **Forward Networks** | Snapshot | ❌ None | ❌ None | Snapshot | ❌ None |
| **VeriFlow** | ❌ None | ❌ None | ❌ None | ❌ None | ❌ None |
| **Chaos Engineering** | ❌ None | ❌ None | ❌ None | Testing | ❌ None |
| **This Project (Aexyron)** | **✅ 30s** | **✅ $\ge$20s** | **✅ L0–L4** | **✅ Live** | **✅ Replay** |

*Table 2: Feature comparison with related work.*

No existing system combines all five capabilities:
1. A **live, continuously-synchronized digital twin** (30s cycle, sub-second deltas, $\ge 85\%$ routing fidelity);
2. **ML-driven failure prediction** ($\ge 20\text{s}$ forecast horizon);
3. **Autonomous multi-level healing with guardrails** (L0–L4 governed by OPA);
4. **Continuous what-if counterfactual reasoning** with pre-computed recovery plan caching ($< 2\text{ms}$ lookup);
5. An **immutable, replayable event log** (SHA-256 hash-chained Black Box).

This project fills that critical gap.

---

## 4. System Architecture

The Self-Healing AI Network is organized into seven architectural layers, each with clearly defined responsibilities, interfaces, and failure modes. The design follows three core principles:
1. **Safety First**: No action without preflight simulation, invariant policy verification, and automated rollback capabilities.
2. **Explainability**: Every decision is traceable, backed by Bayesian causal attribution and human-readable incident narratives.
3. **Graduated Autonomy**: Operators maintain full control over the automation level across five formal tiers (L0–L4).

### 4.1 Seven-Layer Architecture

*Figure 1: Self-Healing AI Network — Seven-Layer Architecture*

```text
┌────────────────────────────────────────────────────────────────────────┐
│ LAYER 7: DECISION ENGINE + EXECUTION + BLACK BOX                       │
│  ┌────────────────┐    ┌────────────────┐    ┌──────────────────────┐  │
│  │   OPA Policy   │    │ Action         │    │  Network Black Box   │  │
│  │   Engine       │───►│ Executor       │───►│  (Kafka → S3/Disk)   │  │
│  │   (Rego rules) │    │ (gNMI/Ansible) │    │  Hash-chained replay │  │
│  └────────────────┘    └────────────────┘    └──────────────────────┘  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 6: ROOT-CAUSE ANALYSIS + RISK FUSION                             │
│  ┌────────────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│  │ Causal Graph       │    │ Bayesian       │    │ LLM Narrative    │  │
│  │ (Neo4j traversal)  │───►│ Inference      │───►│ Generator        │  │
│  └────────────────────┘    └────────────────┘    └──────────────────┘  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 5: WHAT-IF ENGINE                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐   ┌───────────┐ │
│  │ Failure      │    │ Routing      │    │ Risk      │   │ Recovery  │ │
│  │ Injection    │───►│ Reconvergence│───►│ Scoring   │──►│ Plan Cache│ │
│  │ Matrix       │    │ Simulator    │    │           │   │ (Redis)   │ │
│  └──────────────┘    └──────────────┘    └───────────┘   └───────────┘ │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 4: AI ANOMALY ENGINE                                             │
│  ┌────────────────┐    ┌────────────────┐    ┌──────────────────────┐  │
│  │ Isolation      │    │ XGBoost /      │    │ Optional GNN on      │  │
│  │ Forest (<5s)   │    │ TFT (≥20s)     │    │ Topology (PyG)       │  │
│  │ (per link)     │    │ (predictive)   │    │                      │  │
│  └────────────────┘    └────────────────┘    └──────────────────────┘  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 3: LIVE DIGITAL TWIN                                             │
│  ┌────────────────────┐    ┌────────────────┐    ┌──────────────────┐  │
│  │ Neo4j Topology     │    │ Config State   │    │ Routing Table    │  │
│  │ Graph (30s sync)   │    │ (Batfish)      │    │ Snapshots (FIB)  │  │
│  │                    │    │                │    │ + Live Metrics   │  │
│  └────────────────────┘    └────────────────┘    └──────────────────┘  │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 2: TELEMETRY BUS                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────────┐ │
│  │ gNMIc / OTel │───►│ Kafka Bus    │───►│ Prometheus (metrics)      │ │
│  │ sFlow / eBPF │    │ (>100k evt/s)│    │ ClickHouse (flows) / Loki │ │
│  └──────────────┘    └──────────────┘    └───────────────────────────┘ │
└───────────────────────────────────▲────────────────────────────────────┘
                                    │
┌───────────────────────────────────┴────────────────────────────────────┐
│ LAYER 1: DATA PLANE                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Servers / NIC│  │Switches (OVS) │  │Routers (FRR) │  │ GPUs / Hosts│ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └─────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

#### Detailed Layer Responsibilities

- **Layer 1: Data Plane**
  - Physical and virtual network infrastructure: 2-spine, 4-leaf Clos fabric running FRRouting (BGP unnumbered / ECMP) and Open vSwitch (OVS) with server endpoints hosting distributed GPU workloads.
- **Layer 2: Telemetry Bus**
  - High-throughput streaming bus ingesting multi-modal telemetry across `gNMIc` (hardware counters, optical power levels), `eBPF` (socket drops, TCP RTT distribution), `sFlow` (flow matrix sampling), and `OpenTelemetry`.
  - Ingestion backbone powered by **Apache Kafka** partitioned by device and interface hash at $> 100\text{k}$ events/sec, feeding long-term analytics into Prometheus, ClickHouse, and Loki.
- **Layer 3: Live Digital Twin**
  - **Neo4j**-backed property graph mirroring topology, device operational states, BGP peerings, and live queue buffer occupancy.
  - Maintains continuous 30-second full reconciliation with sub-second event-driven delta updates, achieving $\ge 85\%$ routing fidelity verified against switch FIB tables. Incorporates Batfish configuration parsing for declarative control-plane analysis.
- **Layer 4: AI Anomaly Engine**
  - **Fast-Path Detection (< 5s)**: Unsupervised Isolation Forests evaluate sliding statistical windows (mean, standard deviation, delta trend, latest value) to catch microburst drops and silent degradation.
  - **Predictive Failure Forecasting (≥ 20s ahead)**: Multi-horizon Temporal Fusion Transformers (TFT) and XGBoost forecast optical transceiver blowouts and buffer incast exhaustion.
  - **Topology-Aware GNN**: Optional graph neural network (PyTorch Geometric) for spatial graph embedding and cross-layer relational reasoning.
- **Layer 5: What-If Engine**
  - Continuously explores hypothetical failure branches on an in-memory clone of the digital twin *before* physical disruption occurs ($< 2\text{s}$ simulation time).
  - Evaluates topological failure matrices, simulates BGP/ECMP reconvergence, calculates downstream blast radii, and pre-caches signed recovery recipes in **Redis** for instant ($< 2\text{ms}$) execution.
- **Layer 6: Root-Cause Analysis + Risk Fusion**
  - **Causal Graph Traversal**: Disambiguates symptom cascades from primary root causes across topology and dependency DAGs.
  - **Bayesian Inference**: Computes posterior probabilities $P(\text{Root Cause } R_i \mid \text{Observed Symptoms } S_1 \dots S_k)$ to eliminate alert storms.
  - **LLM Narrative Generator**: Synthesizes structured, human-readable post-mortem explanations with timeline, root cause, and remediation rationale.
- **Layer 7: Decision Engine + Execution + Black Box**
  - **OPA Policy Engine**: Enforces invariant safety guardrails written in Rego across five autonomy levels (L0–L4).
  - **Preflight Sandbox & Canary Execution**: Candidate remediations are preflighted on the twin clone, deployed with a 5% traffic canary, and subject to automatic sub-1.5s rollback if telemetry regresses.
  - **Circuit Breaker**: Prevents remediation cascading if $> 3$ actions occur within 60s in the same failure domain.
  - **Network Black Box**: Append-only, SHA-256 hash-chained flight recorder guaranteeing mathematical auditability and deterministic second-by-second forensic incident replay.

### 4.2 Data Flow Narrative

The autonomous closed-loop operation executes along a continuous operational lifecycle:

1. **Telemetry Generation & Streaming Ingestion (L1 → L2)**:
   Physical and container switches (FRR/OVS) and GPU host interfaces stream high-frequency telemetry (gNMI counter ticks, eBPF socket drop events, optical transceiver power readings) to the Kafka bus at $> 100\text{k}$ events/sec.
2. **Digital Twin Synchronization & Reconciliation (L2 → L3)**:
   The Digital Twin synchronizer ingests Kafka event streams, updating graph node properties and link operational states in Neo4j within sub-second deltas, accompanied by a periodic 30-second full topology reconciliation.
3. **Proactive & Reactive Anomaly Detection (L2/L3 → L4)**:
   The AI Anomaly Engine inspects sliding window metrics. If sudden packet loss or queue surge occurs, the Isolation Forest flags an anomaly in $< 5\text{s}$. Concurrently, TFT/XGBoost models forecast impending transceiver blowouts $\ge 20\text{s}$ ahead.
4. **Counterfactual Pre-Computation & Cache Hit (L3 → L5)**:
   Prior to failure, the What-If Engine continuously simulates hypothetical link cuts and switch failures, scoring blast-radius impact and caching verified rerouting recipes in Redis. When an anomaly triggers, the system matches the fault signature to the cache, retrieving an optimal plan in $< 2\text{ms}$.
5. **Causal Attribution & Incident Narrative (L4/L5 → L6)**:
   The Root-Cause Analysis module traverses the Neo4j causal DAG, computes Bayesian posterior probabilities across candidate causes, eliminates downstream alert storms, and invokes the LLM narrative generator to produce an executive incident summary.
6. **Policy Gating, Canary Deployment & Rollback (L5/L6 → L7)**:
   The Decision Engine passes the candidate recovery action to the OPA policy engine. OPA validates autonomy constraints (L0–L4) and fabric safety invariants (max drained capacity $\le 25\%$, redundant GPU paths preserved). Upon approval, the Action Executor shifts a 5% canary. If health verifies for 10s, full remediation is committed; otherwise, sub-1.5s automatic rollback restores previous switch state.
7. **Cryptographic Black Box Commitment & Forensics (L7)**:
   Every telemetry tick, hypothesis, OPA decision, and actuation command is hashed into the append-only SHA-256 chain:
   $$H_n = \text{SHA256}(H_{n-1} \parallel \text{Timestamp} \parallel \text{EventType} \parallel \text{Payload})$$
   Auditors and NOC engineers can scrub through the incident second-by-second using the deterministic forensic replay CLI.

---

## 5. Autonomy Levels (L0 – L4) & Safety Guardrails

| Level | Designation | Execution Mode | Operator Involvement | Safe Failure Mode |
| :---: | :--- | :--- | :--- | :--- |
| **L0** | Alert Only | Passive Monitoring | Manual resolution | System displays causal diagnosis |
| **L1** | Operator Assisted | Recommended Plan | 1-Click approval required | Plan expires after 60s if unapproved |
| **L2** | Bounded Autonomous | Low-Risk Auto-Fix | Post-action notification | Hard-bounded to non-disruptive actions |
| **L3** | Conditional Autonomous | High-Impact Auto-Fix | Alerted with 15s pause override | Strict blast-radius limit ($< 15\%$ fabric) |
| **L4** | Fully Autonomous | Zero-Touch Closed-Loop | Zero-touch; audited in Black Box | Canary validation + instant rollback |

---

## 6. Empirical Benchmark Validation Results

The 500-trial statistical benchmark suite (`tests/test_benchmarks_e2e.py`) validates Aexyron against all target metrics across five randomized failure profiles:

```
================================================================================
  AEXYRON SELF-HEALING BENCHMARK RESULTS (500 Randomized Trials)
================================================================================
  Total Trials:           500 (100 iterations x 5 fault profiles)
  Recovery Success Rate:  100.0%  (target > 90%)
  Detection Rate:         100.0%  (target > 95%)
  False Positive Rate:    0.0%    (target < 5%)
  Black Box Integrity:    500/500 verified (100% cryptographic auditability)
  Predictive Alerts:      100/500 triggered (proactive mitigation enabled)

  MTTD (detection): mean=0.0009s  p50=0.0001s  p99=0.0050s  min=0.0000s  max=0.0053s
  MTTR (recovery) : mean=0.0258s  p50=0.0225s  p99=0.0326s  min=0.0197s  max=1.1221s
  Plan Cache Hit  : mean=0.0199ms p50=0.0184ms p99=0.0493ms min=0.0160ms max=0.1181ms

  Cost Impact Context:
    At $300K/hr baseline, MTTR reduction from 240s -> <15s saves
    ~$18,750 per incident ($300K * (240-15)/3600).
================================================================================
```

### Verified Quantitative Achievements
1. **MTTR Reduction**: Mean MTTR of **0.0258 seconds** compared to the industry manual NOC baseline of ~240 seconds (**> 9,000× faster** in automated simulation; easily exceeding the $< 15\text{s}$ target).
2. **Detection Latency (MTTD)**: Mean detection latency of **0.0009 seconds** ($< 5\text{s}$ target).
3. **Plan Cache Retrieval**: Mean retrieval latency of **0.0199 ms** ($< 2\text{ms}$ budget).
4. **False Positive Rate**: **0.0%** across 500 trials ($< 5\%$ target), effectively eliminating operator alert fatigue.
5. **Recovery Success Rate**: **100.0%** recovery success across all fault scenarios ($> 90\%$ target).
6. **Black Box Cryptographic Auditability**: **500/500** hash-chain integrity verifications passed without a single collision or verification failure.
