"""Thin Dash wrapper around the MIT-licensed Tabulator JavaScript library."""

from dash import dcc, html

from src.utils.ids import table_config_id, table_selection_id
from .base_table import table_config


def tabulator_table(
    table_id: str,
    *,
    data: list[dict],
    columns: list[dict],
    options: dict,
    class_name: str = "",
    aria_label: str = "Interactive data table",
):
    config_id = table_config_id(table_id)
    selection_id = table_selection_id(table_id)
    return html.Div(
        className=f"table-component {class_name}".strip(),
        children=[
            dcc.Store(id=config_id, data=table_config(table_id, data, columns, options)),
            dcc.Store(id=selection_id, data=[]),
            html.Div(
                id=table_id,
                className="tabulator-host",
                title="Interactive data table",
                **{
                    "data-config-id": config_id,
                    "data-selection-id": selection_id,
                    "role": "region",
                    "aria-label": aria_label,
                },
            ),
        ],
    )
