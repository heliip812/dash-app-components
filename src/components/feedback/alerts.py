"""Alert/callout primitive."""

from dash import html


def alert(title: str, message: str, *, tone: str = "info"):
    return html.Div([html.Strong(title), html.P(message)], className=f"alert alert--{tone}", role="status")
