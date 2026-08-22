"""Generic Plotly figure gallery driven by reusable builders."""

from dash import html

from src.components.cards import panel
from src.components.charts import graph_container
from src.components.controls import dropdown
from src.utils.ids import view_id
from .config import VIEW_KEY


def layout(dataframes, visualisations):
    source = dataframes.get("sample")
    return html.Section(
        id=view_id(VIEW_KEY),
        className="app-view",
        children=[
            html.Div(
                [
                    html.Div([html.Span("Plotly builder sandbox", className="eyebrow"), html.H1("Visualisation Lab"), html.P("Line, bar, scatter, and heatmap figures share one restrained visual language.")]),
                    html.Div(
                        [
                            dropdown("viz-category", "Category", [{"label": "All categories", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "category")], "all"),
                            dropdown("viz-region", "Region", [{"label": "All regions", "value": "all"}] + [{"label": value, "value": value} for value in dataframes.distinct_values("sample", "region")], "all"),
                        ],
                        className="filter-toolbar",
                    ),
                ],
                className="view-header",
            ),
            html.Div(
                [
                    panel("Line", graph_container("viz-line", visualisations.time_series(source)), description="Monthly value aggregate."),
                    panel("Bar", graph_container("viz-bar", visualisations.category_bar(source, dimension="region")), description="Value grouped by region."),
                    panel("Scatter", graph_container("viz-scatter", visualisations.scatter(source)), description="Quantity vs value, category colour, percentage size."),
                    panel("Heatmap", graph_container("viz-heatmap", visualisations.heatmap(source)), description="Mean value by category and region."),
                ],
                className="visualisation-grid",
            ),
            html.Div([html.Span("75,000", id="viz-row-count"), " filtered records drive these server-built figures."], className="inline-callout"),
        ],
    )
