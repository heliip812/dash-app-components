"""Labelled text and search input primitives."""

from dash import dcc, html


def text_input(element_id: str, label: str, *, value: str = "", placeholder: str = "", input_type: str = "text"):
    return html.Label(
        className="field",
        children=[
            html.Span(label, className="field__label"),
            dcc.Input(id=element_id, value=value, placeholder=placeholder, type=input_type, className="input"),
        ],
    )


def search_input(element_id: str, *, placeholder: str = "Search…", label: str = "Search"):
    return html.Label(
        className="search-field",
        children=[
            html.Span(label, className="sr-only"),
            html.Span("⌕", className="search-field__icon", **{"aria-hidden": "true"}),
            dcc.Input(id=element_id, type="search", placeholder=placeholder, debounce=False),
        ],
    )
