# Plots and Results Overview

This folder contains visualization outputs generated from the distributed system simulator experiments.

## Files

### Plots (`.png`)

These images represent key performance metrics across different cluster sizes (16–128 nodes):

* `latency_vs_nodes.png` → Average latency comparison
* `throughput_vs_nodes.png` → System throughput comparison
* `utilization_vs_nodes.png` → Resource utilization trends
* `recovery_vs_nodes.png` → Recovery time after failures
* `llm_overhead_vs_nodes.png` → LLM reasoning overhead

Each plot compares:

* **Static mode** (deterministic simulation)
* **Hybrid mode** (LLM-assisted simulation)

---

## Data Sources

### CSV File

The plots are generated from:

```
results/benchmark_results.csv
```

This file contains aggregated metrics averaged across multiple runs and seeds, including:

* latency
* throughput
* utilization
* recovery time
* LLM overhead

---

### JSON Files

Located in:

```
results/*.json
```

These files store detailed outputs for each simulation run:

* per-tick logs
* workload behavior
* failure events
* system metrics

Each JSON corresponds to a specific configuration:

```
nodes_<N>_llm_<True/False>_seed_<S>.json
```

---

## Generation

Plots are generated using:

```
scripts/plot_results.py
```

which reads the CSV file and produces visual comparisons between static and hybrid modes.

---

## Summary

The visualizations demonstrate:

* Higher throughput in hybrid (LLM-assisted) mode
* Increased latency due to LLM overhead
* Improved recovery behavior at larger scales
* Trade-offs between adaptability and performance

These results support the findings discussed in the paper.
