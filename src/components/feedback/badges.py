"""Badge primitives."""

from dash import html


def badge(label: str, tone: str = "neutral"):
    return html.Span(label, className=f"badge badge--{tone}")


def status_badge(status: str):
    tone = {"Active": "positive", "Complete": "positive", "Pending": "warning", "Review": "info", "Paused": "danger"}.get(status, "neutral")
    return badge(status, tone)
