"""Thin cross-filter callback for the figure gallery."""

from dash import Input, Output


def register(app, dataframes, visualisations) -> None:
    @app.callback(
        Output("viz-line", "figure"),
        Output("viz-bar", "figure"),
        Output("viz-scatter", "figure"),
        Output("viz-heatmap", "figure"),
        Output("viz-row-count", "children"),
        Input("viz-category", "value"),
        Input("viz-region", "value"),
    )
    def update_visualisations(category, region):
        filters = []
        if category and category != "all":
            filters.append({"field": "category", "operator": "eq", "value": category})
        if region and region != "all":
            filters.append({"field": "region", "operator": "eq", "value": region})
        frame = dataframes.filtered("sample", filters)
        return (
            visualisations.time_series(frame),
            visualisations.category_bar(frame, dimension="region"),
            visualisations.scatter(frame),
            visualisations.heatmap(frame),
            f"{len(frame):,}",
        )
