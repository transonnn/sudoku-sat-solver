# Sudoku SAT Solver

A research project comparing SAT-based Sudoku solving with constraint programming and mathematical optimization methods.

## Project Goals

- Encode Sudoku constraints as a Boolean satisfiability problem (SAT).
- Explore alternative cardinality encodings.
- Compare SAT, CP-SAT, CPLEX MIP, and Gurobi MIP formulations.
- Evaluate solving time on Sudoku instances of different difficulty levels.

## Project Structure

- `src/`: Solver implementations
- `data/`: Sudoku benchmark instances
- `benchmarks/`: Benchmark and plotting scripts
- `results/`: Experimental results and generated figures
- `report/`: Scientific report and figures
- `tests/`: Automated tests

## Requirements

Use a Python version compatible with all required solver packages.

Install Python dependencies with:

```bash
python -m pip install -r requirements.txt
```

Some solvers require separate installations or valid licenses. In particular, CPLEX and Gurobi may require their own software installations and license configuration.

## Implemented Solvers

- **SAT:** Sudoku encoded as a Boolean satisfiability problem.
- **CP-SAT:** Sudoku modeled using Google OR-Tools.
- **CPLEX MIP:** Sudoku modeled as a binary mixed-integer programming problem using IBM CPLEX.
- **Gurobi MIP:** Sudoku modeled as a binary mixed-integer programming problem using Gurobi.

## Dataset

The benchmark dataset is stored in `data/sudoku_instances.json`.

It contains 30 Sudoku instances:
- 10 easy instances
- 10 medium instances
- 10 hard instances

## Running Tests

Run from the project root:

```bash
python -m pytest -v
```

## Running the Four-Solver Benchmark

Run from the project root:

```bash
python -m benchmarks.benchmark
```

The benchmark compares SAT, CP-SAT, CPLEX MIP, and Gurobi MIP on the dataset. Each solver is warmed up once per instance, then measured five times. The median solving time is recorded for each instance and solver.

Output:

`results/benchmark_sat_cpsat_cplex_gurobi.csv`

## Generating the Comparison Chart

Run:

```bash
python -m benchmarks.plot_results
```

Output:

`results/sat_vs_cpsat_cplex_gurobi.png`

The chart compares the mean of the per-instance median solving times for each solver, grouped by difficulty.

## Experimental Results

In the current benchmark run, the mean solving times were:

| Difficulty | SAT (ms) | CP-SAT (ms) | CPLEX (ms) | Gurobi (ms) |
|---|---:|---:|---:|---:|
| Easy | 12.253 | 15.402 | 7.501 | 14.713 |
| Medium | 12.515 | 15.423 | 7.457 | 14.906 |
| Hard | 15.838 | 25.943 | 12.599 | 20.921 |

These values are specific to the current dataset, hardware, solver versions, and configuration. They should not be interpreted as universal rankings of the solvers.

## Experimental Integrity

Only report results obtained from actual executions. Record the hardware, Python and solver versions, solver parameters, and timeout settings when preparing a formal report.

## Repository

https://github.com/transonnn/sudoku-sat-solver