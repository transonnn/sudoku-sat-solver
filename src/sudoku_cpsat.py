from math import isqrt

from ortools.sat.python import cp_model


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """Solve a standard Sudoku of size n x n."""
    n = len(grid)

    if n == 0 or any(len(row) != n for row in grid):
        raise ValueError("Sudoku grid must be a non-empty square.")

    box_size = isqrt(n)
    if box_size * box_size != n:
        raise ValueError(
            f"Grid size {n} requires explicit box dimensions; "
            "automatic detection supports perfect-square sizes only."
        )

    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > n
        for row in grid
        for value in row
    ):
        raise ValueError(f"Each cell must be an integer from 0 to {n}.")

    model = cp_model.CpModel()

    cells = [
        [
            model.new_int_var(1, n, f"x_{r}_{c}")
            for c in range(n)
        ]
        for r in range(n)
    ]

    # Every row contains distinct digits.
    for r in range(n):
        model.add_all_different(cells[r])

    # Every column contains distinct digits.
    for c in range(n):
        model.add_all_different([cells[r][c] for r in range(n)])

    # Every box contains distinct digits.
    for box_r in range(0, n, box_size):
        for box_c in range(0, n, box_size):
            model.add_all_different([
                cells[r][c]
                for r in range(box_r, box_r + box_size)
                for c in range(box_c, box_c + box_size)
            ])

    # Preserve the given clues.
    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                model.add(cells[r][c] == grid[r][c])

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None

    return [
        [solver.value(cells[r][c]) for c in range(n)]
        for r in range(n)
    ]
