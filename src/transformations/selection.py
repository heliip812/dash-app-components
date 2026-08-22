"""Column projection."""

from collections.abc import Sequence
import pandas as pd

from src.utils.validation import require_columns


def select_columns(frame: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    require_columns(frame, columns)
    return frame.loc[:, list(columns)]
