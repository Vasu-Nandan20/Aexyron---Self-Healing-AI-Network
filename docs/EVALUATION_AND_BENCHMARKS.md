# Evaluation Methodology & Benchmark Suite

This document defines the benchmarking framework, simulated topologies, fault injection profiles, and evaluation metrics used to quantify the performance of **Aexyron** against human operator and rule-based baselines.

---

## 1. Primary Evaluation Metrics & Proposed Targets

| Metric | Industry Baseline (Manual NOC) | Rule-Based Scripts | Aexyron (Target Result) | Improvement Factor |
| :--- | :--- | :--- | :--- | :--- |
| **Mean Time to Detect (MTTD)** | ~90 seconds | ~30 seconds | **< 5 seconds** | **18× faster** |
| **Failure Lead Time (Predictive)** | 0s (reactive only) | 0s (reactive only) | **20+ seconds ahead** | **Proactive mitigation** |
| **Mean Time to Recovery (MTTR)** | ~240 seconds (4 min) | ~60 seconds | **< 15 seconds** | **16× improvement** |
| **False Positive Rate (FPR)** | ~18% (alert fatigue) | ~25% (static limits) | **< 5%** | **> 3.5× cleaner signal** |
| **Recovery Success Rate** | 82% (manual errors) | 71% (fragile scripts) | **> 90%** | **High operational yield** |
| **Post-Action Degradation Rate** | ~12% (unintended side-effects) | ~19% | **< 2%** | **Formal OPA validation** |

---

## 2. Experimental Testbed: Containerlab Topology

The evaluation environment is hosted in **Containerlab** using Linux network containers running FRRouting (FRR) or virtualized switch network operating systems (Arista cEOS / SONiC).

```
          [Spine-01]        [Spine-02]
         /    |    \       /    |    \
        /     |     \     /     |     \
    [Leaf-01] [Leaf-02] [Leaf-03] [Leaf-04]
      |   |     |   |     |   |     |   |
     [H1] [H2] [H3] [H4] [H5] [H6] [H7] [H8] (GPU & Traffic Endpoints)
```

- **Topology**: 2 Spine, 4 Leaf Clos fabric with 8 host/GPU nodes.
- **Routing Protocol**: eBGP unnumbered with ECMP across spines.
- **Traffic Patterns**:
  - Continuous baseline background traffic (HTTP, RPCs).
  - High-bandwidth AllReduce / Incast synthetic traffic simulating distributed GPU machine learning workloads (simulating NCCL collective communications).

---

## 3. Failure Injection Profiles

To rigorously test detection, prediction, and self-healing, the benchmark test harness injects five distinct failure modes:

### 1. Hard Physical Link Failure
- **Mechanism**: Instantaneous interface shutdown or cable pull (`ip link set down`).
- **Challenge**: Fast path recalculation, BGP convergence, avoiding packet blackholes.

### 2. Silent Packet Drop (Grey Failure)
- **Mechanism**: Injected packet drop via `tc netem loss 5%..20%` or corrupted checksums without link state change.
- **Challenge**: Standard SNMP/link monitoring remains green; requires eBPF socket monitoring and interface drop counter anomaly detection.

### 3. Route Flapping & BGP Instability
- **Mechanism**: Intermittent BGP peer flapping injected every 10 seconds.
- **Challenge**: Damping policy enforcement, preventing route oscillation storms across ECMP groups.

### 4. ECMP Hash Polarization / Traffic Imbalance
- **Mechanism**: Path hashing collisions causing a single spine link to reach 100% buffer utilization while sibling links remain idle.
- **Challenge**: Microburst queue detection, dynamic cost-weight adjustments, and traffic re-balancing.

### 5. Priority Flow Control (PFC) Deadlock & Buffer Incast
- **Mechanism**: RoCEv2 buffer saturation causing pause frame storms across the fabric.
- **Challenge**: Rapid identification of the root-cause ingress port and targeted rate throttling.

---

## 4. Benchmark Execution & Statistical Rigor

- **Trial Sample Size**: Minimum of 100 randomized failure trials per profile across varying background traffic loads (30%, 60%, 90% link saturation).
- **Control Group**: Human operator baseline measured with experienced network engineers responding to standard dashboard alerts and executing recovery playbooks.
- **Automated Validation**:
  - Telemetry verification running 60 seconds post-remediation.
  - End-to-end packet delivery and throughput verified via continuous UDP/TCP probes.
