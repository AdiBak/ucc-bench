import argparse
import logging
import sys
from datetime import datetime
import uuid
import platform
from pathlib import Path
import psutil

from ucc_bench.suite import BenchmarkSuite, UnoptimizationSpec
from ucc_bench.runner import run_suite
from ucc_bench.results import (
    SuiteResults,
    RunnerSpecs,
    Metadata,
    save_results_json,
    save_results_csv,
)
from ucc_bench import __version__

# qBraid is setting up logging in a way that is incompatible with the logging setup in this file.
# To avoid conflicts, we will clear the existing handlers and configure logging here.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Command-line utility to run UCC compiler benchmark comparisons."
    )
    parser.add_argument(
        "spec_path",
        help="Path to the TOML file specifying the benchmark suite to run.",
    )
    parser.add_argument(
        "--uid",
        help="Unique identifier for the run. If not provided, a random UUID is generated. For official results, use the git hash of the commit being tested.",
    )
    parser.add_argument(
        "--uid_timestamp",
        help="Timestamp for the unique identifier. If not provided, the current time is used. For official results, use the timestamp of the git commit being tested.",
    )
    parser.add_argument(
        "-o",
        "--out",
        default=".local_results",
        help="Root directory to save results. Defaults to '.local_results'. Individual run results are stored in a hierarchy within this directory.",
    )
    parser.add_argument(
        "--runner_name",
        default=platform.node(),
        help="Name of the runner machine. Should remain consistent across runs for comparison. Defaults to the current machine's hostname.",
    )
    parser.add_argument(
        "-j",
        "--parallel",
        help="Number of benchmarks to run in parallel. Defaults to the number of physical CPU cores if not specified.",
    )
    parser.add_argument(
        "--log_level",
        default="WARNING",
        help="Logging level for the application. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL. Defaults to 'WARNING'.",
    )
    parser.add_argument(
        "--only_compiler",
        help="Run benchmarks only for the specified compiler.",
    )
    parser.add_argument(
        "--only_benchmark",
        help="Run only the specified benchmark.",
    )

    parser.add_argument(
        "--only_target_device",
        help="Run only the specified target device.",
    )

    parser.add_argument(
        "--ucc_hash",
        help="Hash of commit of UCC being tested. This is used to track the version of UCC being benchmarked.",
    )
    parser.add_argument(
        "--ucc_timestamp",
        help="Timestamp of commit of UCC being tested. This is used to track the version of UCC being benchmarked.",
    )

    # Unoptimization (Elementary Recipe) CLI overrides
    parser.add_argument(
        "--unopt",
        action="store_true",
        help="Enable quantum circuit unoptimization (elementary recipe) prior to compilation.",
    )
    parser.add_argument(
        "--unopt-iterations",
        type=int,
        help="Number of unoptimization iterations to apply.",
    )
    parser.add_argument(
        "--unopt-strategy",
        choices=["concatenated", "random"],
        help="Strategy used to select insertion points for unoptimization.",
    )
    parser.add_argument(
        "--unopt-decomposition",
        choices=["default", "kak", "basis"],
        help="Decomposition method for unitary synthesis during unoptimization.",
    )
    parser.add_argument(
        "--unopt-opt-level",
        type=int,
        choices=[0, 1, 2, 3],
        help="Qiskit optimization level for the final synthesis step during unoptimization.",
    )
    parser.add_argument(
        "--unopt-seed",
        type=int,
        help="Random seed for deterministic unoptimization.",
    )
    parser.add_argument(
        "--unopt-skip-synth",
        action="store_true",
        help="Skip the final Qiskit synthesis step during unoptimization.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s [%(levelname)s] %(module)s: %(message)s",
    )

    suite = BenchmarkSuite.load_toml(args.spec_path)

    # Apply unoptimization CLI overrides onto the suite config
    if (
        any(
            getattr(args, name) is not None
            for name in [
                "unopt_iterations",
                "unopt_strategy",
                "unopt_decomposition",
                "unopt_opt_level",
                "unopt_seed",
            ]
        )
        or args.unopt
    ):
        if suite.unoptimization is None:
            suite.unoptimization = UnoptimizationSpec()
        # Enable if flag provided
        if args.unopt:
            suite.unoptimization.enabled = True
        if args.unopt_iterations is not None:
            suite.unoptimization.iterations = args.unopt_iterations
        if args.unopt_strategy is not None:
            suite.unoptimization.strategy = args.unopt_strategy  # type: ignore[assignment]
        if args.unopt_decomposition is not None:
            suite.unoptimization.decomposition_method = args.unopt_decomposition  # type: ignore[assignment]
        if args.unopt_opt_level is not None:
            suite.unoptimization.optimization_level = args.unopt_opt_level
        if args.unopt_seed is not None:
            suite.unoptimization.seed = args.unopt_seed
        if args.unopt_skip_synth:
            suite.unoptimization.skip_synthesize = True

    run_start = datetime.now()
    num_parallel = (
        int(args.parallel) if args.parallel else psutil.cpu_count(logical=False)
    )
    print(f"Running benchmark suite '{suite.id}' with {num_parallel} parallel tasks")
    benchmark_results = run_suite(
        suite,
        num_parallel,
        only_compiler=args.only_compiler,
        only_benchmark=args.only_benchmark,
        only_target_device=args.only_target_device,
    )
    run_end = datetime.now()

    results = SuiteResults(
        suite_specification=suite,
        metadata=Metadata(
            uid=args.uid or str(uuid.uuid4()),
            uid_timestamp=args.uid_timestamp or datetime.now(),
            run_start=run_start,
            run_end=run_end,
            runner_name=args.runner_name,
            runner_specs=RunnerSpecs.from_system(),
            runner_version=__version__,
            runner_args=sys.argv,
            ucc_hash=args.ucc_hash,
            ucc_timestamp=args.ucc_timestamp,
        ),
        results=benchmark_results,
    )
    logger.info(f"Finished running benchmark suite '{suite.id}'")

    save_results_json(results, Path(args.out))
    save_results_csv(results, Path(args.out))


if "__main__" == __name__:
    main()
