import argparse
from pathlib import Path
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ucc_bench.results import SuiteResultsDatabase, to_df_timing, to_df_simulation

from shared import calculate_abs_relative_error, get_compiler_colormap

BAR_WIDTH = 0.35


def generate_compilation_subplots(
    df: pd.DataFrame,
    plot_configs: list[dict],
    latest_date: str,
    out_path: Path,
    use_pdf: bool = False,
):
    """Generate subplots for compilation benchmarks with separate subplot per benchmark."""
    # Configure matplotlib for LaTeX output if PDF export is requested
    if use_pdf:
        plt.rcParams.update(
            {
                "text.usetex": True,  # for matching math & fonts (optional)
                "font.family": "serif",
            }
        )

    benchmarks = sorted(df["benchmark_id"].unique())
    compilers = df["compiler"].unique()
    n_benchmarks = len(benchmarks)
    ncols = 3
    nrows = 2
    
    # Create separate figures for each metric
    for config in plot_configs:
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
        axes = axes.flatten()
        color_map = get_compiler_colormap()
        
        for i, ax in enumerate(axes):
            if i < n_benchmarks:
                benchmark = benchmarks[i]
                sub = df[df["benchmark_id"] == benchmark]
                
                # Extract values for each compiler
                values = []
                compiler_names = []
                for compiler in compilers:
                    row = sub[sub["compiler"] == compiler]
                    if not row.empty:
                        values.append(row[config["y_col"]].values[0])
                        compiler_names.append(compiler)
                
                # Create bars
                x_positions = np.arange(len(compiler_names))
                bars = ax.bar(
                    x_positions,
                    values,
                    color=[color_map.get(compiler, "#4C72B0") for compiler in compiler_names],
                    width=0.5,
                )
                
                ax.set_xticks(x_positions)
                ax.set_xticklabels(compiler_names, rotation=30, ha="right")
                ax.set_title(f"Benchmark: {benchmark}")
                ax.set_ylabel(config["ylabel"])
                # Use log scale only if specified in config (default to True for backwards compatibility)
                if config.get("use_log_scale", True):
                    ax.set_yscale("log")
            else:
                ax.set_visible(False)
        
        plt.suptitle(f"{config['title']} (Date: {latest_date})", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save with metric-specific filename
        metric_name = config["y_col"].replace("_", "-")
        metric_out_path = out_path.parent / f"{out_path.stem}_{metric_name}{out_path.suffix}"
        print(f"Saving plot to {metric_out_path}")
        fig.savefig(metric_out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)


def plot_compilation(
    df: pd.DataFrame, latest_date: str, out_path: Path, use_pdf: bool = False
):
    """Generates and saves plots for compilation benchmark data."""
    df_comp = df.copy()
    df_comp["compiled_ratio"] = df_comp["compiled_multiq_gates"] / df_comp["raw_multiq_gates"]
    
    plot_configs = [
        {
            "y_col": "compile_time",
            "title": "Compiler Performance",
            "ylabel": "Compile Time (s)",
            "use_log_scale": True,
        },
        {
            "y_col": "compiled_multiq_gates",
            "title": "Gate Counts",
            "ylabel": "Compiled Gate Count",
            "use_log_scale": True,
        },
        {
            "y_col": "compiled_ratio",
            "title": "Compiled Gate Ratio",
            "ylabel": "Compiled Gates / Raw Gates",
            "use_log_scale": False,
        },
    ]
    generate_compilation_subplots(df_comp, plot_configs, latest_date, out_path, use_pdf)


def generate_simulation_subplots(
    df: pd.DataFrame,
    plot_configs: list[dict],
    latest_date: str,
    out_path: Path,
    use_pdf: bool = False,
):
    """Generate subplots for simulation benchmarks with separate subplot per benchmark."""
    # Configure matplotlib for LaTeX output if PDF export is requested
    if use_pdf:
        plt.rcParams.update(
            {
                "text.usetex": True,  # for matching math & fonts (optional)
                "font.family": "serif",
            }
        )

    benchmarks = sorted(df["benchmark_id"].unique())
    compilers = df["compiler"].unique()
    n_benchmarks = len(benchmarks)
    ncols = 3
    nrows = 2
    
    # Create separate figures for each metric (like compilation plots)
    for config in plot_configs:
        fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
        axes = axes.flatten()
        color_map = get_compiler_colormap()
        
        for i, ax in enumerate(axes):
            if i < n_benchmarks:
                benchmark = benchmarks[i]
                sub = df[df["benchmark_id"] == benchmark]
                
                # Extract values for each compiler
                values = []
                compiler_names = []
                for compiler in compilers:
                    row = sub[sub["compiler"] == compiler]
                    if not row.empty:
                        values.append(row[config["y_col"]].values[0])
                        compiler_names.append(compiler)
                
                # Create bars
                x_positions = np.arange(len(compiler_names))
                bars = ax.bar(
                    x_positions,
                    values,
                    color=[color_map.get(compiler, "#4C72B0") for compiler in compiler_names],
                    width=0.5,
                )
                
                ax.set_xticks(x_positions)
                ax.set_xticklabels(compiler_names, rotation=30, ha="right")
                ax.set_title(f"Benchmark: {benchmark}")
                ax.set_ylabel(config["ylabel"])
            else:
                ax.set_visible(False)
        
        plt.suptitle(f"{config['title']} (Date: {latest_date})", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # Save with metric-specific filename
        metric_name = config["y_col"].replace("_", "-")
        metric_out_path = out_path.parent / f"{out_path.stem}_{metric_name}{out_path.suffix}"
        print(f"Saving plot to {metric_out_path}")
        fig.savefig(metric_out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)


def plot_simulation(
    df: pd.DataFrame, latest_date: str, out_path: Path, use_pdf: bool = False
):
    """Generates and saves plots for simulation benchmark data."""
    df_sim = df.copy()
    df_sim["rel_err_ideal"] = calculate_abs_relative_error(
        df_sim["compiled_ideal"], df_sim["uncompiled_ideal"]
    )
    df_sim["rel_err_noisy"] = calculate_abs_relative_error(
        df_sim["compiled_noisy"], df_sim["uncompiled_noisy"]
    )

    plot_configs = [
        {
            "y_col": "rel_err_ideal",
            "title": "Observable Error (Noiseless Sim)",
            "ylabel": "Absolute Relative Error",
        },
        {
            "y_col": "rel_err_noisy",
            "title": "Observable Error (Noisy Sim)",
            "ylabel": "Absolute Relative Error",
        },
    ]
    generate_simulation_subplots(df_sim, plot_configs, latest_date, out_path, use_pdf)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Plot latest benchmark results.")
    parser.add_argument("root_dir", type=Path, help="Root directory of the benchmarks.")
    parser.add_argument("runner_name", type=str, help="Name of the runner.")
    parser.add_argument(
        "--uid",
        type=str,
        default=None,
        help="UID of the benchmark result to plot. If provided, uses this UID instead of the latest.",
    )
    parser.add_argument(
        "--plot",
        type=str,
        choices=["all", "compilation", "simulation"],
        default="all",
        help="Which plot(s) to generate.",
    )
    parser.add_argument(
        "--pdf",
        action="store_true",
        help="Export plots as PDF files with LaTeX formatting instead of PNG.",
    )
    args = parser.parse_args()

    # --- Plot Compilation Benchmarks ---
    if args.plot in ["all", "compilation"]:
        db = SuiteResultsDatabase.from_root(
            args.root_dir, args.runner_name, "compilation_benchmarks"
        )

        suite_results = db.from_uid(args.uid) if args.uid else db.get_latest()
        if suite_results is None:
            print(f"No compilation data found for UID {args.uid}")
            sys.exit(1)

        latest_date = suite_results.metadata.uid_timestamp.strftime("%Y-%m-%d")

        df = to_df_timing(suite_results)
        if "compile_time_ms" in df.columns:
            df["compile_time"] = df["compile_time_ms"] / 1000.0

        file_ext = "pdf" if args.pdf else "png"
        out_path = (
            args.root_dir
            / args.runner_name
            / f"latest_compiler_benchmarks_by_circuit.{file_ext}"
        )
        plot_compilation(df, latest_date, out_path, args.pdf)

    # --- Plot Simulation Benchmarks ---
    if args.plot in ["all", "simulation"]:
        db = SuiteResultsDatabase.from_root(
            args.root_dir, args.runner_name, "simulation_benchmarks"
        )

        suite_results = db.from_uid(args.uid) if args.uid else db.get_latest()
        if suite_results is None:
            print(f"No simulation data found for UID {args.uid}")
            sys.exit(1)

        latest_date = suite_results.metadata.uid_timestamp.strftime("%Y-%m-%d")

        df = to_df_simulation(suite_results)

        file_ext = "pdf" if args.pdf else "png"
        out_path = (
            args.root_dir
            / args.runner_name
            / f"latest_simulation_benchmarks_by_circuit.{file_ext}"
        )
        plot_simulation(df, latest_date, out_path, args.pdf)


if __name__ == "__main__":
    main()
