"""Thin overview callbacks."""

from dash import Input, Output

from src.components.tables.base_table import dataframe_records, table_config
from src.components.tables.column_builders import date_column, numeric_column, status_column, text_column
from src.components.tables.table_options import base_table_options
from src.figures import build_bar_figure, build_line_figure
from src.transformations import group_dataframe
from src.utils.formatting import format_number, format_percentage
from src.utils.ids import table_config_id


def _filters(region, category):
    items = []
    if region and region != "all":
        items.append({"field": "region", "operator": "eq", "value": region})
    if category and category != "all":
        items.append({"field": "category", "operator": "eq", "value": category})
    return items


def register(app, dataframes) -> None:
    @app.callback(
        Output("overview-total-records", "children"),
        Output("overview-active-categories", "children"),
        Output("overview-average-value", "children"),
        Output("overview-average-percentage", "children"),
        Output("overview-main-chart", "figure"),
        Output("overview-secondary-chart", "figure"),
        Output(table_config_id("overview-activity-table"), "data"),
        Input("overview-region", "value"),
        Input("overview-category", "value"),
    )
    def update_overview(region, category):
        frame = dataframes.filtered("sample", _filters(region, category))
        working = frame.assign(month=frame["date"].dt.to_period("M").dt.to_timestamp())
        by_date = working.groupby("month", as_index=False, observed=True)["value"].sum()
        by_category = group_dataframe(frame, ["category"], {"value": "sum"}).sort_values("value", ascending=False)
        recent = frame.sort_values("date", ascending=False).head(10)
        columns = [text_column("Record", "record_id", frozen=True), text_column("Category", "category"), date_column("Date", "date"), numeric_column("Value", "value"), status_column()]
        config = table_config(
            "overview-activity-table",
            dataframe_records(recent.loc[:, ["record_id", "category", "date", "value", "status"]]),
            columns,
            base_table_options(height="300px", pagination=False, selectableRows=False),
        )
        return (
            format_number(len(frame)),
            str(frame["category"].nunique()),
            format_number(frame["value"].mean(), 2) if not frame.empty else "—",
            format_percentage(frame["percentage"].mean()) if not frame.empty else "—",
            build_line_figure(by_date, x="month", y="value", height=340),
            build_bar_figure(by_category, x="category", y="value", height=340),
            config,
        )
