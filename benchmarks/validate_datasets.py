import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.sudoku_sat import solve_sudoku as solve_sat
from src.sudoku_cpsat import solve_sudoku as solve_cpsat

DATA_FILE = ROOT / "data" / "sudoku_instances.json"


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

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            box = {
                solution[r][c]
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            }
            if box != required:
                return False

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0 and solution[r][c] != puzzle[r][c]:
                return False

    return True


def main():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        datasets = json.load(file)

    total = 0
    errors = []

    for difficulty, puzzles in datasets.items():
        for index, puzzle in enumerate(puzzles, start=1):
            total += 1

            for name, solver in [
                ("SAT", solve_sat),
                ("CP-SAT", solve_cpsat),
            ]:
                try:
                    solution = solver(puzzle)
                    valid = is_valid_solution(puzzle, solution)
                except Exception as exc:
                    valid = False
                    print(
                        f"ERROR: {difficulty} #{index}, "
                        f"{name}: {exc}"
                    )

                if not valid:
                    errors.append((difficulty, index, name))
                    print(
                        f"FAIL: {difficulty} #{index}, {name}"
                    )

        print(f"Checked group: {difficulty}")

    print(f"\nTotal puzzles: {total}")
    print(f"Failed solver checks: {len(errors)}")

    if errors:
        raise SystemExit("Validation failed. Do not benchmark yet.")

    print("All puzzles passed SAT and CP-SAT solution checks.")


if __name__ == "__main__":
    main()
