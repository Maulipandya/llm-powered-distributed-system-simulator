# Scripts

This folder contains the scripts used to run simulations and generate plots.

## Files

### run_experiments.py

* Runs the distributed system simulator across different cluster sizes
* Executes both static and hybrid (LLM-assisted) modes
* Collects results from multiple runs
* Saves outputs to:

  * `results/benchmark_results.csv`
  * `results/*.json`

---

### plot_results.py

* Reads the CSV results file
* Generates plots for:

  * latency
  * throughput
  * utilization
  * recovery time
  * LLM overhead
* Saves plots as `.png` images

---

## Usage

Run experiments:
python scripts/run_experiments.py

Generate plots:
python scripts/plot_results.py

---

## Pipeline

Simulation → JSON logs → CSV aggregation → Plots
