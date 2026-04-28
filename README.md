# LLM-Powered Distributed System Simulator

## 📌 Overview

This project presents a **hybrid distributed system simulator** that combines:

* **Deterministic execution** for reproducibility
* **LLM-assisted reasoning** for adaptability

The system models real-world behavior through:

* Adaptive workload generation
* Failure modeling (node, network, cascading)
* Semantic log analysis

---

## 🚀 Key Features

* Static vs **Hybrid (LLM-assisted)** simulation modes
* Controlled failure injection
* Realistic workload generation
* LLM-based log analysis
* Reproducible experiment pipeline

---

## 🏗️ Architecture

Core components:

* `DistributedSystemSimulator` (engine)
* `WorkloadAgent`, `FailureAgent`, `SemanticLogAgent`
* `LLMModule` (bounded reasoning layer)

👉 LLMs are used only for **high-level reasoning**, while execution remains deterministic.

---

## 📊 Metrics

* Latency
* Throughput
* Utilization
* Recovery Time
* LLM Overhead

---

## 📈 Results (Summary)

* Hybrid improves **throughput and utilization**
* Improves **recovery under failures**
* Trade-off: **increased latency due to LLM overhead**

---

## 📄 Paper

`paper/Team_14_LLM_Study_paper.pdf`
Detailed design, experiments, and evaluation.

---

## 📊 Presentation

`presentation/Team_14_LLM_Study_presentation.pptx`

Provides a **visual overview** of:

* Problem & motivation
* System architecture & workflow
* Experimental setup and results
* Key insights and trade-offs

---

## 📁 Structure

```id="3i0v5r"
src/        # simulator
scripts/    # experiments
results/    # outputs
plots/      # graphs
paper/      # report
presentation/ # slides
```

---

## ▶️ Run

```id="r6r03g"
python scripts/run_experiments.py
python scripts/plot_results.py
```

---

## 🔁 Reproducibility

Experiments can be reproduced using provided scripts. Results and plots are included.

---

## 👥 Team

**Team 14 – LLM Study**
