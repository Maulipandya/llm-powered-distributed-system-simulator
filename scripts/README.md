# Scripts

This folder contains scripts used to run experiments and generate visualizations for the distributed system simulator.

## Files

### run_experiments.py

* Executes simulation experiments across different cluster sizes (16–128 nodes)
* Runs both static and hybrid (LLM-assisted) modes
* Aggregates results across multiple seeds
* Outputs:

  * CSV file (`results/benchmark_results.csv`)
  * JSON logs (`results/*.json`)

---

### plot_results.py

* Reads the aggregated CSV file
* Generates performance plots for key metrics:

  * latency
  * throughput
  * utilization
  * recovery time
  * LLM overhead
* Saves plots as `.png` files

---

## Usage

Run experiments:
python scripts/run_experiments.py

Generate plots:
python scripts/plot_results.py

---

## Summary

These scripts form the experimental pipeline:

Simulation → JSON logs → CSV aggregation → Plots

They ensure all results in the paper are reproducible.
