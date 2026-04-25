from __future__ import annotations

from pathlib import Path
from statistics import mean
import csv
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulator import DistributedSystemSimulator, SimulationConfig, save_run

OUTPUT = PROJECT_ROOT / "results"
OUTPUT.mkdir(exist_ok=True)


def run() -> None:
    rows = []

    for nodes in [16, 32, 64, 128]:
        for llm_enabled in [False, True]:
            summaries = []

            for seed in [7, 21, 42]:
                cfg = SimulationConfig(
                    nodes=nodes,
                    gpus_per_node=8,
                    llm_enabled=llm_enabled,
                    workload_mode="hybrid" if llm_enabled else "static",
                    failure_mode="controlled",
                    ticks=120,
                    seed=seed,
                    target_rps=4200,
                    failure_tick=70,
                    base_latency_ms=0.5 if nodes <= 32 else 1.2,
                    bandwidth_gbps=50 if nodes <= 32 else 150,
                    output_dir=str(OUTPUT),
                )

                sim = DistributedSystemSimulator(cfg)
                result = sim.run()

                name = f"nodes_{nodes}_llm_{llm_enabled}_seed_{seed}"
                save_run(result, str(OUTPUT), name)

                s = result["summary"]
                summaries.append(s)

            rows.append(
                {
                    "nodes": nodes,
                    "mode": "hybrid" if llm_enabled else "static",
                    "latency_ms": round(mean(x["avg_latency_ms"] for x in summaries), 4),
                    "throughput": round(mean(x["avg_throughput"] for x in summaries), 4),
                    "utilization": round(mean(x["avg_utilization"] for x in summaries), 4),
                    "recovery_time_ticks": round(mean(x["avg_recovery_time_ticks"] for x in summaries), 4),
                    "anomaly_count": round(mean(x["anomaly_count"] for x in summaries), 4),
                    "error_ticks": round(mean(x["error_ticks"] for x in summaries), 4),
                    "llm_overhead_ms": round(mean(x["total_llm_overhead_ms"] for x in summaries), 4),
                }
            )

    out_file = OUTPUT / "benchmark_results.csv"
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "nodes",
                "mode",
                "latency_ms",
                "throughput",
                "utilization",
                "recovery_time_ticks",
                "anomaly_count",
                "error_ticks",
                "llm_overhead_ms",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Done. Results saved to:", out_file)


if __name__ == "__main__":
    run()