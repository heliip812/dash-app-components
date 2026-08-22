"""Semantic alias for a hierarchy-oriented expandable table."""

from .expandable_table import expandable_table


def hierarchy_table(table_id: str, *, hierarchy: list[dict], columns: list[dict], options: dict | None = None):
    return expandable_table(table_id, data=hierarchy, columns=columns, options=options)
