"""Bounded copy-on-read cache for expensive, compact derived DataFrames."""

from collections import OrderedDict
from threading import RLock
import pandas as pd


class DataFrameResultCache:
    def __init__(self, max_entries: int = 32) -> None:
        self.max_entries = max_entries
        self._values: OrderedDict[tuple, pd.DataFrame] = OrderedDict()
        self._lock = RLock()

    def get(self, key: tuple) -> pd.DataFrame | None:
        with self._lock:
            value = self._values.get(key)
            if value is None:
                return None
            self._values.move_to_end(key)
            return value.copy(deep=False)

    def put(self, key: tuple, value: pd.DataFrame) -> None:
        with self._lock:
            self._values[key] = value.copy(deep=False)
            self._values.move_to_end(key)
            while len(self._values) > self.max_entries:
                self._values.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()
