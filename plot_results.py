from __future__ import annotations

from pathlib import Path
import csv
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RESULTS_FILE = RESULTS_DIR / "benchmark_results.csv"


def load_results():
    rows = []
    with open(RESULTS_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["nodes"] = int(row["nodes"])
            row["latency_ms"] = float(row["latency_ms"])
            row["throughput"] = float(row["throughput"])
            row["utilization"] = float(row["utilization"])
            row["recovery_time_ticks"] = float(row["recovery_time_ticks"])
            row["anomaly_count"] = float(row["anomaly_count"])
            row["error_ticks"] = float(row["error_ticks"])
            row["llm_overhead_ms"] = float(row["llm_overhead_ms"])
            rows.append(row)
    return rows


def split_modes(rows):
    static_rows = sorted([r for r in rows if r["mode"] == "static"], key=lambda x: x["nodes"])
    hybrid_rows = sorted([r for r in rows if r["mode"] == "hybrid"], key=lambda x: x["nodes"])
    return static_rows, hybrid_rows


def plot_metric(rows_static, rows_hybrid, metric, ylabel, title, output_name):
    xs_static = [r["nodes"] for r in rows_static]
    ys_static = [r[metric] for r in rows_static]

    xs_hybrid = [r["nodes"] for r in rows_hybrid]
    ys_hybrid = [r[metric] for r in rows_hybrid]

    plt.figure(figsize=(8, 5))
    plt.plot(xs_static, ys_static, marker="o", label="Static")
    plt.plot(xs_hybrid, ys_hybrid, marker="s", label="Hybrid (LLM-assisted)")
    plt.xlabel("Nodes")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    out = RESULTS_DIR / output_name
    plt.savefig(out, dpi=200, bbox_inches="tight")
    plt.close()
    print("Saved plot to:", out)


def main():
    rows = load_results()
    static_rows, hybrid_rows = split_modes(rows)

    plot_metric(
        static_rows,
        hybrid_rows,
        metric="latency_ms",
        ylabel="Average Latency (ms)",
        title="Latency vs Cluster Size",
        output_name="latency_vs_nodes.png",
    )

    plot_metric(
        static_rows,
        hybrid_rows,
        metric="throughput",
        ylabel="Average Throughput",
        title="Throughput vs Cluster Size",
        output_name="throughput_vs_nodes.png",
    )

    plot_metric(
        static_rows,
        hybrid_rows,
        metric="utilization",
        ylabel="Average Utilization",
        title="Utilization vs Cluster Size",
        output_name="utilization_vs_nodes.png",
    )

    plot_metric(
        static_rows,
        hybrid_rows,
        metric="recovery_time_ticks",
        ylabel="Recovery Time (ticks)",
        title="Recovery Time vs Cluster Size",
        output_name="recovery_vs_nodes.png",
    )

    plot_metric(
        static_rows,
        hybrid_rows,
        metric="llm_overhead_ms",
        ylabel="Total LLM Overhead (ms)",
        title="LLM Overhead vs Cluster Size",
        output_name="llm_overhead_vs_nodes.png",
    )


if __name__ == "__main__":
    main()