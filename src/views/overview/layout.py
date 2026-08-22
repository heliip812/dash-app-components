"""Generic overview composition."""

from dash import html

from src.components.cards import metric_card, panel
from src.components.charts import graph_container
from src.components.controls import dropdown
from src.components.tables.base_table import dataframe_records
from src.components.tables.column_builders import date_column, numeric_column, status_column, text_column
from src.components.tables.tabulator_table import tabulator_table
from src.components.tables.table_options import base_table_options
from src.figures import build_bar_figure, build_line_figure
from src.transformations import group_dataframe
from src.utils.formatting import format_number, format_percentage
from src.utils.ids import view_id
from .config import VIEW_KEY


def _initial_state(dataframes):
    frame = dataframes.get("sample")
    by_date = frame.assign(month=frame["date"].dt.to_period("M").dt.to_timestamp()).groupby("month", as_index=False, observed=True)["value"].sum()
    by_category = group_dataframe(frame, ["category"], {"value": "sum"}).sort_values("value", ascending=False)
    recent = frame.sort_values("date", ascending=False).head(10)
    return frame, by_date, by_category, recent


def layout(dataframes):
    frame, by_date, by_category, recent = _initial_state(dataframes)
    active_categories = int(frame["category"].nunique())
    latest = frame["date"].max()
    table_columns = [
        text_column("Record", "record_id", frozen=True),
        text_column("Category", "category"),
        date_column("Date", "date"),
        numeric_column("Value", "value"),
        status_column(),
    ]
    return html.Section(
        id=view_id(VIEW_KEY),
        className="app-view app-view--active",
        children=[
            html.Div(
                [
                    html.Div([html.Span("Generic analytical workspace", className="eyebrow"), html.H1("Operational overview"), html.P("A compact readout built from a registry-owned static DataFrame.")]),
                    html.Div(
                        [
                            dropdown("overview-region", "Region", [{"label": "All regions", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "region")], "all"),
                            dropdown("overview-category", "Category", [{"label": "All categories", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "category")], "all"),
                        ],
                        className="filter-toolbar",
                    ),
                ],
                className="view-header",
            ),
            html.Div(
                [
                    metric_card("Total Records", format_number(len(frame)), value_id="overview-total-records", helper="filtered rows"),
                    metric_card("Active Categories", str(active_categories), value_id="overview-active-categories", helper="distinct groups", tone="positive"),
                    metric_card("Average Value", format_number(frame["value"].mean(), 2), value_id="overview-average-value", helper="across selection", tone="info"),
                    metric_card("Average Percentage", format_percentage(frame["percentage"].mean()), value_id="overview-average-percentage", helper=f"updated {latest:%d %b %Y}", tone="warning"),
                ],
                className="metric-grid",
            ),
            html.Div(
                [
                    panel("Value over time", graph_container("overview-main-chart", build_line_figure(by_date, x="month", y="value", height=340)), description="Monthly aggregate; filter before aggregation."),
                    panel("Category mix", graph_container("overview-secondary-chart", build_bar_figure(by_category, x="category", y="value", height=340)), description="Current selection grouped in Python."),
                ],
                className="dashboard-grid dashboard-grid--2-1",
            ),
            panel(
                "Recent activity",
                tabulator_table(
                    "overview-activity-table",
                    data=dataframe_records(recent.loc[:, ["record_id", "category", "date", "value", "status"]]),
                    columns=table_columns,
                    options=base_table_options(height="300px", pagination=False, selectableRows=False),
                ),
                description="Only ten records are transferred; the source frame remains server-side.",
            ),
        ],
    )
