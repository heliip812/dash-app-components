"""Optional Feather loader using the same Apache Arrow dependency as Parquet."""

from pathlib import Path
import pandas as pd


def load_feather(path: str | Path, *, columns: list[str] | None = None, **kwargs) -> pd.DataFrame:
    return pd.read_feather(Path(path), columns=columns, **kwargs)
