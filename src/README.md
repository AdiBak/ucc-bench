This document gives a high-level overview of the modules in `ucc-bench`

## Architecture
* `main.py`: Handles command-line argument parsing, logging setup, loading the suite specification, initiating the run, and saving results.
* `runner.py`: Orchestrates the execution of benchmark tasks using concurrent.futures.ProcessPoolExecutor for parallelism. It calls run_task for each compiler/benchmark combination. run_task performs transpilation, compilation, optional simulation, and gathers results.
* `suite.py`: Defines Pydantic models (BenchmarkSuite, BenchmarkSpec, CompilerSpec, SimulationSpec) for parsing and validating the TOML configuration file. Handles path resolution for QASM files.
* `results.py`: Defines Pydantic models for structuring the output results (SuiteResults, BenchmarkResult, Metadata, CompilationMetrics, SimulationMetrics, etc.) and includes the save_results function.
* `registry.py`: Implements the Registry class and register instance. Provides decorators (@register.compiler, @register.observable, @register.output_metric) to dynamically register new components.
* `compilers/`: Contains modules for specific compiler implementations.
* * `base_compiler.py`: Defines the abstract BaseCompiler class interface.
* * `_compiler.py`: Concrete implementations for Qiskit, Cirq, PyTket, and UCC, inheriting from BaseCompiler and registered using the decorator.
* `simulation/`: Contains modules related to circuit simulation.
* * `noise_models.py`: Defines functions to create noise models (currently a standard depolarizing model).
* * `observables.py`: Provides functions to calculate expectation values and includes implementations of registered observables (computational_basis, qaoa).
* * `heavy_output_prob.py`: Implements the Heavy Output Probability metric as a registered output metric.

## Circuit Unoptimization

`ucc-bench` can optionally apply the "quantum circuit unoptimization" elementary recipe (arXiv:2311.03805) prior to compilation.
Configure this per-suite via a `[unoptimization]` section in the TOML specification:

```
[unoptimization]
enabled = true
iterations = 1
strategy = "concatenated"       # or "random"
decomposition_method = "default" # one of: default, kak, basis
optimization_level = 3
seed = 42                        # optional: fix randomness
```

An example suite is provided at `benchmarks/compilation_benchmarks_unoptimized.toml`, mirroring the base
compilation benchmarks but with unoptimization enabled.

### CLI Overrides

You can toggle or override unoptimization settings without editing the TOML via flags:

- `--unopt`: enable unoptimization
- `--unopt-iterations N`: set iterations
- `--unopt-strategy concatenated|random`: choose insertion strategy
- `--unopt-decomposition default|kak|basis`: choose decomposition method
- `--unopt-opt-level 0|1|2|3`: synthesis optimization level
- `--unopt-seed SEED`: fix randomness for reproducibility

Example:
`uv run ucc-bench benchmarks/compilation_benchmarks.toml --only_compiler ucc --unopt --unopt-iterations 2 --unopt-strategy random --unopt-seed 7`
