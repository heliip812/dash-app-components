"""CSV loader."""

from pathlib import Path
import pandas as pd


def load_csv(path: str | Path, **kwargs) -> pd.DataFrame:
    return pd.read_csv(Path(path), **kwargs)
