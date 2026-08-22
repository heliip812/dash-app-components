"""Format-dispatching loader with a deliberately small public API."""

from pathlib import Path
import pandas as pd

from .csv_loader import load_csv
from .feather_loader import load_feather
from .parquet_loader import load_parquet


def load_dataframe(path: str | Path, **kwargs) -> pd.DataFrame:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".parquet", ".pq"}:
        return load_parquet(source, **kwargs)
    if suffix == ".csv":
        return load_csv(source, **kwargs)
    if suffix in {".feather", ".arrow"}:
        return load_feather(source, **kwargs)
    raise ValueError(f"Unsupported DataFrame format: {suffix or '<none>'}")
