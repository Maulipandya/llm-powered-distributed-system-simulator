# Source Code

This folder contains the core implementation of the LLM-powered distributed system simulator.

## Files

### simulator.py

Implements the main simulation engine and system components, including:

* `DistributedSystemSimulator` → core simulation loop
* `SimulationConfig` → configuration parameters
* `WorkloadAgent` → workload generation (static and hybrid modes)
* `FailureAgent` → failure injection (node, network, cascading)
* `SemanticLogAgent` → log analysis and anomaly detection
* `LLMModule` → bounded reasoning layer for adaptive behavior

---

### **init**.py

Marks the folder as a Python package.

---

## Summary

This module integrates deterministic simulation with LLM-assisted reasoning to model performance, failures, and system behavior in distributed environments.
