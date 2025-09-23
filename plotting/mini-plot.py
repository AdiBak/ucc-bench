from shared import get_compiler_colormap

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_compiled_metrics(csv_path):
    """
    Plot compiled_ideal and compiled_noisy for each compiler and benchmark as subplots.
    """
    df = pd.read_csv(csv_path)
    benchmarks = df["benchmark_id"].unique()
    compilers = df["compiler"].unique()
    n_benchmarks = len(benchmarks)
    ncols = 3
    nrows = int(np.ceil(n_benchmarks / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), sharex=True)
    axes = axes.flatten()

    bar_width = 0.35
    index = np.arange(len(compilers))
    # Use shared colormap for compilers
    compiler_colors = get_compiler_colormap()

    for i, benchmark in enumerate(benchmarks):
        ax = axes[i]
        sub = df[df["benchmark_id"] == benchmark]
        bars_ideal = []
        bars_noisy = []
        for compiler in compilers:
            row = sub[sub["compiler"] == compiler]
            bars_ideal.append(
                row["compiled_ideal"].values[0] if not row.empty else np.nan
            )
            bars_noisy.append(
                row["compiled_noisy"].values[0] if not row.empty else np.nan
            )
        # Plot compiled_ideal and compiled_noisy side by side for each compiler, color-coded
        for j, compiler in enumerate(compilers):
            ax.bar(
                j - bar_width / 2,
                bars_ideal[j],
                bar_width,
                label="compiled_ideal" if j == 0 else "",
                color=compiler_colors.get(compiler, "#4C72B0"),
                alpha=0.7,
            )
            ax.bar(
                j + bar_width / 2,
                bars_noisy[j],
                bar_width,
                label="compiled_noisy" if j == 0 else "",
                color=compiler_colors.get(compiler, "#4C72B0"),
                alpha=1.0,
                hatch="//",
            )
        ax.set_xticks(index)
        ax.set_xticklabels(compilers, rotation=30)
        ax.set_title(f"Benchmark: {benchmark}")
        ax.set_ylabel("Value")
        if i == 0:
            ax.legend()
    # Hide unused subplots
    for j in range(n_benchmarks, nrows * ncols):
        fig.delaxes(axes[j])
    plt.tight_layout()
    plt.show()


def plot_relative_error(csv_path):
    """
    Plot the relative error between compiled_noisy and uncompiled_ideal for each compiler and benchmark as subplots.
    """
    df = pd.read_csv(csv_path)
    benchmarks = df["benchmark_id"].unique()
    compilers = df["compiler"].unique()
    n_benchmarks = len(benchmarks)
    ncols = 3
    nrows = int(np.ceil(n_benchmarks / ncols))
    # Compute relative error: (compiled_noisy - uncompiled_ideal) / uncompiled_ideal
    df["relative_error"] = (df["compiled_noisy"] - df["uncompiled_ideal"]) / df[
        "uncompiled_ideal"
    ]

    fig, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), sharex=True)
    axes = axes.flatten()
    index = np.arange(len(compilers))
    compiler_colors = get_compiler_colormap()

    for i, benchmark in enumerate(benchmarks):
        ax = axes[i]
        sub = df[df["benchmark_id"] == benchmark]
        rel_errs = []
        for j, compiler in enumerate(compilers):
            row = sub[sub["compiler"] == compiler]
            rel_errs.append(
                row["relative_error"].values[0] if not row.empty else np.nan
            )
            ax.bar(
                j,
                rel_errs[-1],
                color=compiler_colors.get(compiler, "#4C72B0"),
                width=0.5,
            )
        ax.set_xticks(index)
        ax.set_xticklabels(compilers, rotation=30)
        ax.set_ylabel("Relative Error")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    # Hide unused subplots
    for j in range(n_benchmarks, nrows * ncols):
        fig.delaxes(axes[j])
    plt.tight_layout()
    plt.show()


plot_relative_error(
    "/Users/jordansullivan/UnitaryFoundation/ucc-bench/.local_results/Jordans-MacBook-Pro.local/simulation_benchmarks/20250922/20250922175509.18cc536c-7100-4fd9-8900-ecb19deb5eb0.simulation.csv"
)
