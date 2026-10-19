import json
import sys
from pathlib import Path

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "sudoku_instances.json"


def var_id(row, col, digit):
    return row * 81 + col * 9 + digit


def encode_sudoku(puzzle):
    clauses = []

    def cell_vars(r, c):
        return [var_id(r, c, d) for d in range(1, 10)]

    # Mỗi ô có ít nhất một chữ số.
    for r in range(9):
        for c in range(9):
            clauses.append(cell_vars(r, c))

    # Mỗi ô có nhiều nhất một chữ số.
    for r in range(9):
        for c in range(9):
            vs = cell_vars(r, c)
            for i in range(9):
                for j in range(i + 1, 9):
                    clauses.append([-vs[i], -vs[j]])

    # Mỗi hàng và mỗi cột chứa từng chữ số đúng một lần.
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

    # Mỗi khối 3x3 chứa từng chữ số đúng một lần.
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

    # Giữ nguyên dữ kiện ban đầu.
    for r in range(9):
        for c in range(9):
            d = puzzle[r][c]
            if d != 0:
                clauses.append([var_id(r, c, d)])

    return clauses


def count_solutions_up_to_two(puzzle):
    clauses = encode_sudoku(puzzle)
    count = 0

    with Solver(name="g3", bootstrap_with=clauses) as solver:
        while solver.solve():
            count += 1

            # Chặn chính xác nghiệm vừa tìm được.
            model = solver.get_model()
            blocking_clause = []

            for r in range(9):
                for c in range(9):
                    for d in range(1, 10):
                        v = var_id(r, c, d)
                        if v in model:
                            blocking_clause.append(-v)
                            break

            solver.add_clause(blocking_clause)

            if count == 2:
                return 2

    return count


def main():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        datasets = json.load(f)

    total = 0
    unique = 0
    multiple = 0
    unsat = 0

    for difficulty, puzzles in datasets.items():
        for index, puzzle in enumerate(puzzles, start=1):
            total += 1
            count = count_solutions_up_to_two(puzzle)

            if count == 1:
                unique += 1
                status = "UNIQUE"
            elif count == 2:
                multiple += 1
                status = "MULTIPLE (at least 2)"
            else:
                unsat += 1
                status = "UNSAT"

            print(f"{difficulty} #{index:02}: {status}")

    print("\nSummary")
    print(f"Total puzzles: {total}")
    print(f"Unique solutions: {unique}")
    print(f"Multiple solutions: {multiple}")
    print(f"No solutions: {unsat}")

    if unique != total:
        sys.exit("Some puzzles do not have exactly one solution.")


if __name__ == "__main__":
    main()
