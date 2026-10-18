from ortools.sat.python import cp_model


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """Solve a 9x9 Sudoku using Google OR-Tools CP-SAT."""
    n = 9

    if len(grid) != n or any(len(row) != n for row in grid):
        raise ValueError("Sudoku grid must be 9x9.")

    if any(
        not isinstance(value, int) or isinstance(value, bool)
        or value < 0 or value > 9
        for row in grid for value in row
    ):
        raise ValueError("Each cell must be an integer from 0 to 9.")

    model = cp_model.CpModel()

    cells = [
        [model.new_int_var(1, 9, f"x_{r}_{c}") for c in range(n)]
        for r in range(n)
    ]

    # Every row contains distinct digits.
    for r in range(n):
        model.add_all_different(cells[r])

    # Every column contains distinct digits.
    for c in range(n):
        model.add_all_different([cells[r][c] for r in range(n)])

    # Every 3x3 box contains distinct digits.
    for box_r in range(0, n, 3):
        for box_c in range(0, n, 3):
            model.add_all_different([
                cells[r][c]
                for r in range(box_r, box_r + 3)
                for c in range(box_c, box_c + 3)
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
