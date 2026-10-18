import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "data" / "sudoku_instances.json"

COUNT_PER_LEVEL = 10
SEED = 2026

# Số ô bị xóa để tạo câu đố.
# Đây là mức phân nhóm theo số ô trống, không bảo đảm độ khó giải thực tế.
EMPTY_CELLS = {
    "easy": (30, 35),
    "medium": (40, 48),
    "hard": (50, 55),
}


def generate_solution(rng):
    """Generate a complete valid Sudoku grid."""
    digits = list(range(1, 10))
    rng.shuffle(digits)

    def pattern(r, c):
        return (3 * (r % 3) + r // 3 + c) % 9

    rows = list(range(9))
    cols = list(range(9))

    # Shuffle rows within each band and shuffle the bands.
    row_order = []
    bands = [0, 1, 2]
    rng.shuffle(bands)
    for band in bands:
        within = [0, 1, 2]
        rng.shuffle(within)
        row_order.extend(3 * band + r for r in within)

    # Shuffle columns within each stack and shuffle the stacks.
    col_order = []
    stacks = [0, 1, 2]
    rng.shuffle(stacks)
    for stack in stacks:
        within = [0, 1, 2]
        rng.shuffle(within)
        col_order.extend(3 * stack + c for c in within)

    return [
        [digits[pattern(row_order[r], col_order[c])] for c in range(9)]
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


def main():
    rng = random.Random(SEED)
    datasets = {}

    for difficulty, (min_empty, max_empty) in EMPTY_CELLS.items():
        puzzles = []

        for _ in range(COUNT_PER_LEVEL):
            solution = generate_solution(rng)

            if not is_valid_complete_grid(solution):
                raise RuntimeError("Generated an invalid complete Sudoku.")

            empty_count = rng.randint(min_empty, max_empty)
            puzzle = make_puzzle(solution, empty_count, rng)
            puzzles.append(puzzle)

        datasets[difficulty] = puzzles
        print(f"{difficulty}: generated {len(puzzles)} puzzles")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(datasets, file, indent=2)

    print(f"\nSaved {sum(map(len, datasets.values()))} puzzles to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
