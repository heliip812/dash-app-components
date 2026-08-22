"""Group-by transformation returning a regular, presentation-neutral frame."""

from collections.abc import Mapping, Sequence
import pandas as pd

from src.utils.validation import require_columns


def group_dataframe(
    frame: pd.DataFrame,
    by: Sequence[str],
    aggregations: Mapping[str, str | list[str]],
    *,
    dropna: bool = False,
) -> pd.DataFrame:
    require_columns(frame, [*by, *aggregations.keys()])
    result = frame.groupby(list(by), dropna=dropna, observed=True).agg(dict(aggregations)).reset_index()
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = ["_".join(str(part) for part in column if part) for column in result.columns]
    return result
