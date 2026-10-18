# Sudoku SAT Solver

A research project comparing SAT-based Sudoku solving with exact optimization methods.

## Project Goals

- Encode Sudoku constraints as a Boolean satisfiability problem (SAT).
- Investigate alternative cardinality encodings.
- Compare SAT with CP-SAT, CPLEX MIP, CPLEX CP, and Gurobi.
- Evaluate solving time and other relevant metrics on Sudoku instances.

## Project Structure

- `src/`: Solver implementations
- `data/`: Sudoku benchmark instances
- `benchmarks/`: Benchmark scripts
- `results/`: Experimental results
- `report/`: Scientific report and figures
- `tests/`: Automated tests

## Requirements

Python 3.13 may not be supported by every solver package. Use a Python version compatible with all required dependencies.

Install dependencies with:

```bash
python -m pip install -r requirements.txt
```

Some solvers may require separate installations or academic licenses.

## Experimental Integrity

Only include benchmark results obtained from actual executions. Document solver versions, hardware, parameters, and timeout settings.

## Data Availability

Repository: https://github.com/transonnn/sudoku-sat-solver
