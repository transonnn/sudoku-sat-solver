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
## Implemented Solvers

- **SAT:** Sudoku encoded as a Boolean satisfiability problem.
- **CP-SAT:** Sudoku modeled using Google OR-Tools.
- **CPLEX MIP:** Sudoku modeled as a binary mixed-integer optimization problem using IBM CPLEX.

## Running Tests

Run from the project root:

```bash
python -m pytest -v
```

## Running the Three-Solver Benchmark

Run from the project root:

```bash
python -m benchmarks.benchmark
```

The benchmark compares SAT, CP-SAT, and CPLEX using the Sudoku instances in `data/sudoku_instances.json`. Each instance is warmed up once and measured five times. The median time is recorded.

Output: `results/benchmark_sat_cpsat_cplex.csv`

## Generating the Comparison Chart

Run:

```bash
python -m benchmarks.plot_results
```

Output: `results/sat_vs_cpsat_cplex.png`

The chart compares the mean of the per-instance median solving times for each solver, grouped by difficulty.

## Experimental Integrity

Benchmark results depend on the hardware, solver configuration, and model-building overhead. Record the environment and solver versions when reporting results.