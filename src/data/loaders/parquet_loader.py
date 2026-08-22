"""Parquet loader."""

from pathlib import Path
import pandas as pd


def load_parquet(path: str | Path, *, columns: list[str] | None = None, **kwargs) -> pd.DataFrame:
    return pd.read_parquet(Path(path), columns=columns, **kwargs)
