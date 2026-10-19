import csv
import json
import statistics
import time
from pathlib import Path

from src.sudoku_sat import solve_sudoku as solve_sat
from src.sudoku_cpsat import solve_sudoku as solve_cpsat
from src.sudoku_cplex import solve_sudoku as solve_cplex
from src.sudoku_cplex_cp import solve_sudoku as solve_cplex_cp
from src.sudoku_gurobi import solve_sudoku as solve_gurobi

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "sudoku_instances.json"
RESULTS_DIR = ROOT / "results"
OUTPUT_FILE = RESULTS_DIR / "benchmark_sat_cpsat_cplex_mip_cplex_cp_gurobi.csv"
RUNS = 5

SOLVERS = [
    ("SAT", solve_sat),
    ("CP-SAT", solve_cpsat),
    ("CPLEX MIP", solve_cplex),
    ("CPLEX CP", solve_cplex_cp),
    ("Gurobi", solve_gurobi),
]


def load_datasets():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        datasets = json.load(file)

    for difficulty, instances in datasets.items():
        for index, grid in enumerate(instances):
            if len(grid) != 9 or any(len(row) != 9 for row in grid):
                raise ValueError(
                    f"Invalid grid size: {difficulty}, instance {index}"
                )
            if any(
                not isinstance(value, int) or isinstance(value, bool)
                or value < 0 or value > 9
                for row in grid
                for value in row
            ):
                raise ValueError(
                    f"Invalid cell value: {difficulty}, instance {index}"
                )

    return datasets


def is_valid_solution(original, solution):
    if solution is None or len(solution) != 9:
        return False

    if any(len(row) != 9 for row in solution):
        return False

    expected = set(range(1, 10))

    for row in solution:
        if set(row) != expected:
            return False

    for col in range(9):
        if {solution[row][col] for row in range(9)} != expected:
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = {
                solution[row][col]
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            }
            if box != expected:
                return False

    for row in range(9):
        for col in range(9):
            if original[row][col] != 0 and (
                solution[row][col] != original[row][col]
            ):
                return False

    return True


def measure(solver, grid):
    start = time.perf_counter()
    solution = solver(grid)
    elapsed = time.perf_counter() - start

    if not is_valid_solution(grid, solution):
        raise RuntimeError(
            f"{solver.__module__ if hasattr(solver, '__module__') else solver} "
            "returned an invalid Sudoku solution"
        )

    return elapsed


def main():
    datasets = load_datasets()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for difficulty, instances in datasets.items():
        for index, grid in enumerate(instances):
            for solver_name, solver in SOLVERS:
                # Warm-up run; validate the solution but exclude its time.
                measure(solver, grid)

                times = [
                    measure(solver, grid)
                    for _ in range(RUNS)
                ]
                median_time = statistics.median(times)

                results.append({
                    "difficulty": difficulty,
                    "instance": index + 1,
                    "solver": solver_name,
                    "runs": RUNS,
                    "median_time_seconds": median_time,
                })

                print(
                    f"{difficulty:>6} | Instance {index + 1:>2} | "
                    f"{solver_name:>6} | Median: {median_time:.6f}s"
                )

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "difficulty",
                "instance",
                "solver",
                "runs",
                "median_time_seconds",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
