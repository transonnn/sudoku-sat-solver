import csv
from pathlib import Path
from time import perf_counter

from src.scaled_sudoku import load_scaled_sudoku
from src.sudoku_sat import solve_sudoku as solve_sat
from src.sudoku_cpsat import solve_sudoku as solve_cpsat


DATA_ROOT = Path("data/scaled-sudoku-sample")
OUTPUT_PATH = Path("results/benchmark_scaled_solvers.csv")
PUZZLES_PER_SIZE = 10


def validate_solution(
    puzzle: list[list[int]],
    solution: list[list[int]],
) -> bool:
    n = len(puzzle)
    box = int(n**0.5)
    expected = set(range(1, n + 1))

    if len(solution) != n or any(len(row) != n for row in solution):
        return False

    if any(set(row) != expected for row in solution):
        return False

    if any(
        {solution[r][c] for r in range(n)} != expected
        for c in range(n)
    ):
        return False

    for br in range(0, n, box):
        for bc in range(0, n, box):
            values = {
                solution[r][c]
                for r in range(br, br + box)
                for c in range(bc, bc + box)
            }
            if values != expected:
                return False

    for r in range(n):
        for c in range(n):
            if puzzle[r][c] and puzzle[r][c] != solution[r][c]:
                return False

    return True


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    results = []

    for size in (16, 25):
        root = DATA_ROOT / f"{size}x{size}"
        puzzle_paths = sorted(root.rglob("*.sdk.txt"))[
            :PUZZLES_PER_SIZE
        ]

        if not puzzle_paths:
            print(f"WARNING: No puzzles found for size {size}x{size}")
            continue

        print(f"\n{'=' * 55}")
        print(f"Sudoku {size}x{size}: {len(puzzle_paths)} puzzles")
        print(f"{'=' * 55}")

        for index, puzzle_path in enumerate(puzzle_paths, start=1):
            puzzle = load_scaled_sudoku(puzzle_path)
            print(f"\n[{index}/{len(puzzle_paths)}] {puzzle_path.name}")

            for name, solve in (
                ("SAT", solve_sat),
                ("CP-SAT", solve_cpsat),
            ):
                start = perf_counter()
                error = ""
                solution = None

                try:
                    solution = solve(puzzle)
                    elapsed = perf_counter() - start
                    valid = (
                        solution is not None
                        and validate_solution(puzzle, solution)
                    )
                    status = "SOLVED" if valid else "FAILED"
                except Exception as exc:
                    elapsed = perf_counter() - start
                    valid = False
                    status = "ERROR"
                    error = str(exc)

                row = {
                    "size": size,
                    "puzzle": puzzle_path.name,
                    "solver": name,
                    "status": status,
                    "valid": valid,
                    "time_seconds": round(elapsed, 6),
                    "error": error,
                }
                results.append(row)

                print(
                    f"  {name}: {status}, "
                    f"time={elapsed:.3f}s"
                )
                if error:
                    print(f"    Error: {error}")

    with OUTPUT_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as csvfile:
        fields = [
            "size",
            "puzzle",
            "solver",
            "status",
            "valid",
            "time_seconds",
            "error",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {OUTPUT_PATH}")
    print(f"Total solver runs: {len(results)}")

    print("\nSummary:")
    for size in (16, 25):
        for name in ("SAT", "CP-SAT"):
            rows = [
                row for row in results
                if row["size"] == size and row["solver"] == name
            ]
            successful = [
                row for row in rows if row["status"] == "SOLVED"
            ]
            times = [row["time_seconds"] for row in successful]

            if times:
                print(
                    f"  {size}x{size} {name}: "
                    f"{len(successful)}/{len(rows)} solved, "
                    f"mean={sum(times) / len(times):.3f}s"
                )
            else:
                print(f"  {size}x{size} {name}: 0/{len(rows)} solved")


if __name__ == "__main__":
    main()
