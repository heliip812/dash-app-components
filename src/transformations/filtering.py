"""Composable row filters kept independent from Dash callbacks."""

from collections.abc import Iterable, Mapping
import pandas as pd

from src.utils.validation import require_columns


SUPPORTED_OPERATORS = {"eq", "ne", "gt", "gte", "lt", "lte", "contains", "in", "between"}


def filter_dataframe(frame: pd.DataFrame, filters: Iterable[Mapping] | None = None) -> pd.DataFrame:
    filters = list(filters or [])
    if not filters:
        return frame
    require_columns(frame, (item["field"] for item in filters))
    mask = pd.Series(True, index=frame.index)
    for item in filters:
        field = item["field"]
        operator = item.get("operator", "eq")
        value = item.get("value")
        if operator not in SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported filter operator: {operator}")
        series = frame[field]
        if operator == "eq":
            current = series == value
        elif operator == "ne":
            current = series != value
        elif operator == "gt":
            current = series > value
        elif operator == "gte":
            current = series >= value
        elif operator == "lt":
            current = series < value
        elif operator == "lte":
            current = series <= value
        elif operator == "contains":
            current = series.astype("string").str.contains(str(value), case=False, na=False, regex=False)
        elif operator == "in":
            current = series.isin(value if isinstance(value, (list, tuple, set)) else [value])
        else:
            if not isinstance(value, (list, tuple)) or len(value) != 2:
                raise ValueError("between filters require a two-item value")
            current = series.between(value[0], value[1], inclusive="both")
        mask &= current.fillna(False)
    return frame.loc[mask]
