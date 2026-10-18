import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "benchmark_sat_cpsat_cplex.csv"
OUTPUT_DIR = ROOT / "results"

df = pd.read_csv(INPUT_FILE)

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

pivot = pivot.reindex(["easy", "medium", "hard"])
pivot = pivot.reindex(columns=["SAT", "CP-SAT", "CPLEX"])

ax = (pivot * 1000).plot(kind="bar", figsize=(10, 6))

ax.set_title("Sudoku Solver Performance: SAT vs CP-SAT vs CPLEX")
ax.set_xlabel("Difficulty")
ax.set_ylabel("Mean solving time (ms)")
ax.tick_params(axis="x", rotation=0)
ax.legend(title="Solver")

plt.tight_layout()

output_file = OUTPUT_DIR / "sat_vs_cpsat_cplex.png"
plt.savefig(output_file, dpi=300)
plt.close()

print(f"Chart saved to: {output_file}")
print("\nMean solving time (ms):")
print((pivot * 1000).round(3).to_string())
