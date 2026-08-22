"""Labelled Dash dropdown primitive."""

from dash import dcc, html


def dropdown(element_id: str, label: str, options, value=None, *, multi: bool = False, clearable: bool = False, class_name: str = ""):
    return html.Label(
        className=f"field {class_name}".strip(),
        children=[
            html.Span(label, className="field__label"),
            dcc.Dropdown(id=element_id, options=options, value=value, multi=multi, clearable=clearable, className="dropdown"),
        ],
    )
