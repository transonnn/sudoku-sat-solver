import csv
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "results" / "benchmark_amo.csv"


def main():
    results = defaultdict(dict)

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["difficulty"], int(row["instance"]))
            results[key][row["encoding"]] = float(
                row["median_time_seconds"]
            )

    print("AMO encoding benchmark analysis")
    print("=" * 65)

    for difficulty in ("easy", "medium", "hard"):
        pairs = [
            values
            for (group, _), values in results.items()
            if group == difficulty
        ]

        if not pairs or any(
            "pairwise" not in p or "seqcounter" not in p
            for p in pairs
        ):
            raise ValueError(
                f"Missing benchmark results for {difficulty}."
            )

        pairwise_times = [p["pairwise"] for p in pairs]
        seqcounter_times = [p["seqcounter"] for p in pairs]

        pairwise_median = statistics.median(pairwise_times)
        seqcounter_median = statistics.median(seqcounter_times)

        wins = sum(
            p["seqcounter"] < p["pairwise"] for p in pairs
        )

        if seqcounter_median > 0:
            speedup = pairwise_median / seqcounter_median
        else:
            speedup = float("inf")

        print(f"\nGroup: {difficulty} ({len(pairs)} puzzles)")
        print(f"  Pairwise median:  {pairwise_median:.6f} s")
        print(f"  SeqCounter median: {seqcounter_median:.6f} s")
        print(f"  SeqCounter faster: {wins}/{len(pairs)} puzzles")

        if speedup > 1:
            print(f"  Median speedup: {speedup:.3f}x (SeqCounter)")
        elif speedup < 1:
            print(f"  Median speedup: {1 / speedup:.3f}x (Pairwise)")
        else:
            print("  Median speedup: equal")

    print("\nAnalysis completed.")


if __name__ == "__main__":
    main()
