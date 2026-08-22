"""Pandas-based pivoting with flattened, UI-safe column labels."""

from collections.abc import Sequence
import pandas as pd

from src.utils.validation import as_list, require_columns


AGGREGATIONS = {"sum", "mean", "count", "min", "max"}


def _flatten_label(label) -> str:
    if isinstance(label, tuple):
        return " · ".join(str(part) for part in label if str(part))
    return str(label)


def pivot_dataframe(
    frame: pd.DataFrame,
    *,
    rows: str | Sequence[str],
    columns: str | Sequence[str] | None,
    values: str,
    aggregation: str = "sum",
    fill_value=0,
) -> pd.DataFrame:
    row_fields = as_list(rows)
    column_fields = as_list(columns)
    if not row_fields:
        raise ValueError("At least one row dimension is required")
    if aggregation not in AGGREGATIONS:
        raise ValueError(f"Unsupported aggregation: {aggregation}")
    require_columns(frame, [*row_fields, *column_fields, values])
    result = pd.pivot_table(
        frame,
        index=row_fields,
        columns=column_fields or None,
        values=values,
        aggfunc=aggregation,
        fill_value=fill_value,
        observed=True,
        sort=True,
    ).reset_index()
    result.columns = [_flatten_label(column) for column in result.columns]
    return result
