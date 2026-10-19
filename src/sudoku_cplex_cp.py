from math import isqrt

from docplex.cp.model import CpoModel


def solve_sudoku(
    grid: list[list[int]],
    time_limit: int = 60,
) -> list[list[int]] | None:
    """Solve a square-box Sudoku using IBM ILOG CP Optimizer."""
    n = len(grid)
    box = isqrt(n)

    if n == 0 or box * box != n:
        raise ValueError("Sudoku size must be a perfect square.")

    if any(len(row) != n for row in grid):
        raise ValueError(f"Sudoku grid must be {n}x{n}.")

    if any(
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > n
        for row in grid
        for value in row
    ):
        raise ValueError(f"Each cell must be an integer from 0 to {n}.")

    model = CpoModel(name=f"Sudoku_CP_{n}")

    cells = [
        [
            model.integer_var(min=1, max=n, name=f"x_{r}_{c}")
            for c in range(n)
        ]
        for r in range(n)
    ]

    for r in range(n):
        model.add(model.all_diff(cells[r]))

    for c in range(n):
        model.add(model.all_diff([cells[r][c] for r in range(n)]))

    for box_r in range(0, n, box):
        for box_c in range(0, n, box):
            model.add(
                model.all_diff([
                    cells[r][c]
                    for r in range(box_r, box_r + box)
                    for c in range(box_c, box_c + box)
                ])
            )

    for r in range(n):
        for c in range(n):
            if grid[r][c] != 0:
                model.add(cells[r][c] == grid[r][c])

    solution = model.solve(
        TimeLimit=time_limit,
        LogVerbosity="Quiet",
    )

    if solution is None or not solution.is_solution():
        return None

    return [
        [solution.get_value(cells[r][c]) for c in range(n)]
        for r in range(n)
    ]
