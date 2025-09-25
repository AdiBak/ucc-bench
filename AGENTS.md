# Repository Guidelines

## Project Structure & Module Organization
Core logic lives in `src/ucc_bench/`; notable modules include `compilers/` for backend adapters, `simulation/` for noisy and ideal runs, and `runner.py` for orchestration. Benchmark specifications and QASM assets sit under `benchmarks/`, while rendered charts belong in `plotting/` and canonical outputs reside in `results/`. Tests mirror package layout inside `tests/`, and `pyproject.toml` plus `uv.lock` define dependencies and tool versions.

## Build, Test, and Development Commands
Bootstrap the environment with `uv sync`, or `uv sync --all-groups` when you need optional `pyqpanda3` support. Run a suite locally via `uv run ucc-bench benchmarks/compilation_benchmarks.toml`. Execute targeted runs with `--only_compiler` or `--only_benchmark` to validate incremental changes. Keep the lockfile fresh after dependency bumps using `uv lock --upgrade-package <name>`.

## Coding Style & Naming Conventions
All code targets Python 3.12 and uses four-space indentation. Modules, files, and functions follow `snake_case`; classes remain `PascalCase`; registry identifiers match the lowercase-hyphen form already present (for example `my-compiler-id`). The project is typed (`py.typed`), so prefer explicit type hints. Before sending changes, run `uv run ruff check src tests` and `uv run mypy src` to enforce linting and typing expectations.

## Testing Guidelines
Unit and integration tests sit in `tests/` and should be named `test_<feature>.py` with `pytest`-style functions or fixtures. Add coverage whenever a compiler, observable, or runner path changes, especially for new benchmark metadata fields. Validate the whole suite with `uv run pytest`; for long benchmark loops, it is acceptable to mark slow cases with `pytest.mark.slow` and document how to exercise them manually.

## Commit & Pull Request Guidelines
Recent history favors descriptive prefixes such as `chore:` or bracketed tags like `[benchmark chore]` and `[upgrade chore]`; follow the same pattern and keep subjects under 72 characters. Each pull request should summarize motivation, list affected benchmark suites, and link any related issues. Include command outputs (e.g., `uv run ucc-bench ...`) or screenshots when results or plots change, and note updates to `benchmarks/*` or `results/*` so reviewers can regenerate artifacts confidently.

## Benchmark Data Tips
When modifying TOML suites, bump the `suite_version` field and explain the change in the PR body. Store large raw outputs in the standard `{out_dir}/{runner}/{suite_id}/...` layout, and avoid committing temporary `.local_results` artifacts.
