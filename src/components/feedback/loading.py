"""Static loading-state example."""

from dash import html


def loading_state(label: str = "Loading data"):
    return html.Div([html.Span(className="loading-state__spinner"), html.Span(label)], className="loading-state", role="status")
