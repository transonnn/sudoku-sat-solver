from pathlib import Path
from time import perf_counter

from src.scaled_sudoku import load_scaled_sudoku
from src.sudoku_sat import solve_sudoku as solve_sat
from src.sudoku_cpsat import solve_sudoku as solve_cpsat


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
    root = Path("data/scaled-sudoku-sample/25x25")
    puzzle_path = next(root.rglob("*.sdk.txt"))
    puzzle = load_scaled_sudoku(puzzle_path)

    print(f"Puzzle: {puzzle_path}")
    print(f"Size: {len(puzzle)}x{len(puzzle)}")

    for name, solve in [
        ("SAT", solve_sat),
        ("CP-SAT", solve_cpsat),
    ]:
        start = perf_counter()
        solution = solve(puzzle)
        elapsed = perf_counter() - start

        valid = (
            solution is not None
            and validate_solution(puzzle, solution)
        )

        print(
            f"{name}: "
            f"{'SOLVED' if valid else 'FAILED'}, "
            f"time={elapsed:.3f}s"
        )

        if solution is not None and not valid:
            print(f"WARNING: {name} returned an invalid solution")


if __name__ == "__main__":
    main()
