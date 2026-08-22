"""Application top bar."""

from dash import html
from src.components.controls.buttons import icon_button


def topbar():
    return html.Header(
        className="topbar",
        children=[
            html.Div(
                [
                    icon_button("☰", element_id="sidebar-toggle", label="Toggle sidebar"),
                    html.Div(
                        [html.Span("Workspace", id="current-view-eyebrow", className="topbar__eyebrow"), html.Strong("Overview", id="current-view-title")],
                        className="topbar__title",
                    ),
                ],
                className="topbar__leading",
            ),
            html.Div(
                [
                    html.Span([html.Span(className="status-dot"), "75k rows ready"], className="system-status"),
                    icon_button("◐", element_id="theme-toggle", label="Toggle colour theme"),
                ],
                className="topbar__actions",
            ),
        ],
    )
