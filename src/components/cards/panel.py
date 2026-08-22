"""Content panel and section-heading primitives."""

from dash import html


def section_heading(title: str, description: str | None = None, actions=None):
    return html.Div(
        className="section-heading",
        children=[
            html.Div([html.H2(title), html.P(description) if description else None]),
            html.Div(actions or [], className="section-heading__actions"),
        ],
    )


def panel(title: str, body, *, description: str | None = None, actions=None, class_name: str = ""):
    return html.Section(
        className=f"panel {class_name}".strip(),
        children=[section_heading(title, description, actions), html.Div(body, className="panel__body")],
    )
