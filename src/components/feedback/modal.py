"""Reusable modal shell; visibility is controlled by lightweight UI state."""

from dash import html
from src.components.controls.buttons import button, icon_button


def modal(element_id: str, title: str, body, *, close_id: str, hidden: bool = True):
    return html.Div(
        id=element_id,
        className="modal",
        hidden=hidden,
        role="dialog",
        **{"aria-modal": "true", "aria-labelledby": f"{element_id}-title"},
        children=[
            html.Div(className="modal__backdrop"),
            html.Div(
                [
                    html.Div([html.H2(title, id=f"{element_id}-title"), icon_button("×", element_id=close_id, label="Close modal")], className="modal__header"),
                    html.Div(body, className="modal__body"),
                    html.Div([button("Close", element_id=f"{close_id}-footer", variant="secondary")], className="modal__footer"),
                ],
                className="modal__dialog",
            ),
        ],
    )
