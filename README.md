# LLM-Powered Distributed System Simulator

## Overview

This project implements a hybrid distributed system simulator that combines deterministic execution with LLM-assisted reasoning for workload generation, failure modeling, and semantic log analysis.

## Key Features

* Static vs Hybrid (LLM-assisted) simulation modes
* Adaptive workload generation
* Controlled failure injection (node, network, cascading)
* Semantic log analysis
* Reproducible experiment pipeline

## Architecture

The system includes:

* `DistributedSystemSimulator` (core engine)
* `WorkloadAgent` (workload generation)
* `FailureAgent` (failure modeling)
* `SemanticLogAgent` (log analysis)
* `LLMModule` (bounded reasoning layer)

## Metrics

* Latency
* Throughput
* Utilization
* Recovery Time
* LLM Overhead

## Results Summary

* Hybrid mode improves throughput
* LLM introduces additional latency overhead
* Recovery improves with scale in hybrid mode
* Demonstrates trade-off between adaptability and cost

## Structure

* `src/` → simulator
* `scripts/` → experiments & plotting
* `results/` → outputs (CSV, JSON)
* `plots/` → graphs
* `paper/` → report
* `slides/` → presentation

## How to Run

Run experiments:
python scripts/run_experiments.py

Generate plots:
python scripts/plot_results.py

## Team

Team 14 – LLM Study

