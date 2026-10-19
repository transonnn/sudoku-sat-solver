import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "benchmark_scaled_all_solvers.csv"
OUTPUT_DIR = ROOT / "results"

df = pd.read_csv(INPUT_FILE)

df["size"] = df["size"].astype(int)
df["time_seconds"] = pd.to_numeric(df["time_seconds"], errors="coerce")

# Only include successful, valid solutions.
df = df[
    (df["status"] == "SOLVED")
    & (df["valid"].astype(str).str.lower() == "true")
].copy()

summary = (
    df.groupby(["size", "solver"])["time_seconds"]
    .agg(["mean", "median"])
    .reset_index()
)

solver_order = ["SAT", "CP-SAT", "CPLEX MIP", "Gurobi"]

for size in sorted(summary["size"].unique()):
    subset = summary[summary["size"] == size]
    pivot = subset.pivot(
        index="solver",
        columns=None,
        values="mean",
    ) if False else subset.set_index("solver")["mean"]

    pivot = pivot.reindex(solver_order).dropna()

    fig, ax = plt.subplots(figsize=(9, 5))
    pivot.plot(kind="bar", ax=ax)

    ax.set_title(f"Sudoku {size}x{size}: Solver Performance")
    ax.set_xlabel("Solver")
    ax.set_ylabel("Mean solving time (seconds)")
    ax.tick_params(axis="x", rotation=0)

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=3, fontsize=8)

    plt.tight_layout()
    output_file = OUTPUT_DIR / f"scaled_sudoku_{size}x{size}_comparison.png"
    plt.savefig(output_file, dpi=300)
    plt.close(fig)
    print(f"Chart saved to: {output_file}")

print("\nMean and median solving time (seconds):")
print(summary.sort_values(["size", "mean"]).round(3).to_string(index=False))
