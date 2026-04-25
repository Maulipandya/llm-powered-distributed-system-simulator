# Results

This folder contains output data generated from simulation experiments.

## Files

### benchmark_results.csv

* Aggregated results across all runs
* Contains averaged metrics for each configuration
* Includes:

  * latency
  * throughput
  * utilization
  * recovery time
  * LLM overhead

---

### JSON Files (`*.json`)

* Detailed logs for each simulation run
* A total of multiple files are generated across:

  * different cluster sizes (16–128 nodes)
  * static and hybrid (LLM-assisted) modes
  * multiple random seeds

Each file follows this format:

`nodes_<N>_llm_<True/False>_seed_<S>.json`
---

## Usage

- CSV file is used for generating plots  
- JSON files provide detailed simulation logs and reproducibility  
---

## Summary

This folder contains:

- aggregated performance metrics (CSV)  
- detailed run-level logs (JSON)  

which support the results presented in the paper.
