"""Python/pandas pivot laboratory."""

from dash import dcc, html

from src.components.cards import panel
from src.components.charts import graph_container
from src.components.controls import dropdown
from src.components.tables.tabulator_table import tabulator_table
from src.figures import build_heatmap_figure
from src.services import PivotRequest
from src.utils.ids import view_id
from .config import AGGREGATIONS, DIMENSIONS, VALUES, VIEW_KEY


def _options(values):
    return [{"label": value.replace("_", " ").title(), "value": value} for value in values]


def layout(pivots, tables):
    initial = pivots.run(PivotRequest("sample", ("category",), ("region",), "value", "sum"))
    initial_table = tables.pivot_config("pivot-table", initial.table, initial.row_fields)
    return html.Section(
        id=view_id(VIEW_KEY),
        className="app-view",
        children=[
            html.Div(
                [
                    html.Div([html.Span("Reusable pandas workflow", className="eyebrow"), html.H1("Pivot Lab"), html.P("Define dimensions and measures once; reuse the structured result in tables and figures.")]),
                    html.Div(
                        [
                            dropdown("pivot-rows", "Rows", _options(DIMENSIONS), ["category"], multi=True),
                            dropdown("pivot-columns", "Columns", _options(DIMENSIONS), ["region"], multi=True),
                            dropdown("pivot-value", "Value", _options(VALUES), "value"),
                            dropdown("pivot-aggregation", "Aggregation", _options(AGGREGATIONS), "sum"),
                        ],
                        className="filter-toolbar pivot-controls",
                    ),
                ],
                className="view-header",
            ),
            html.Div(
                [
                    html.Span("category × region · sum(value)", id="pivot-summary", className="result-summary"),
                    dcc.RadioItems(
                        id="pivot-chart-mode",
                        options=[{"label": "Heatmap", "value": "heatmap"}, {"label": "Bars", "value": "bar"}],
                        value="heatmap",
                        inline=True,
                        className="segmented-control",
                    ),
                ],
                className="context-bar",
            ),
            html.Div(
                [
                    panel(
                        "Pivot result",
                        tabulator_table(
                            "pivot-table",
                            data=initial_table["data"],
                            columns=initial_table["columns"],
                            options=initial_table["options"],
                        ),
                        description="All aggregation is performed in pandas, with compact output sent to Tabulator.",
                    ),
                    panel(
                        "Pivot visualisation",
                        graph_container("pivot-chart", build_heatmap_figure(initial.matrix, row_labels=initial.matrix.index.astype(str).tolist(), height=390)),
                        description="The same result drives the table and the selected Plotly representation.",
                    ),
                ],
                className="dashboard-grid dashboard-grid--equal",
            ),
        ],
    )
