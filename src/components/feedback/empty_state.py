"""Empty-state primitive."""

from dash import html
from src.components.controls.buttons import button


def empty_state(title: str, message: str, *, action_label: str = "Create item", action_id: str | None = None):
    return html.Div(
        [html.Span("◇", className="empty-state__icon"), html.H3(title), html.P(message), button(action_label, element_id=action_id)],
        className="empty-state",
    )
