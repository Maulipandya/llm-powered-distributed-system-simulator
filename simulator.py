from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import json
import math
import random


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SimulationConfig:
    # Cluster
    nodes: int = 32
    gpus_per_node: int = 8

    # Network + runtime
    base_latency_ms: float = 1.0
    bandwidth_gbps: float = 100.0
    ticks: int = 120
    seed: int = 42

    # Modes
    llm_enabled: bool = True
    workload_mode: str = "hybrid"     # "static" or "hybrid"
    failure_mode: str = "controlled"  # "none", "controlled", "stress"

    # Workload + failures
    target_rps: int = 4200
    failure_tick: int = 70
    output_dir: str = "results"

    # Optional external hook for real LLM integration
    # Expected signature:
    #   fn(task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]
    llm_callback: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None


# =============================================================================
# Guardrails / schema validation
# =============================================================================

class SchemaValidator:
    @staticmethod
    def bounded_float(value: Any, low: float, high: float, default: float) -> float:
        try:
            value = float(value)
        except (TypeError, ValueError):
            return default
        return max(low, min(high, value))

    @staticmethod
    def bounded_int(value: Any, low: int, high: int, default: int) -> int:
        try:
            value = int(value)
        except (TypeError, ValueError):
            return default
        return max(low, min(high, value))

    @staticmethod
    def workload_schema(raw: Dict[str, Any]) -> Dict[str, float]:
        return {
            "context_score": SchemaValidator.bounded_float(raw.get("context_score"), 0.0, 1.0, 0.50),
            "burstiness": SchemaValidator.bounded_float(raw.get("burstiness"), 0.0, 0.25, 0.08),
            "priority_mix": SchemaValidator.bounded_float(raw.get("priority_mix"), 0.0, 1.0, 0.45),
        }

    @staticmethod
    def failure_schema(raw: Dict[str, Any], total_nodes: int) -> Dict[str, float]:
        return {
            "failed_nodes": SchemaValidator.bounded_int(raw.get("failed_nodes"), 1, max(1, total_nodes // 3), 3),
            "network_penalty": SchemaValidator.bounded_float(raw.get("network_penalty"), 1.0, 2.0, 1.25),
            "recovery_ticks": SchemaValidator.bounded_int(raw.get("recovery_ticks"), 4, 20, 10),
            "cascade_factor": SchemaValidator.bounded_float(raw.get("cascade_factor"), 0.0, 0.4, 0.10),
        }


# =============================================================================
# Bounded LLM module
# =============================================================================

class LLMModule:
    """
    Bounded reasoning layer.
    - If llm_callback is provided, it can be used for real LLM-backed outputs.
    - Otherwise a deterministic seeded fallback is used.
    - All outputs are schema-validated before use.
    """

    def __init__(
        self,
        rng: random.Random,
        enabled: bool,
        total_nodes: int,
        callback: Optional[Callable[[str, Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.rng = rng
        self.enabled = enabled
        self.total_nodes = total_nodes
        self.callback = callback

    def _fallback_workload_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        progress = payload["progress"]
        pressure = payload["recent_pressure"]

        context_score = 0.45 + 0.45 * progress + 0.08 * pressure
        burstiness = 0.05 + 0.12 * self.rng.random() + 0.03 * progress
        priority_mix = 0.40 + 0.25 * progress + 0.10 * self.rng.random()

        return {
            "context_score": context_score,
            "burstiness": burstiness,
            "priority_mix": priority_mix,
        }

    def _fallback_failure_plan(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        severity = payload["severity"]
        pressure = payload["pressure"]

        failed_nodes = 2 + int(severity * 2)
        network_penalty = 1.15 + 0.15 * severity + 0.10 * pressure
        recovery_ticks = 11 + int(severity * 4)
        cascade_factor = 0.08 + 0.15 * severity

        return {
            "failed_nodes": failed_nodes,
            "network_penalty": network_penalty,
            "recovery_ticks": recovery_ticks,
            "cascade_factor": cascade_factor,
        }

    def _fallback_log_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        latency = payload["latency_ms"]
        errors = payload["errors"]
        util = payload["utilization"]
        queue_ratio = payload["queue_ratio"]
        burstiness = payload["burstiness"]

        if errors > 12:
            label = "error_spike"
            explanation = "Elevated request failures likely caused by injected fault and temporary service disruption."
            severity = 3
        elif queue_ratio > 0.25 and latency > 6.0:
            label = "queue_saturation"
            explanation = "Latency increase is dominated by queue buildup near effective capacity."
            severity = 3
        elif burstiness > 0.14 and latency > 4.5:
            label = "traffic_anomaly"
            explanation = "Burst-sensitive latency rise detected under dynamic workload conditions."
            severity = 2
        elif util > 0.90:
            label = "capacity_pressure"
            explanation = "High utilization indicates resource pressure with limited headroom."
            severity = 2
        else:
            label = "normal"
            explanation = "System is operating within expected bounds."
            severity = 0

        return {
            "label": label,
            "severity": severity,
            "explanation": explanation,
        }

    def _call(self, task_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        if self.callback is not None:
            try:
                response = self.callback(task_name, payload)
                if isinstance(response, dict):
                    return response
            except Exception:
                pass

        if task_name == "workload_plan":
            return self._fallback_workload_plan(payload)
        if task_name == "failure_plan":
            return self._fallback_failure_plan(payload)
        if task_name == "log_summary":
            return self._fallback_log_summary(payload)

        return {}

    def reasoning_overhead_ms(self, task_complexity: float) -> float:
        if not self.enabled:
            return 0.0
        base = 2.5 + 2.0 * task_complexity
        jitter = self.rng.uniform(0.8, 2.0)
        return base + jitter

    def workload_guidance(self, payload: Dict[str, Any]) -> Dict[str, float]:
        if not self.enabled:
            return {
                "context_score": 0.05,
                "burstiness": 0.02,
                "priority_mix": 0.35,
            }
        raw = self._call("workload_plan", payload)
        return SchemaValidator.workload_schema(raw)

    def failure_guidance(self, payload: Dict[str, Any]) -> Dict[str, float]:
        if not self.enabled:
            return {
                "failed_nodes": 3,
                "network_penalty": 1.25,
                "recovery_ticks": 12,
                "cascade_factor": 0.08,
            }
        raw = self._call("failure_plan", payload)
        return SchemaValidator.failure_schema(raw, self.total_nodes)

    def log_reasoning(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return self._fallback_log_summary(payload)
        return self._call("log_summary", payload)


# =============================================================================
# Modular agent-like components
# =============================================================================

class WorkloadAgent:
    def __init__(self, rng: random.Random, cfg: SimulationConfig, llm: LLMModule):
        self.rng = rng
        self.cfg = cfg
        self.llm = llm

    def generate(
        self,
        tick: int,
        total_ticks: int,
        recent_pressure: float,
    ) -> Dict[str, float]:
        progress = tick / max(total_ticks - 1, 1)

        ramp = self.cfg.target_rps * (0.40 + 0.60 * progress)
        seasonal = 180.0 * math.sin((2.0 * math.pi * tick) / max(12, total_ticks // 2))
        noise = self.rng.randint(-120, 140)

        if self.cfg.workload_mode == "static":
            requests = ramp + 0.30 * seasonal + noise
            return {
                "requests": max(100, int(requests)),
                "burstiness": 0.02,
                "context_score": 0.05,
                "priority_mix": 0.35,
                "llm_overhead_ms": 0.0,
            }

        guidance = self.llm.workload_guidance(
            {
                "tick": tick,
                "progress": progress,
                "recent_pressure": recent_pressure,
                "target_rps": self.cfg.target_rps,
            }
        )

        context_score = guidance["context_score"]
        burstiness = guidance["burstiness"]
        priority_mix = guidance["priority_mix"]

        adaptive_multiplier = 1.0 + 0.22 * context_score + 0.10 * priority_mix
        burst_spike = self.cfg.target_rps * burstiness * (0.20 + self.rng.random())

        requests = (ramp + seasonal + noise + burst_spike) * adaptive_multiplier

        llm_overhead = self.llm.reasoning_overhead_ms(task_complexity=0.8 + context_score)

        return {
            "requests": max(100, int(requests)),
            "burstiness": burstiness,
            "context_score": context_score,
            "priority_mix": priority_mix,
            "llm_overhead_ms": llm_overhead,
        }


class FailureAgent:
    def __init__(self, rng: random.Random, cfg: SimulationConfig, llm: LLMModule):
        self.rng = rng
        self.cfg = cfg
        self.llm = llm

    def event(self, tick: int, pressure: float) -> Optional[Dict[str, float]]:
        if self.cfg.failure_mode == "none":
            return None

        should_fail = tick == self.cfg.failure_tick
        if self.cfg.failure_mode == "stress":
            should_fail = tick in {self.cfg.failure_tick, min(self.cfg.ticks - 1, self.cfg.failure_tick + 18)}

        if not should_fail:
            return None

        severity = 0.35 + 0.45 * pressure + 0.10 * self.rng.random()

        if self.cfg.llm_enabled:
            plan = self.llm.failure_guidance(
                {
                    "tick": tick,
                    "pressure": pressure,
                    "severity": severity,
                    "nodes": self.cfg.nodes,
                }
            )
        else:
            plan = {
                "failed_nodes": 2 + self.rng.randint(0, 2),
                "network_penalty": 1.20 + 0.10 * self.rng.random(),
                "recovery_ticks": 10 + self.rng.randint(0, 4),
                "cascade_factor": 0.08 + 0.04 * self.rng.random(),
            }

        fault_type = self.rng.choice(["node_failure", "network_partition", "cascading_failure"])

        return {
            "fault_type": fault_type,
            "failed_nodes": int(plan["failed_nodes"]),
            "network_penalty": float(plan["network_penalty"]),
            "recovery_ticks": int(plan["recovery_ticks"]),
            "cascade_factor": float(plan["cascade_factor"]),
            "llm_overhead_ms": self.llm.reasoning_overhead_ms(task_complexity=1.0 + severity) if self.cfg.llm_enabled else 0.0,
        }


class SemanticLogAgent:
    def __init__(self, llm: LLMModule):
        self.llm = llm

    def classify(self, log: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "latency_ms": log["latency_ms"],
            "throughput": log["throughput"],
            "utilization": log["utilization"],
            "errors": log["errors"],
            "queue_ratio": log["queue_ratio"],
            "burstiness": log["burstiness"],
            "fault_active": log["fault_active"],
        }

        result = self.llm.log_reasoning(payload)

        label = result.get("label", "normal")
        severity = int(result.get("severity", 0))
        explanation = str(result.get("explanation", "No explanation available."))

        if label not in {
            "normal",
            "traffic_anomaly",
            "capacity_pressure",
            "queue_saturation",
            "error_spike",
        }:
            label = "normal"

        severity = max(0, min(3, severity))

        return {
            "semantic_label": label,
            "semantic_severity": severity,
            "semantic_explanation": explanation,
        }


# =============================================================================
# Core simulator
# =============================================================================

class DistributedSystemSimulator:
    def __init__(self, cfg: SimulationConfig):
        self.cfg = cfg
        self.rng = random.Random(cfg.seed)

        self.total_capacity = cfg.nodes * cfg.gpus_per_node * 18

        self.llm = LLMModule(
            rng=self.rng,
            enabled=cfg.llm_enabled,
            total_nodes=cfg.nodes,
            callback=cfg.llm_callback,
        )
        self.workload_agent = WorkloadAgent(self.rng, cfg, self.llm)
        self.failure_agent = FailureAgent(self.rng, cfg, self.llm)
        self.semantic_agent = SemanticLogAgent(self.llm)

    def run(self) -> Dict[str, Any]:
        logs: List[Dict[str, Any]] = []

        active_failures: List[Dict[str, Any]] = []
        recovery_windows: List[int] = []
        total_llm_overhead_ms = 0.0

        for tick in range(self.cfg.ticks):
            recent_pressure = 0.0
            if logs:
                recent_pressure = min(1.0, (logs[-1]["queue_ratio"] + logs[-1]["utilization"]) / 2.0)

            new_fault = self.failure_agent.event(tick, pressure=recent_pressure)
            if new_fault is not None:
                active_failures.append(
                    {
                        "fault_type": new_fault["fault_type"],
                        "failed_nodes": new_fault["failed_nodes"],
                        "network_penalty": new_fault["network_penalty"],
                        "remaining_ticks": new_fault["recovery_ticks"],
                        "cascade_factor": new_fault["cascade_factor"],
                    }
                )
                recovery_windows.append(int(new_fault["recovery_ticks"]))
                total_llm_overhead_ms += float(new_fault["llm_overhead_ms"])

            workload = self.workload_agent.generate(
                tick=tick,
                total_ticks=self.cfg.ticks,
                recent_pressure=recent_pressure,
            )
            total_llm_overhead_ms += float(workload["llm_overhead_ms"])

            total_failed_nodes = sum(f["failed_nodes"] for f in active_failures)
            total_failed_nodes = min(total_failed_nodes, self.cfg.nodes - 1)

            network_penalty = 1.0
            cascade_penalty = 0.0
            dominant_fault_type = "none"

            if active_failures:
                dominant_fault = max(active_failures, key=lambda x: x["network_penalty"] + x["cascade_factor"])
                dominant_fault_type = dominant_fault["fault_type"]
                network_penalty = max(f["network_penalty"] for f in active_failures)
                cascade_penalty = sum(f["cascade_factor"] for f in active_failures)

            effective_capacity = max(
                1.0,
                self.total_capacity
                - total_failed_nodes * self.cfg.gpus_per_node * 18
                - cascade_penalty * 0.12 * self.total_capacity
            )

            requests = workload["requests"]
            burstiness = workload["burstiness"]
            context_score = workload["context_score"]
            priority_mix = workload["priority_mix"]

            throughput = min(float(requests), effective_capacity)
            queue_ratio = max(0.0, (requests - effective_capacity) / effective_capacity)

            bandwidth_factor = max(0.55, min(1.25, self.cfg.bandwidth_gbps / 100.0))
            network_delay = (network_penalty - 1.0) * 2.2 / bandwidth_factor

            latency_ms = (
                self.cfg.base_latency_ms
                + 2.6 * queue_ratio
                + 13.5 * (queue_ratio ** 2)
                + 1.9 * burstiness
                + 0.9 * context_score
                + network_delay
                + (workload["llm_overhead_ms"] / 8.0)
            )

            if active_failures:
                latency_ms += 0.25 * len(active_failures)

            utilization = min(1.0, throughput / self.total_capacity)

            errors = 0
            if active_failures:
                errors += int(requests * 0.0015 * len(active_failures))
                if dominant_fault_type == "network_partition":
                    errors += int(requests * 0.0008)
                elif dominant_fault_type == "cascading_failure":
                    errors += int(requests * 0.0012)

            log = {
                "tick": tick,
                "requests": requests,
                "throughput": round(throughput, 3),
                "latency_ms": round(latency_ms, 4),
                "utilization": round(utilization, 4),
                "errors": int(errors),
                "queue_ratio": round(queue_ratio, 4),
                "burstiness": round(burstiness, 4),
                "context_score": round(context_score, 4),
                "priority_mix": round(priority_mix, 4),
                "fault_active": bool(active_failures),
                "fault_type": dominant_fault_type,
                "failed_nodes": int(total_failed_nodes),
                "network_penalty": round(network_penalty, 4),
                "active_failure_count": len(active_failures),
            }

            semantic = self.semantic_agent.classify(log)
            log.update(semantic)
            logs.append(log)

            # advance failures
            next_failures = []
            for f in active_failures:
                f["remaining_ticks"] -= 1
                if f["remaining_ticks"] > 0:
                    next_failures.append(f)
            active_failures = next_failures

        recovery_time = sum(recovery_windows) / len(recovery_windows) if recovery_windows else 0.0
        anomaly_count = sum(1 for x in logs if x["semantic_label"] != "normal")
        error_ticks = sum(1 for x in logs if x["errors"] > 0)

        summary = {
            "avg_latency_ms": round(sum(x["latency_ms"] for x in logs) / len(logs), 4),
            "avg_throughput": round(sum(x["throughput"] for x in logs) / len(logs), 4),
            "avg_utilization": round(sum(x["utilization"] for x in logs) / len(logs), 4),
            "avg_recovery_time_ticks": round(recovery_time, 4),
            "anomaly_count": int(anomaly_count),
            "error_ticks": int(error_ticks),
            "total_llm_overhead_ms": round(total_llm_overhead_ms, 4),
        }

        return {
            "config": asdict(self.cfg),
            "summary": summary,
            "logs": logs,
        }


# =============================================================================
# File helpers
# =============================================================================

def save_run(result: Dict[str, Any], output_dir: str, name: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    cfg = SimulationConfig()
    sim = DistributedSystemSimulator(cfg)
    result = sim.run()
    save_run(result, cfg.output_dir, "single_run_demo")
    print("Saved:", Path(cfg.output_dir) / "single_run_demo.json")
    print("Summary:", result["summary"])