"""Convenience wrapper for nested expandable tables."""

from .tabulator_table import tabulator_table
from .table_options import tree_table_options


def expandable_table(table_id: str, *, data: list[dict], columns: list[dict], options: dict | None = None):
    return tabulator_table(
        table_id,
        data=data,
        columns=columns,
        options=tree_table_options(**(options or {})),
        class_name="table-component--tree",
        aria_label="Expandable hierarchy table",
    )
