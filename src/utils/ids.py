"""Stable component ID helpers."""


def view_id(name: str) -> str:
    return f"view-{name}"


def nav_id(name: str) -> str:
    return f"nav-{name}"


def table_config_id(table_id: str) -> str:
    return f"{table_id}--config"


def table_selection_id(table_id: str) -> str:
    return f"{table_id}--selection"
