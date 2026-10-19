import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = (
    ROOT
    / "results"
    / "benchmark_sat_cpsat_cplex_mip_cplex_cp_gurobi.csv"
)
OUTPUT_DIR = ROOT / "results"

df = pd.read_csv(INPUT_FILE)

expected_solvers = ["SAT", "CP-SAT", "CPLEX MIP", "CPLEX CP", "Gurobi"]
actual_solvers = set(df["solver"].unique())

missing_solvers = set(expected_solvers) - actual_solvers
if missing_solvers:
    raise ValueError(f"Missing solvers in benchmark CSV: {sorted(missing_solvers)}")

summary = (
    df.groupby(["difficulty", "solver"])["median_time_seconds"]
    .mean()
    .reset_index()
)

pivot = summary.pivot(
    index="difficulty",
    columns="solver",
    values="median_time_seconds",
)

pivot = pivot.reindex(index=["easy", "medium", "hard"])
pivot = pivot.reindex(columns=expected_solvers)

if pivot.isna().any().any():
    raise ValueError("Missing benchmark results for one or more difficulty/solver pairs.")

ax = (pivot * 1000).plot(kind="bar", figsize=(12, 6))

ax.set_title("Sudoku Solver Performance: Five-Solver Comparison")
ax.set_xlabel("Difficulty")
ax.set_ylabel("Mean of per-puzzle median solving time (ms)")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="Solver")

plt.tight_layout()

output_file = OUTPUT_DIR / "sat_vs_cpsat_cplex_gurobi.png"
plt.savefig(output_file, dpi=300)
plt.close()

print(f"Chart saved to: {output_file}")
print("\nMean of per-puzzle median solving time (ms):")
print((pivot * 1000).round(3).to_string())
