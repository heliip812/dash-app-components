"""UI-only Component Gallery callbacks."""

from dash import Input, Output, ctx


def register(app) -> None:
    @app.callback(
        Output("gallery-modal", "hidden"),
        Input("gallery-open-modal", "n_clicks"),
        Input("gallery-close-modal", "n_clicks"),
        Input("gallery-close-modal-footer", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_modal(_open, _close, _footer):
        return ctx.triggered_id != "gallery-open-modal"
