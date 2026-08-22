"""Sandbox for standard, hierarchy, detail, and large-table patterns."""

from dash import html

from src.components.cards import panel
from src.components.charts import graph_container
from src.components.controls import dropdown, search_input
from src.components.feedback import badge
from src.components.tables.base_table import dataframe_records
from src.components.tables.hierarchy_table import hierarchy_table
from src.components.tables.tabulator_table import tabulator_table
from src.components.tables.table_options import base_table_options, virtual_table_options
from src.figures.base import empty_figure
from src.transformations import build_hierarchy
from src.utils.ids import view_id
from .config import STANDARD_COLUMNS, VIEW_KEY


def layout(dataframes, tables):
    source = dataframes.get("sample")
    standard = source.loc[:, list(STANDARD_COLUMNS)].head(180)
    hierarchy = build_hierarchy(
        source,
        levels=["category", "subcategory", "product"],
        aggregations={"value": "sum", "quantity": "sum"},
    )
    large_slice = dataframes.table_slice("sample", columns=STANDARD_COLUMNS, sort_by="date", ascending=False, limit=2_500)
    return html.Section(
        id=view_id(VIEW_KEY),
        className="app-view",
        children=[
            html.Div(
                [
                    html.Div([html.Span("Interactive table patterns", className="eyebrow"), html.H1("Table Lab"), html.P("Reusable Tabulator configurations with selection, hierarchy, detail, and virtual rendering.")]),
                    html.Div(
                        [
                            dropdown("table-category-filter", "Category", [{"label": "All categories", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "category")], "all"),
                            dropdown("table-status-filter", "Status", [{"label": "All statuses", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "status")], "all"),
                        ],
                        className="filter-toolbar",
                    ),
                ],
                className="view-header",
            ),
            panel(
                "Standard table",
                [
                    html.Div([badge("sorting"), badge("header filters"), badge("resizing"), badge("frozen ID"), badge("selection"), html.Span("180 rows", id="standard-table-count", className="table-count")], className="capability-row"),
                    tabulator_table(
                        "standard-table",
                        data=dataframe_records(standard),
                        columns=tables.standard_columns(),
                        options=base_table_options(height="420px", paginationSize=12),
                    ),
                ],
                description="Client-side presentation remains generic; server-side callbacks only send a capped result.",
            ),
            html.Div(
                [
                    panel(
                        "Expandable hierarchy",
                        hierarchy_table("hierarchy-table", hierarchy=hierarchy, columns=tables.hierarchy_columns()),
                        description="Category → subcategory → product using native Tabulator Data Tree and _children records.",
                    ),
                    panel(
                        "Selection detail",
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div([html.Span("Record"), html.Strong("Select a row", id="detail-record-id")], className="definition-row"),
                                        html.Div([html.Span("Category"), html.Strong("—", id="detail-category")], className="definition-row"),
                                        html.Div([html.Span("Region"), html.Strong("—", id="detail-region")], className="definition-row"),
                                        html.Div([html.Span("Status"), html.Strong("—", id="detail-status")], className="definition-row"),
                                        html.Div([html.Span("Value"), html.Strong("—", id="detail-value")], className="definition-row"),
                                    ],
                                    className="definition-list",
                                ),
                                graph_container("detail-related-chart", empty_figure("Select a standard-table row", height=260)),
                                html.H3("Related records", className="subsection-title"),
                                tabulator_table(
                                    "detail-related-table",
                                    data=[],
                                    columns=tables.standard_columns(),
                                    options=base_table_options(height="245px", paginationSize=5, selectableRows=False),
                                ),
                            ],
                            className="detail-panel",
                        ),
                        description="Tabulator selection → lightweight dcc.Store → Python service → chart and metadata.",
                    ),
                ],
                className="dashboard-grid dashboard-grid--equal",
            ),
            panel(
                "Large static dataset",
                [
                    html.Div(
                        [
                            search_input("large-table-search", placeholder="Search record ID…"),
                            dropdown("large-table-region", "Region", [{"label": "All regions", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "region")], "all"),
                            html.Span(f"Showing 2,500 of {large_slice.total_rows:,}", id="large-table-count", className="table-count"),
                        ],
                        className="filter-toolbar filter-toolbar--inline",
                    ),
                    tabulator_table(
                        "large-table",
                        data=dataframe_records(large_slice.frame),
                        columns=tables.standard_columns(),
                        options=virtual_table_options(),
                    ),
                ],
                description="The registry holds 75,000 rows; server filters first and transfers at most 2,500 rows.",
            ),
        ],
    )
