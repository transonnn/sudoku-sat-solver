from math import isqrt

from pysat.solvers import Solver
from pysat.card import CardEnc, EncType


AMO_ENCODINGS = {
    "pairwise": EncType.pairwise,
    "seqcounter": EncType.seqcounter,
}


def var_id(row: int, col: int, digit: int, n: int = 9) -> int:
    """Map (row, col, digit) to a positive SAT variable."""
    return row * n * n + col * n + digit


def _validate_grid(
    grid: list[list[int]],
) -> tuple[int, int, int]:
    """Validate a Sudoku grid and return (size, box_height, box_width)."""
    n = len(grid)

    if n == 0 or any(len(row) != n for row in grid):
        raise ValueError("Sudoku grid must be a non-empty square.")

    # Standard square boxes: 9x9 -> 3x3, 16x16 -> 4x4, 25x25 -> 5x5.
    box_size = isqrt(n)
    if box_size * box_size != n:
        raise ValueError(
            f"Grid size {n} requires explicit box dimensions; "
            "automatic detection supports perfect-square sizes only."
        )

    if any(
        not isinstance(value, int) or isinstance(value, bool)
        or value < 0 or value > n
        for row in grid
        for value in row
    ):
        raise ValueError(f"Each cell must be an integer from 0 to {n}.")

    return n, box_size, box_size


def encode_sudoku(
    grid: list[list[int]],
    amo_encoding: str = "pairwise",
) -> list[list[int]]:
    """Encode a standard Sudoku of size n x n as CNF clauses."""
    n, box_height, box_width = _validate_grid(grid)

    if amo_encoding not in AMO_ENCODINGS:
        raise ValueError(
            f"Unknown AMO encoding: {amo_encoding}. "
            f"Choose from {list(AMO_ENCODINGS)}."
        )

    clauses: list[list[int]] = []
    top_id = n * n * n

    def add_exactly_one(variables: list[int]) -> None:
        nonlocal top_id

        clauses.append(variables)

        result = CardEnc.atmost(
            lits=variables,
            bound=1,
            encoding=AMO_ENCODINGS[amo_encoding],
            top_id=top_id,
        )
        clauses.extend(result.clauses)
        top_id = result.nv

    # Each cell contains exactly one digit.
    for r in range(n):
        for c in range(n):
            add_exactly_one(
                [var_id(r, c, d, n) for d in range(1, n + 1)]
            )

    # Each digit appears exactly once in every row.
    for r in range(n):
        for d in range(1, n + 1):
            add_exactly_one(
                [var_id(r, c, d, n) for c in range(n)]
            )

    # Each digit appears exactly once in every column.
    for c in range(n):
        for d in range(1, n + 1):
            add_exactly_one(
                [var_id(r, c, d, n) for r in range(n)]
            )

    # Each digit appears exactly once in every box.
    for box_r in range(0, n, box_height):
        for box_c in range(0, n, box_width):
            for d in range(1, n + 1):
                cells = [
                    var_id(r, c, d, n)
                    for r in range(box_r, box_r + box_height)
                    for c in range(box_c, box_c + box_width)
                ]
                add_exactly_one(cells)

    # Encode the given clues.
    for r in range(n):
        for c in range(n):
            digit = grid[r][c]
            if digit != 0:
                clauses.append([var_id(r, c, digit, n)])

    return clauses


def solve_sudoku(
    grid: list[list[int]],
    amo_encoding: str = "pairwise",
) -> list[list[int]] | None:
    """Return a solved Sudoku grid, or None if it is unsatisfiable."""
    n, _, _ = _validate_grid(grid)
    clauses = encode_sudoku(grid, amo_encoding)

    with Solver(name="g3", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None

        model = set(lit for lit in solver.get_model() if lit > 0)

    solution = [[0] * n for _ in range(n)]

    for r in range(n):
        for c in range(n):
            for d in range(1, n + 1):
                if var_id(r, c, d, n) in model:
                    solution[r][c] = d
                    break

    return solution
