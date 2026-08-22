"""Convert tabular groupings into Tabulator-compatible ``_children`` trees."""

from collections.abc import Mapping, Sequence
from typing import Any
import pandas as pd

from src.utils.validation import require_columns


def _python_value(value):
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def build_hierarchy(
    frame: pd.DataFrame,
    *,
    levels: Sequence[str],
    aggregations: Mapping[str, str] | None = None,
    label_field: str = "label",
    id_field: str = "node_id",
) -> list[dict[str, Any]]:
    levels = list(levels)
    aggregations = dict(aggregations or {"value": "sum"})
    if not levels:
        raise ValueError("At least one hierarchy level is required")
    require_columns(frame, [*levels, *aggregations.keys()])

    def visit(current: pd.DataFrame, depth: int, path: tuple[str, ...]) -> list[dict[str, Any]]:
        level = levels[depth]
        records: list[dict[str, Any]] = []
        grouped = current.groupby(level, observed=True, dropna=False, sort=True)
        for raw_label, group in grouped:
            label = "Unspecified" if pd.isna(raw_label) else str(raw_label)
            node_path = (*path, label)
            node = {
                id_field: "/".join(node_path),
                label_field: label,
                "level": depth,
                "record_count": int(len(group)),
            }
            for column, operation in aggregations.items():
                node[column] = _python_value(group[column].agg(operation))
            if depth + 1 < len(levels):
                children = visit(group, depth + 1, node_path)
                if children:
                    node["_children"] = children
            records.append(node)
        return records

    return visit(frame, 0, tuple())


def flatten_hierarchy(
    records: Sequence[Mapping[str, Any]],
    *,
    children_field: str = "_children",
    depth_field: str = "depth",
) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []

    def visit(nodes: Sequence[Mapping[str, Any]], depth: int) -> None:
        for node in nodes:
            row = {key: value for key, value in node.items() if key != children_field}
            row[depth_field] = depth
            flattened.append(row)
            visit(node.get(children_field, []), depth + 1)

    visit(records, 0)
    return flattened
