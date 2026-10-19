import pytest

from src.sudoku_gurobi import solve_sudoku


STANDARD_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def is_valid_solution(grid, solution):
    if len(solution) != 9 or any(len(row) != 9 for row in solution):
        return False

    expected = set(range(1, 10))

    if any(set(row) != expected for row in solution):
        return False

    if any(
        {solution[r][c] for r in range(9)} != expected
        for c in range(9)
    ):
        return False

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            box = {
                solution[r][c]
                for r in range(box_r, box_r + 3)
                for c in range(box_c, box_c + 3)
            }
            if box != expected:
                return False

    return all(
        grid[r][c] == 0 or grid[r][c] == solution[r][c]
        for r in range(9)
        for c in range(9)
    )


def test_solves_standard_puzzle():
    solution = solve_sudoku(STANDARD_PUZZLE)

    assert solution is not None
    assert is_valid_solution(STANDARD_PUZZLE, solution)


def test_rejects_invalid_grid_size():
    with pytest.raises(ValueError):
        solve_sudoku([[0] * 8 for _ in range(9)])


@pytest.mark.parametrize("value", [-1, 10, 1.5, True])
def test_rejects_invalid_cell_values(value):
    grid = [row[:] for row in STANDARD_PUZZLE]
    grid[0][0] = value

    with pytest.raises(ValueError):
        solve_sudoku(grid)

@pytest.mark.parametrize(
    "grid",
    [
        [],
        [[0] * 8 for _ in range(8)],
        [[0] * 9 for _ in range(8)],
        [[0] * 9 for _ in range(4)],
    ],
)
def test_rejects_invalid_grid_shape(grid):
    with pytest.raises(ValueError):
        solve_sudoku(grid)


def test_returns_none_for_contradictory_puzzle():
    grid = [row[:] for row in STANDARD_PUZZLE]
    grid[0][2] = 5

    assert solve_sudoku(grid) is None