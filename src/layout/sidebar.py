"""Sidebar for state-based, same-URL navigation."""

from dash import html

from src.navigation.config import NAV_ITEMS
from src.utils.ids import nav_id


def sidebar():
    return html.Aside(
        id="app-sidebar",
        className="sidebar",
        children=[
            html.Div(
                [html.Span("D", className="brand__mark"), html.Div([html.Strong("Dashwork"), html.Small("Component foundation")])],
                className="brand",
            ),
            html.Nav(
                [
                    html.Button(
                        [html.Span(item.icon, className="nav-item__icon"), html.Span(item.label)],
                        id=nav_id(item.key),
                        className="nav-item nav-item--active" if index == 0 else "nav-item",
                        n_clicks=0,
                    )
                    for index, item in enumerate(NAV_ITEMS)
                ],
                className="sidebar__nav",
                **{"aria-label": "Workspace views"},
            ),
            html.Div(
                [
                    html.Span("LOCAL WORKSPACE", className="sidebar-note__label"),
                    html.Strong("Server-side data"),
                    html.P("Large frames stay in Python. Only compact results reach the browser."),
                ],
                className="sidebar-note",
            ),
            html.Div(
                [html.Span("OS", className="avatar"), html.Div([html.Strong("Open source"), html.Small("No enterprise grids")])],
                className="sidebar__footer",
            ),
        ],
    )
