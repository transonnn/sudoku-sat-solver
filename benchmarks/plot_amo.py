import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "benchmark_amo.csv"
OUTPUT_FILE = ROOT / "results" / "amo_encoding_comparison.png"

GROUPS = ("easy", "medium", "hard")
ENCODINGS = ("pairwise", "seqcounter")


def main():
    results = defaultdict(lambda: defaultdict(list))

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        for row in csv.DictReader(file):
            results[row["difficulty"]][row["encoding"]].append(
                float(row["median_time_seconds"])
            )

    medians = {
        group: {
            encoding: statistics.median(
                results[group][encoding]
            )
            for encoding in ENCODINGS
        }
        for group in GROUPS
    }

    x = list(range(len(GROUPS)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))

    pairwise = [medians[g]["pairwise"] for g in GROUPS]
    seqcounter = [medians[g]["seqcounter"] for g in GROUPS]

    ax.bar(
        [i - width / 2 for i in x],
        pairwise,
        width,
        label="Pairwise",
    )
    ax.bar(
        [i + width / 2 for i in x],
        seqcounter,
        width,
        label="Sequential Counter",
    )

    ax.set_title("Sudoku SAT: AMO Encoding Comparison")
    ax.set_xlabel("Puzzle group")
    ax.set_ylabel("Median solving time (seconds)")
    ax.set_xticks(x)
    ax.set_xticklabels([g.capitalize() for g in GROUPS])
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.3)

    fig.tight_layout()
    fig.savefig(OUTPUT_FILE, dpi=200)
    plt.close(fig)

    print(f"Chart saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
