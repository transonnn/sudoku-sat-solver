import csv
import json
import statistics
import time
from pathlib import Path

from benchmarks.benchmark import is_valid_solution, load_datasets
from src.sudoku_sat import solve_sudoku


ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
OUTPUT_FILE = RESULTS_DIR / "benchmark_amo.csv"

RUNS = 5
ENCODINGS = ("pairwise", "seqcounter")


def measure(puzzle, encoding):
    start = time.perf_counter()
    solution = solve_sudoku(puzzle, amo_encoding=encoding)
    elapsed = time.perf_counter() - start

    if not is_valid_solution(puzzle, solution):
        raise RuntimeError(
            f"{encoding} returned no solution or an invalid solution."
        )

    return elapsed


def main():
    datasets = load_datasets()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for difficulty, puzzles in datasets.items():
        for index, puzzle in enumerate(puzzles, start=1):
            print(f"\nDataset: {difficulty}, instance #{index}")

            for encoding in ENCODINGS:
                # Warm-up; this run is excluded from the measurements.
                measure(puzzle, encoding)

                times = [
                    measure(puzzle, encoding)
                    for _ in range(RUNS)
                ]

                median_time = statistics.median(times)

                rows.append({
                    "difficulty": difficulty,
                    "instance": index,
                    "encoding": encoding,
                    "runs": RUNS,
                    "median_time_seconds": median_time,
                })

                print(
                    f"  {encoding:10} | "
                    f"median = {median_time:.6f} s"
                )

    fieldnames = [
        "difficulty",
        "instance",
        "encoding",
        "runs",
        "median_time_seconds",
    ]

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nBenchmark completed: {len(rows)} measurements.")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
