import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "benchmark_sat_cpsat.csv"
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

ax = pivot.plot(kind="bar", figsize=(9, 5))

ax.set_title("Sudoku Solver Performance: SAT vs CP-SAT")
ax.set_xlabel("Difficulty")
ax.set_ylabel("Median solving time (seconds)")
ax.tick_params(axis="x", rotation=0)

plt.tight_layout()

output_file = OUTPUT_DIR / "sat_vs_cpsat.png"
plt.savefig(output_file, dpi=300)
plt.show()

print(f"Chart saved to: {output_file}")
