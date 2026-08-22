"""Pivot Lab callback orchestration."""

from dash import Input, Output

from src.figures import build_bar_figure, build_heatmap_figure
from src.services import PivotRequest
from src.utils.ids import table_config_id


def _figure(result, mode: str):
    if mode == "bar":
        table = result.table.copy()
        table["row_label"] = table.loc[:, list(result.row_fields)].astype(str).agg(" / ".join, axis=1)
        value_columns = [column for column in table.columns if column not in {*result.row_fields, "row_label"}]
        long = table.melt(id_vars=["row_label"], value_vars=value_columns, var_name="series", value_name="value")
        return build_bar_figure(long, x="row_label", y="value", color="series", height=390)
    return build_heatmap_figure(result.matrix, row_labels=result.matrix.index.astype(str).tolist(), height=390)


def register(app, pivots, tables) -> None:
    @app.callback(
        Output(table_config_id("pivot-table"), "data"),
        Output("pivot-chart", "figure"),
        Output("pivot-summary", "children"),
        Input("pivot-rows", "value"),
        Input("pivot-columns", "value"),
        Input("pivot-value", "value"),
        Input("pivot-aggregation", "value"),
        Input("pivot-chart-mode", "value"),
    )
    def update_pivot(rows, columns, value, aggregation, mode):
        rows = list(rows or ["category"])
        columns = [column for column in (columns or []) if column not in rows]
        result = pivots.run(PivotRequest("sample", tuple(rows), tuple(columns), value or "value", aggregation or "sum"))
        summary = f"{' / '.join(rows)} × {(' / '.join(columns) if columns else 'no column dimension')} · {aggregation}({value}) · {len(result.table):,} rows"
        return tables.pivot_config("pivot-table", result.table, result.row_fields), _figure(result, mode), summary
