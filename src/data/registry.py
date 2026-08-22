"""Thread-safe, process-local registry for immutable-by-convention DataFrames."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class DatasetMetadata:
    dataset_id: str
    rows: int
    columns: tuple[str, ...]
    memory_bytes: int
    registered_at: datetime
    source: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


class DataFrameRegistry:
    """Own loaded frames for one app process.

    ``get`` returns the registered object to avoid multi-million-row copies. Callers
    must treat it as read-only and make derived frames through transformations.
    Multi-process deployments create one registry per worker by design.
    """

    def __init__(self) -> None:
        self._frames: dict[str, pd.DataFrame] = {}
        self._metadata: dict[str, DatasetMetadata] = {}
        self._lock = RLock()

    def register(
        self,
        dataset_id: str,
        dataframe: pd.DataFrame,
        *,
        source: str | None = None,
        replace: bool = False,
        attributes: dict[str, Any] | None = None,
    ) -> DatasetMetadata:
        if not dataset_id or not isinstance(dataset_id, str):
            raise ValueError("dataset_id must be a non-empty string")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe must be a pandas DataFrame")
        with self._lock:
            if dataset_id in self._frames and not replace:
                raise KeyError(f"Dataset already registered: {dataset_id}")
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                rows=len(dataframe),
                columns=tuple(str(column) for column in dataframe.columns),
                memory_bytes=int(dataframe.memory_usage(index=True, deep=True).sum()),
                registered_at=datetime.now(timezone.utc),
                source=source,
                attributes=dict(attributes or {}),
            )
            self._frames[dataset_id] = dataframe
            self._metadata[dataset_id] = metadata
            return metadata

    def get(self, dataset_id: str) -> pd.DataFrame:
        with self._lock:
            try:
                return self._frames[dataset_id]
            except KeyError as error:
                raise KeyError(f"Unknown dataset: {dataset_id}") from error

    def metadata(self, dataset_id: str) -> DatasetMetadata:
        with self._lock:
            try:
                return self._metadata[dataset_id]
            except KeyError as error:
                raise KeyError(f"Unknown dataset: {dataset_id}") from error

    def contains(self, dataset_id: str) -> bool:
        with self._lock:
            return dataset_id in self._frames

    def list_datasets(self) -> tuple[DatasetMetadata, ...]:
        with self._lock:
            return tuple(self._metadata.values())

    def remove(self, dataset_id: str) -> None:
        with self._lock:
            self._frames.pop(dataset_id, None)
            self._metadata.pop(dataset_id, None)

    def clear(self) -> None:
        with self._lock:
            self._frames.clear()
            self._metadata.clear()
