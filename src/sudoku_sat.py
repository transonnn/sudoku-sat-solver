from pysat.solvers import Solver
from pysat.card import CardEnc, EncType


AMO_ENCODINGS = {
    "pairwise": EncType.pairwise,
    "seqcounter": EncType.seqcounter,
}


def var_id(row: int, col: int, digit: int, n: int = 9) -> int:
    """Map (row, col, digit) to a positive SAT variable."""
    return row * n * n + col * n + digit


def encode_sudoku(
    grid: list[list[int]],
    amo_encoding: str = "pairwise",
) -> list[list[int]]:
    """Encode a standard 9x9 Sudoku as CNF clauses."""
    n = 9

    if len(grid) != n or any(len(row) != n for row in grid):
        raise ValueError("Sudoku grid must be 9x9.")

    if any(
        not isinstance(value, int) or value < 0 or value > 9
        for row in grid
        for value in row
    ):
        raise ValueError("Each cell must be an integer from 0 to 9.")

    if amo_encoding not in AMO_ENCODINGS:
        raise ValueError(
            f"Unknown AMO encoding: {amo_encoding}. "
            f"Choose from {list(AMO_ENCODINGS)}."
        )

    clauses: list[list[int]] = []
    top_id = n * n * n

    def add_exactly_one(variables: list[int]) -> None:
        nonlocal top_id

        # At least one variable must be true.
        clauses.append(variables)

        # At most one variable may be true.
        encoding = AMO_ENCODINGS[amo_encoding]
        result = CardEnc.atmost(
            lits=variables,
            bound=1,
            encoding=encoding,
            top_id=top_id,
        )
        clauses.extend(result.clauses)
        top_id = result.nv

    # Every cell contains exactly one digit.
    for r in range(n):
        for c in range(n):
            add_exactly_one([var_id(r, c, d) for d in range(1, n + 1)])

    # Each digit appears exactly once in every row.
    for r in range(n):
        for d in range(1, n + 1):
            add_exactly_one([var_id(r, c, d) for c in range(n)])

    # Each digit appears exactly once in every column.
    for c in range(n):
        for d in range(1, n + 1):
            add_exactly_one([var_id(r, c, d) for r in range(n)])

    # Each digit appears exactly once in every 3x3 box.
    for box_r in range(0, n, 3):
        for box_c in range(0, n, 3):
            for d in range(1, n + 1):
                cells = [
                    var_id(r, c, d)
                    for r in range(box_r, box_r + 3)
                    for c in range(box_c, box_c + 3)
                ]
                add_exactly_one(cells)

    # Encode the given clues.
    for r in range(n):
        for c in range(n):
            digit = grid[r][c]
            if digit != 0:
                clauses.append([var_id(r, c, digit)])

    return clauses


def solve_sudoku(
    grid: list[list[int]],
    amo_encoding: str = "pairwise",
) -> list[list[int]] | None:
    """Return a solved Sudoku grid, or None if it is unsatisfiable."""
    clauses = encode_sudoku(grid, amo_encoding)

    with Solver(name="g3", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return None

        model = set(lit for lit in solver.get_model() if lit > 0)

    solution = [[0] * 9 for _ in range(9)]

    for r in range(9):
        for c in range(9):
            for d in range(1, 10):
                if var_id(r, c, d) in model:
                    solution[r][c] = d
                    break

    return solution
