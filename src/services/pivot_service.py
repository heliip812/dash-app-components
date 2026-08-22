"""Pivot orchestration independent from tables and Plotly."""

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import pandas as pd

from src.data.cache import DataFrameResultCache
from src.services.dataframe_service import DataFrameService
from src.transformations import filter_dataframe, pivot_dataframe
from src.utils.validation import as_list


@dataclass(frozen=True)
class PivotRequest:
    dataset_id: str
    rows: Sequence[str]
    columns: Sequence[str]
    value: str
    aggregation: str = "sum"
    filters: tuple[Mapping, ...] = ()


@dataclass(frozen=True)
class PivotResult:
    table: pd.DataFrame
    matrix: pd.DataFrame
    row_fields: tuple[str, ...]
    value_field: str
    aggregation: str


class PivotService:
    def __init__(self, dataframes: DataFrameService, cache: DataFrameResultCache | None = None):
        self.dataframes = dataframes
        self.cache = cache or DataFrameResultCache()

    def run(self, request: PivotRequest) -> PivotResult:
        rows = tuple(as_list(request.rows))
        columns = tuple(as_list(request.columns))
        filter_key = tuple(sorted((item["field"], item.get("operator", "eq"), str(item.get("value"))) for item in request.filters))
        cache_key = (request.dataset_id, rows, columns, request.value, request.aggregation, filter_key)
        pivot = self.cache.get(cache_key)
        if pivot is None:
            source = filter_dataframe(self.dataframes.get(request.dataset_id), request.filters)
            pivot = pivot_dataframe(
                source,
                rows=rows,
                columns=columns,
                values=request.value,
                aggregation=request.aggregation,
            )
            self.cache.put(cache_key, pivot)
        numeric_columns = [column for column in pivot.columns if column not in rows]
        if numeric_columns:
            row_labels = pivot.loc[:, list(rows)].astype(str).agg(" / ".join, axis=1)
            matrix = pivot.loc[:, numeric_columns].copy(deep=False)
            matrix.index = row_labels
        else:
            matrix = pd.DataFrame()
        return PivotResult(pivot, matrix, rows, request.value, request.aggregation)
