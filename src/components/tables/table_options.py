"""Composable Tabulator option dictionaries."""

from copy import deepcopy


def merge_options(*option_sets: dict | None) -> dict:
    result: dict = {}
    for option_set in option_sets:
        for key, value in (option_set or {}).items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = merge_options(result[key], value)
            else:
                result[key] = deepcopy(value)
    return result


def base_table_options(**overrides) -> dict:
    defaults = {
        "layout": "fitColumns",
        "height": "360px",
        "index": "record_id",
        "placeholder": "No records match the current filters.",
        "pagination": True,
        "paginationMode": "local",
        "paginationSize": 12,
        "paginationSizeSelector": [12, 25, 50, 100],
        "selectableRows": 1,
        "selectableRowsPersistence": False,
        "columnDefaults": {"resizable": True, "tooltip": True},
    }
    return merge_options(defaults, overrides)


def tree_table_options(**overrides) -> dict:
    defaults = base_table_options(
        index="node_id",
        pagination=False,
        height="390px",
        dataTree=True,
        dataTreeChildField="_children",
        dataTreeElementColumn="label",
        dataTreeStartExpanded=[True, False],
        dataTreeChildIndent=22,
        dataTreeSelectPropagate=False,
        dataTreeToggleStyle="chevron",
    )
    return merge_options(defaults, overrides)


def detail_table_options(**overrides) -> dict:
    return merge_options(base_table_options(height="300px", paginationSize=8), overrides)


def virtual_table_options(**overrides) -> dict:
    return merge_options(
        base_table_options(height="480px", paginationSize=50, paginationSizeSelector=[25, 50, 100, 250]),
        {"renderVertical": "virtual", "renderVerticalBuffer": 300},
        overrides,
    )
