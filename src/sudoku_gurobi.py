from math import isqrt

import gurobipy as gp
from gurobipy import GRB


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """Solve a square-box Sudoku using Gurobi as a binary MIP model."""
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

    model = gp.Model(f"sudoku_{n}")
    model.Params.OutputFlag = 0

    try:
        x = model.addVars(
            n, n, range(1, n + 1),
            vtype=GRB.BINARY,
            name="x",
        )

        # Each cell contains exactly one digit.
        for r in range(n):
            for c in range(n):
                model.addConstr(
                    gp.quicksum(x[r, c, d] for d in range(1, n + 1)) == 1
                )

        # Each digit appears exactly once in every row.
        for r in range(n):
            for d in range(1, n + 1):
                model.addConstr(
                    gp.quicksum(x[r, c, d] for c in range(n)) == 1
                )

        # Each digit appears exactly once in every column.
        for c in range(n):
            for d in range(1, n + 1):
                model.addConstr(
                    gp.quicksum(x[r, c, d] for r in range(n)) == 1
                )

        # Each digit appears exactly once in every box.
        for box_r in range(0, n, box):
            for box_c in range(0, n, box):
                for d in range(1, n + 1):
                    model.addConstr(
                        gp.quicksum(
                            x[r, c, d]
                            for r in range(box_r, box_r + box)
                            for c in range(box_c, box_c + box)
                        ) == 1
                    )

        # Preserve the given clues.
        for r in range(n):
            for c in range(n):
                digit = grid[r][c]
                if digit != 0:
                    model.addConstr(x[r, c, digit] == 1)

        model.optimize()

        if model.Status != GRB.OPTIMAL:
            return None

        return [
            [
                next(
                    d for d in range(1, n + 1)
                    if x[r, c, d].X > 0.5
                )
                for c in range(n)
            ]
            for r in range(n)
        ]
    finally:
        model.dispose()
