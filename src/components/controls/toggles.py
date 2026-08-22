"""Toggle-switch primitive built from an accessible checklist."""

from dash import dcc, html


def toggle(element_id: str, label: str, *, value: bool = False, description: str | None = None):
    return html.Label(
        className="toggle",
        children=[
            html.Span([html.Strong(label), html.Small(description) if description else None]),
            dcc.Checklist(id=element_id, options=[{"label": "", "value": "on"}], value=["on"] if value else [], className="toggle__control"),
        ],
    )
