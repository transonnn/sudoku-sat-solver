import cplex


def solve_sudoku(grid: list[list[int]]) -> list[list[int]] | None:
    """Solve a 9x9 Sudoku using IBM ILOG CPLEX as a binary MIP model."""
    n = 9

    if len(grid) != n or any(len(row) != n for row in grid):
        raise ValueError("Sudoku grid must be 9x9.")

    if any(
        not isinstance(value, int) or isinstance(value, bool)
        or value < 0 or value > 9
        for row in grid
        for value in row
    ):
        raise ValueError("Each cell must be an integer from 0 to 9.")

    model = cplex.Cplex()
    model.set_log_stream(None)
    model.set_error_stream(None)
    model.set_warning_stream(None)
    model.set_results_stream(None)
    model.objective.set_sense(model.objective.sense.minimize)

    def var_name(r: int, c: int, d: int) -> str:
        return f"x_{r}_{c}_{d}"

    names = [
        var_name(r, c, d)
        for r in range(n)
        for c in range(n)
        for d in range(1, n + 1)
    ]

    model.variables.add(
        obj=[0.0] * len(names),
        lb=[0.0] * len(names),
        ub=[1.0] * len(names),
        types=[model.variables.type.binary] * len(names),
        names=names,
    )

    constraint_names = []
    linear_expressions = []
    senses = []
    rhs = []

    def add_exactly_one(variables: list[str]) -> None:
        constraint_names.append(f"constraint_{len(constraint_names)}")
        linear_expressions.append(cplex.SparsePair(
            ind=variables,
            val=[1.0] * len(variables),
        ))
        senses.append("E")
        rhs.append(1.0)

    # Each cell contains exactly one digit.
    for r in range(n):
        for c in range(n):
            add_exactly_one([var_name(r, c, d) for d in range(1, n + 1)])

    # Each digit appears exactly once in every row.
    for r in range(n):
        for d in range(1, n + 1):
            add_exactly_one([var_name(r, c, d) for c in range(n)])

    # Each digit appears exactly once in every column.
    for c in range(n):
        for d in range(1, n + 1):
            add_exactly_one([var_name(r, c, d) for r in range(n)])

    # Each digit appears exactly once in every 3x3 box.
    for box_r in range(0, n, 3):
        for box_c in range(0, n, 3):
            for d in range(1, n + 1):
                add_exactly_one([
                    var_name(r, c, d)
                    for r in range(box_r, box_r + 3)
                    for c in range(box_c, box_c + 3)
                ])

    # Preserve the given clues.
    for r in range(n):
        for c in range(n):
            digit = grid[r][c]
            if digit != 0:
                add_exactly_one([var_name(r, c, digit)])

    try:
        model.linear_constraints.add(
            lin_expr=linear_expressions,
            senses="".join(senses),
            rhs=rhs,
            names=constraint_names,
        )

        model.solve()

        if not model.solution.is_primal_feasible():
            return None

        solution = [[0] * n for _ in range(n)]
        values = model.solution.get_values()

        for r in range(n):
            for c in range(n):
                for d in range(1, n + 1):
                    index = ((r * n + c) * n) + (d - 1)
                    if values[index] > 0.5:
                        solution[r][c] = d
                        break

        return solution
    finally:
        model.end()
