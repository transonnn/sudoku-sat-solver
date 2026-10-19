from pathlib import Path


SYMBOLS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def load_scaled_sudoku(path: str | Path) -> list[list[int]]:
    """Load a scaled Sudoku puzzle from an .sdk.txt file."""
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()

    size = None
    rows = []

    for line in lines:
        line = line.strip().upper()

        if not line or line.startswith("#"):
            if line.startswith("#") and "SIZE=" in line:
                header = line.split()
                for item in header:
                    if item.startswith("SIZE="):
                        size = int(item.split("=", 1)[1])
            continue

        rows.append(line)

    if size is None:
        raise ValueError(f"Missing size header in {path}")

    if len(rows) != size or any(len(row) != size for row in rows):
        raise ValueError(f"Expected {size} rows of {size} cells in {path}")

    grid = []

    for row in rows:
        values = []
        for char in row:
            if char == ".":
                values.append(0)
            elif char in SYMBOLS[1:]:
                values.append(SYMBOLS.index(char))
            else:
                raise ValueError(f"Invalid Sudoku symbol {char!r} in {path}")
        grid.append(values)

    if any(value > size for row in grid for value in row):
        raise ValueError(f"Symbol exceeds Sudoku size {size} in {path}")

    return grid
