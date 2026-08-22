"""Callbacks that change UI state only; layouts stay mounted."""

from dash import Input, Output, State, ctx

from .config import DEFAULT_VIEW, NAV_ITEMS, VIEW_KEYS
from src.utils.ids import nav_id, view_id


def navigation_state(triggered_id: str | None, current: str | None) -> str:
    if triggered_id and triggered_id.startswith("nav-"):
        candidate = triggered_id.removeprefix("nav-")
        if candidate in VIEW_KEYS:
            return candidate
    return current if current in VIEW_KEYS else DEFAULT_VIEW


def register(app) -> None:
    outputs = [Output("active-view", "data"), Output("current-view-title", "children"), Output("current-view-eyebrow", "children")]
    outputs += [Output(view_id(item.key), "className") for item in NAV_ITEMS]
    outputs += [Output(nav_id(item.key), "className") for item in NAV_ITEMS]
    inputs = [Input(nav_id(item.key), "n_clicks") for item in NAV_ITEMS]

    @app.callback(*outputs, *inputs, State("active-view", "data"))
    def switch_view(*args):
        current = args[-1]
        active = navigation_state(ctx.triggered_id, current)
        item = next(item for item in NAV_ITEMS if item.key == active)
        view_classes = ["app-view app-view--active" if candidate.key == active else "app-view" for candidate in NAV_ITEMS]
        nav_classes = ["nav-item nav-item--active" if candidate.key == active else "nav-item" for candidate in NAV_ITEMS]
        return active, item.label, item.eyebrow, *view_classes, *nav_classes
