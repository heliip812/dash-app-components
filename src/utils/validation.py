"""Shared validation helpers."""

from collections.abc import Iterable


def require_columns(frame, columns: Iterable[str]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"Unknown DataFrame columns: {', '.join(missing)}")


def as_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
