"""Build the app's process-local dataset registry once at startup."""

from .loaders import load_parquet
from .registry import DataFrameRegistry
from .sample_data import ensure_sample_parquet
from src.utils.paths import SAMPLE_PARQUET_PATH
from src.utils.timing import timer


DEFAULT_DATASET_ID = "sample"


def bootstrap_registry(registry: DataFrameRegistry | None = None) -> DataFrameRegistry:
    registry = registry or DataFrameRegistry()
    if registry.contains(DEFAULT_DATASET_ID):
        return registry
    # APPLICATION-SPECIFIC FUNCTION GOES HERE: replace this sample source with
    # a configured Parquet/CSV path or a loader owned by your deployment.
    source = ensure_sample_parquet(SAMPLE_PARQUET_PATH)
    with timer("load sample parquet"):
        frame = load_parquet(source)
    registry.register(
        DEFAULT_DATASET_ID,
        frame,
        source=str(source),
        attributes={"format": "parquet", "load_count": 1},
    )
    return registry
