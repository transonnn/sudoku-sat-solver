import json
from pathlib import Path

from src.sudoku_sat import encode_sudoku, solve_sudoku


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "sudoku_instances.json"


def valid_solution(
    puzzle: list[list[int]],
    solution: list[list[int]] | None,
) -> bool:
    if solution is None or len(solution) != 9:
        return False

    expected = set(range(1, 10))

    for r in range(9):
        if len(solution[r]) != 9:
            return False

        if set(solution[r]) != expected:
            return False

    for c in range(9):
        if {solution[r][c] for r in range(9)} != expected:
            return False

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            values = {
                solution[r][c]
                for r in range(box_r, box_r + 3)
                for c in range(box_c, box_c + 3)
            }
            if values != expected:
                return False

    for r in range(9):
        for c in range(9):
            if puzzle[r][c] != 0 and puzzle[r][c] != solution[r][c]:
                return False

    return True


def main() -> None:
    with DATASET_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    puzzle = data["easy"][0]

    for encoding in ("pairwise", "seqcounter"):
        clauses = encode_sudoku(puzzle, amo_encoding=encoding)
        solution = solve_sudoku(puzzle, amo_encoding=encoding)

        max_variable = max(
            abs(literal)
            for clause in clauses
            for literal in clause
        )

        print(
            f"{encoding}: clauses={len(clauses)}, "
            f"max_variable_id={max_variable}, "
            f"valid_solution={valid_solution(puzzle, solution)}"
        )


if __name__ == "__main__":
    main()
