"""Native, accessible collapsible panel with no callback overhead."""

from dash import html


def collapsible_panel(title: str, body, *, open_by_default: bool = False):
    return html.Details(
        className="collapsible-panel",
        open=open_by_default,
        children=[html.Summary(title), html.Div(body, className="collapsible-panel__body")],
    )
