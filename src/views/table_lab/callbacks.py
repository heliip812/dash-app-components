"""Thin callbacks for Table Lab workflows."""

from dash import Input, Output

from src.components.tables.base_table import dataframe_records
from src.components.tables.table_options import base_table_options
from src.utils.formatting import format_number
from src.utils.ids import table_config_id, table_selection_id
from .config import STANDARD_COLUMNS


def _optional_filter(field, value):
    return [] if not value or value == "all" else [{"field": field, "operator": "eq", "value": value}]


def register(app, dataframes, tables, visualisations) -> None:
    @app.callback(
        Output(table_config_id("standard-table"), "data"),
        Output("standard-table-count", "children"),
        Input("table-category-filter", "value"),
        Input("table-status-filter", "value"),
    )
    def update_standard(category, status):
        filters = _optional_filter("category", category) + _optional_filter("status", status)
        result = dataframes.table_slice("sample", filters=filters, columns=STANDARD_COLUMNS, sort_by="date", ascending=False, limit=500)
        return tables.standard_config("standard-table", result.frame), f"{result.filtered_rows:,} matches · {len(result.frame):,} sent"

    @app.callback(
        Output("detail-record-id", "children"),
        Output("detail-category", "children"),
        Output("detail-region", "children"),
        Output("detail-status", "children"),
        Output("detail-value", "children"),
        Output("detail-related-chart", "figure"),
        Output(table_config_id("detail-related-table"), "data"),
        Input(table_selection_id("standard-table"), "data"),
    )
    def update_detail(selection):
        source = dataframes.get("sample")
        selected = selection[0] if selection else None
        if not selected:
            empty_config = tables.standard_config("detail-related-table", source.iloc[0:0].loc[:, list(STANDARD_COLUMNS)], page_size=5)
            return "Select a row", "—", "—", "—", "—", visualisations.record_context(source, None), empty_config
        record = dataframes.record("sample", selected.get("record_id")) or selected
        related = source.loc[source["category"].astype(str) == str(record.get("category"))].head(20).loc[:, list(STANDARD_COLUMNS)]
        related_config = tables.standard_config("detail-related-table", related, page_size=5)
        return (
            record.get("record_id", "—"),
            str(record.get("category", "—")),
            str(record.get("region", "—")),
            str(record.get("status", "—")),
            format_number(record.get("value"), 2),
            visualisations.record_context(source, record),
            related_config,
        )

    @app.callback(
        Output(table_config_id("large-table"), "data"),
        Output("large-table-count", "children"),
        Input("large-table-search", "value"),
        Input("large-table-region", "value"),
    )
    def update_large_table(query, region):
        filters = _optional_filter("region", region)
        if query and query.strip():
            filters.append({"field": "record_id", "operator": "contains", "value": query.strip()})
        result = dataframes.table_slice("sample", filters=filters, columns=STANDARD_COLUMNS, sort_by="date", ascending=False, limit=2_500)
        return tables.virtual_config("large-table", result.frame), f"Showing {len(result.frame):,} of {result.filtered_rows:,} matches"
