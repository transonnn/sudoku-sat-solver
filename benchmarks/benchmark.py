
import csv
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sudoku_sat import solve_sudoku as solve_sat
from src.sudoku_cpsat import solve_sudoku as solve_cpsat

DATA_FILE = ROOT / "data" / "sudoku_instances.json"
RESULTS_DIR = ROOT / "results"
OUTPUT_FILE = RESULTS_DIR / "benchmark_sat_cpsat.csv"

RUNS = 5

SOLVERS = [
    ("SAT", solve_sat),
    ("CP-SAT", solve_cpsat),
]


def load_datasets():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        datasets = json.load(file)

    if not isinstance(datasets, dict) or not datasets:
        raise ValueError("Dataset must be a non-empty JSON object.")

    for difficulty, puzzles in datasets.items():
        if not isinstance(puzzles, list) or not puzzles:
            raise ValueError(
                f"Dataset '{difficulty}' must be a non-empty list."
            )

        for index, grid in enumerate(puzzles, start=1):
            if (
                not isinstance(grid, list)
                or len(grid) != 9
                or any(
                    not isinstance(row, list) or len(row) != 9
                    for row in grid
                )
            ):
                raise ValueError(
                    f"{difficulty} instance {index} must be a 9x9 grid."
                )

            for row in grid:
                for value in row:
                    if type(value) is not int or not 0 <= value <= 9:
                        raise ValueError(
                            f"{difficulty} instance {index} "
                            "contains an invalid cell value."
                        )

    return datasets


def is_valid_solution(puzzle, solution):
    if (
        solution is None
        or len(solution) != 9
        or any(len(row) != 9 for row in solution)
    ):
        return False

    required = set(range(1, 10))

    for i in range(9):
        if set(solution[i]) != required:
            return False

        if {solution[r][i] for r in range(9)} != required:
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = {
                solution[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            }
            if values != required:
                return False

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0 and solution[r][c] != puzzle[r][c]:
                return False

    return True


def measure(solver, puzzle):
    start = time.perf_counter()
    solution = solver(puzzle)
    elapsed = time.perf_counter() - start

    if not is_valid_solution(puzzle, solution):
        raise RuntimeError(
            "Solver returned no solution or an invalid solution."
        )

    return elapsed


def main():
    datasets = load_datasets()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = []

    for difficulty, puzzles in datasets.items():
        for index, puzzle in enumerate(puzzles, start=1):
            print(f"\nDataset: {difficulty}, instance #{index}")

            for solver_name, solver in SOLVERS:
                # Warm-up is not included in the recorded measurements.
                measure(solver, puzzle)

                times = [
                    measure(solver, puzzle)
                    for _ in range(RUNS)
                ]

                median_time = statistics.median(times)

                rows.append({
                    "difficulty": difficulty,
                    "instance": index,
                    "solver": solver_name,
                    "runs": RUNS,
                    "median_time_seconds": median_time,
                })

                print(
                    f"  {solver_name:6} | "
                    f"median = {median_time:.6f} s"
                )

    fieldnames = [
        "difficulty",
        "instance",
        "solver",
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
