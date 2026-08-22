"""Whole-frame aggregation with a predictable one-row result."""

from collections.abc import Mapping
import pandas as pd

from src.utils.validation import require_columns


def aggregate_dataframe(frame: pd.DataFrame, aggregations: Mapping[str, str]) -> pd.DataFrame:
    require_columns(frame, aggregations.keys())
    values = {f"{column}_{operation}": frame[column].agg(operation) for column, operation in aggregations.items()}
    return pd.DataFrame([values])
