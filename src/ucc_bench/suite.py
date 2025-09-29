import tomllib
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


from .registry import register


class CompilerSpec(BaseModel):
    """
    Represents a compiler to benchmark against

    Attributes:
        id: The id of the compiler, used to look up the compiler in the registry
    """

    id: str

    @field_validator("id", mode="after")
    @classmethod
    def is_valid_compiler(cls, value: str) -> str:
        if not register.has_compiler(value):
            raise ValueError(f"Unknown compiler id: {value}")
        return value


class SimulationSpec(BaseModel):
    measurement: str

    @field_validator("measurement", mode="after")
    @classmethod
    def is_valid_measurement(cls, value: str) -> str:
        if not register.has_observable(value) and not register.has_output_metric(value):
            raise ValueError(f"Unknown measurement id: {value}")
        return value


class TargetDeviceSpec(BaseModel):
    """
    Represents a target device to compile the circuit for.

    Attributes:
        The name of the target device, as defined in the registry.
    """

    id: str

    @field_validator("id", mode="after")
    @classmethod
    def is_valid_target_device(cls, value: str) -> str:
        if not register.has_target_device(value):
            raise ValueError(f"Unknown target device: {value}")
        return value


class BenchmarkSpec(BaseModel):
    """
    Represents a specific benchmark (circuit+metrics) to run.

    Attributes:
        id: The id of the benchmark, used to identify the benchmark
        description: A human-readable description of the benchmark
        qasm_file: The path to the QASM file containing the benchmark circuit. This path is relative to the spec file itself.
    """

    id: str
    description: str
    qasm_file: Path
    resolved_qasm_file: Optional[Path] = None
    simulate: Optional[SimulationSpec] = None


class BenchmarkSuite(BaseModel):
    """
    Represents a specification of a benchmark suite.

    Attributes:
        spec_path: The path to the specification file
        spec_version: The version of the specification format
        suite_version: The version of the benchmark suite
        id: The id of the suite
        description: A human-readable description of the suite
        compilers: A list of compilers to benchmark against
        benchmarks: A list of benchmarks to run
    """

    spec_path: Path
    spec_version: str
    suite_version: str
    id: str
    description: str
    compilers: List[CompilerSpec] = Field(default_factory=list)
    benchmarks: List[BenchmarkSpec] = Field(default_factory=list)
    target_devices: List[TargetDeviceSpec] = Field(default_factory=list)

    @classmethod
    def load_toml(cls, path: str) -> "BenchmarkSuite":
        """Load a specification from a TOML file at the specified path."""
        with open(path, "rb") as f:
            raw = tomllib.load(f)
            raw["spec_path"] = Path(path)
            return BenchmarkSuite.model_validate(raw)

    @model_validator(mode="after")
    def _post_init_checks(self):
        """Run data integrity checks after model construction."""
        self._ensure_unique_ids()
        self._canonicalize_and_validate_qasm_paths()
        return self

    def _ensure_unique_ids(self) -> None:
        """Ensure ids are unique for compilers, benchmarks, and target devices."""
        self.__class__._ensure_unique_ids_core(
            benchmarks=self.benchmarks,
            compilers=self.compilers,
            target_devices=self.target_devices,
        )

    def _canonicalize_and_validate_qasm_paths(self) -> None:
        """Resolve benchmark QASM paths relative to the suite specification path."""
        self.__class__._canonicalize_and_validate_qasm_paths_core(
            spec_path=self.spec_path,
            benchmarks=self.benchmarks,
        )

    @staticmethod
    def _ensure_unique_ids_core(
        *,
        benchmarks: List[BenchmarkSpec],
        compilers: List[CompilerSpec],
        target_devices: List[TargetDeviceSpec],
    ) -> None:
        for field_name, items in (
            ("benchmarks", benchmarks),
            ("compilers", compilers),
            ("target_devices", target_devices),
        ):
            seen = set()
            for item in items:
                if item.id in seen:
                    raise ValueError(f"Duplicate {field_name[:-1]} id: {item.id}")
                seen.add(item.id)

    @staticmethod
    def _canonicalize_and_validate_qasm_paths_core(
        *, spec_path: Path, benchmarks: List[BenchmarkSpec]
    ) -> None:
        for benchmark in benchmarks:
            if benchmark.resolved_qasm_file is None:
                benchmark.resolved_qasm_file = spec_path.parent / benchmark.qasm_file
            if not benchmark.resolved_qasm_file.is_file():
                raise ValueError(
                    "qasm_file for benchmark "
                    f"'{benchmark.id}' does not point to a valid file: {benchmark.resolved_qasm_file}"
                )

