from src.sudoku_cpsat import solve_sudoku


PUZZLE = [
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


def is_valid_solution(grid):
    target = set(range(1, 10))

    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False

    if any(set(row) != target for row in grid):
        return False

    for c in range(9):
        if {grid[r][c] for r in range(9)} != target:
            return False

    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            values = {
                grid[r][c]
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            }
            if values != target:
                return False

    return True


def test_solves_standard_puzzle():
    solution = solve_sudoku(PUZZLE)

    assert solution is not None
    assert is_valid_solution(solution)

    for r in range(9):
        for c in range(9):
            if PUZZLE[r][c] != 0:
                assert solution[r][c] == PUZZLE[r][c]


def test_rejects_invalid_grid_shape():
    try:
        solve_sudoku([[0] * 8 for _ in range(9)])
    except ValueError:
        return

    raise AssertionError("Expected ValueError for an invalid grid shape.")
