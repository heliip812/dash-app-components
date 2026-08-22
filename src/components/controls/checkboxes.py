"""Checkbox primitive."""

from dash import dcc, html


def checkbox(element_id: str, label: str, *, checked: bool = False):
    return html.Label(
        className="checkbox",
        children=[
            dcc.Checklist(id=element_id, options=[{"label": label, "value": "checked"}], value=["checked"] if checked else []),
        ],
    )
