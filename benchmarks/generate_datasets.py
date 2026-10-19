import json
import random
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "data" / "sudoku_instances.json"

COUNT_PER_LEVEL = 10
SEED = 2026
MAX_ATTEMPTS_PER_LEVEL = 5000

EMPTY_CELLS = {
    "easy": (30, 35),
    "medium": (40, 48),
    "hard": (50, 55),
}


def var_id(row, col, digit):
    return row * 81 + col * 9 + digit


def generate_solution(rng):
    """Generate a complete valid Sudoku grid."""
    digits = list(range(1, 10))
    rng.shuffle(digits)

    def pattern(r, c):
        return (3 * (r % 3) + r // 3 + c) % 9

    rows = list(range(9))
    cols = list(range(9))

    row_order = []
    bands = [0, 1, 2]
    rng.shuffle(bands)
    for band in bands:
        within = [0, 1, 2]
        rng.shuffle(within)
        row_order.extend(3 * band + r for r in within)

    col_order = []
    stacks = [0, 1, 2]
    rng.shuffle(stacks)
    for stack in stacks:
        within = [0, 1, 2]
        rng.shuffle(within)
        col_order.extend(3 * stack + c for c in within)

    return [
        [digits[pattern(row_order[r], col_order[c])] for c in cols]
        for r in rows
    ]


def make_puzzle(solution, empty_count, rng):
    """Remove cells from a solved grid."""
    puzzle = [row[:] for row in solution]
    positions = [(r, c) for r in range(9) for c in range(9)]
    rng.shuffle(positions)

    for r, c in positions[:empty_count]:
        puzzle[r][c] = 0

    return puzzle


def is_valid_complete_grid(grid):
    """Check rows, columns, and 3x3 boxes of a complete Sudoku."""
    required = set(range(1, 10))

    if len(grid) != 9 or any(len(row) != 9 for row in grid):
        return False

    if any(
        type(value) is not int or not 1 <= value <= 9
        for row in grid
        for value in row
    ):
        return False

    for i in range(9):
        if set(grid[i]) != required:
            return False

        if {grid[r][i] for r in range(9)} != required:
            return False

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            values = {
                grid[r][c]
                for r in range(box_r, box_r + 3)
                for c in range(box_c, box_c + 3)
            }
            if values != required:
                return False

    return True


def encode_sudoku(puzzle):
    """Encode Sudoku constraints as CNF clauses."""
    clauses = []

    def cell_vars(r, c):
        return [var_id(r, c, d) for d in range(1, 10)]

    # Each cell contains at least one digit.
    for r in range(9):
        for c in range(9):
            clauses.append(cell_vars(r, c))

    # Each cell contains at most one digit.
    for r in range(9):
        for c in range(9):
            vs = cell_vars(r, c)
            for i in range(9):
                for j in range(i + 1, 9):
                    clauses.append([-vs[i], -vs[j]])

    # Each digit appears exactly once in every row and column.
    for d in range(1, 10):
        for i in range(9):
            row_vars = [var_id(i, c, d) for c in range(9)]
            col_vars = [var_id(r, i, d) for r in range(9)]

            clauses.append(row_vars)
            clauses.append(col_vars)

            for a in range(9):
                for b in range(a + 1, 9):
                    clauses.append([-row_vars[a], -row_vars[b]])
                    clauses.append([-col_vars[a], -col_vars[b]])

    # Each digit appears exactly once in every 3x3 box.
    for d in range(1, 10):
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                vs = [
                    var_id(r, c, d)
                    for r in range(br, br + 3)
                    for c in range(bc, bc + 3)
                ]
                clauses.append(vs)

                for i in range(9):
                    for j in range(i + 1, 9):
                        clauses.append([-vs[i], -vs[j]])

    # Preserve the original clues.
    for r in range(9):
        for c in range(9):
            d = puzzle[r][c]
            if d != 0:
                clauses.append([var_id(r, c, d)])

    return clauses


def has_unique_solution(puzzle):
    """Return True only if the puzzle has exactly one solution."""
    clauses = encode_sudoku(puzzle)

    with Solver(name="g3", bootstrap_with=clauses) as solver:
        if not solver.solve():
            return False

        model = solver.get_model()
        blocking_clause = []

        # Block the complete assignment found by the solver.
        model_set = set(model)
        for r in range(9):
            for c in range(9):
                for d in range(1, 10):
                    v = var_id(r, c, d)
                    if v in model_set:
                        blocking_clause.append(-v)
                        break

        solver.add_clause(blocking_clause)

        # A second solution means the puzzle is not unique.
        return not solver.solve()


def main():
    rng = random.Random(SEED)
    datasets = {}

    for difficulty, (min_empty, max_empty) in EMPTY_CELLS.items():
        puzzles = []
        attempts = 0

        while len(puzzles) < COUNT_PER_LEVEL:
            attempts += 1

            if attempts > MAX_ATTEMPTS_PER_LEVEL:
                raise RuntimeError(
                    f"Could not generate {COUNT_PER_LEVEL} unique "
                    f"{difficulty} puzzles within "
                    f"{MAX_ATTEMPTS_PER_LEVEL} attempts."
                )

            solution = generate_solution(rng)

            if not is_valid_complete_grid(solution):
                raise RuntimeError(
                    "Generated an invalid complete Sudoku."
                )

            empty_count = rng.randint(min_empty, max_empty)
            puzzle = make_puzzle(solution, empty_count, rng)

            if has_unique_solution(puzzle):
                puzzles.append(puzzle)
                print(
                    f"{difficulty}: accepted "
                    f"{len(puzzles)}/{COUNT_PER_LEVEL} "
                    f"(attempt {attempts}, empty cells {empty_count})"
                )

        datasets[difficulty] = puzzles

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(datasets, file, indent=2)

    print(f"\nSaved {sum(map(len, datasets.values()))} puzzles to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
