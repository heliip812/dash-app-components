"""Metric-card primitive."""

from dash import html


def metric_card(label: str, value, *, value_id: str | None = None, helper: str | None = None, tone: str = "neutral"):
    value_props = {"id": value_id} if value_id else {}
    return html.Article(
        className=f"metric-card metric-card--{tone}",
        children=[
            html.Span(label, className="metric-card__label"),
            html.Strong(value, className="metric-card__value", **value_props),
            html.Small(helper or "", className="metric-card__helper"),
        ],
    )
