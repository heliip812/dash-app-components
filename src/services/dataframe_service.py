"""Read-only workflows over registry-owned DataFrames."""

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import pandas as pd

from src.data.registry import DataFrameRegistry
from src.transformations import filter_dataframe, select_columns, sort_dataframe


@dataclass(frozen=True)
class TableSlice:
    frame: pd.DataFrame
    filtered_rows: int
    total_rows: int
    offset: int
    limit: int


class DataFrameService:
    def __init__(self, registry: DataFrameRegistry):
        self.registry = registry

    def get(self, dataset_id: str) -> pd.DataFrame:
        # APPLICATION-SPECIFIC FUNCTION GOES HERE when access policy, dataset
        # tenancy, or additional source validation is required.
        return self.registry.get(dataset_id)

    def filtered(self, dataset_id: str, filters: list[Mapping] | None = None) -> pd.DataFrame:
        return filter_dataframe(self.get(dataset_id), filters)

    def distinct_values(self, dataset_id: str, column: str) -> list:
        frame = self.get(dataset_id)
        if column not in frame:
            raise ValueError(f"Unknown DataFrame column: {column}")
        return sorted(value for value in frame[column].dropna().unique().tolist())

    def table_slice(
        self,
        dataset_id: str,
        *,
        filters: list[Mapping] | None = None,
        columns: Sequence[str] | None = None,
        sort_by: str | Sequence[str] | None = None,
        ascending=True,
        offset: int = 0,
        limit: int = 1_000,
    ) -> TableSlice:
        source = self.get(dataset_id)
        filtered = filter_dataframe(source, filters)
        if sort_by:
            filtered = sort_dataframe(filtered, sort_by, ascending)
        if columns:
            filtered = select_columns(filtered, columns)
        start = max(int(offset), 0)
        size = max(min(int(limit), 10_000), 1)
        return TableSlice(
            frame=filtered.iloc[start : start + size],
            filtered_rows=len(filtered),
            total_rows=len(source),
            offset=start,
            limit=size,
        )

    def record(self, dataset_id: str, record_id: str, *, id_column: str = "record_id") -> dict | None:
        frame = self.get(dataset_id)
        matches = frame.loc[frame[id_column].astype(str) == str(record_id)]
        if matches.empty:
            return None
        return matches.iloc[0].to_dict()
