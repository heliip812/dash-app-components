"""Stable DataFrame sorting."""

from collections.abc import Sequence
import pandas as pd

from src.utils.validation import as_list, require_columns


def sort_dataframe(
    frame: pd.DataFrame,
    by: str | Sequence[str],
    ascending: bool | Sequence[bool] = True,
    *,
    na_position: str = "last",
) -> pd.DataFrame:
    columns = as_list(by)
    require_columns(frame, columns)
    return frame.sort_values(columns, ascending=ascending, na_position=na_position, kind="stable")
