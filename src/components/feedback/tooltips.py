"""CSS-driven tooltip primitive."""

from dash import html


def tooltip(label: str, tip: str):
    return html.Span([label, html.Span(tip, className="tooltip__content", role="tooltip")], className="tooltip", tabIndex=0)
