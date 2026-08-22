"""Shared Plotly layout and empty-figure behaviour."""

from plotly import graph_objects as go


PALETTE = ["#6d5dfc", "#16a085", "#f0a93d", "#d65b73", "#3f8fd2", "#8c63d8"]


def apply_base_layout(figure: go.Figure, *, height: int = 320, legend: bool = False) -> go.Figure:
    figure.update_layout(
        height=height,
        margin={"l": 28, "r": 18, "t": 24, "b": 36},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, ui-sans-serif, system-ui", "color": "#687286", "size": 12},
        colorway=PALETTE,
        showlegend=legend,
        hoverlabel={"bgcolor": "#171a2b", "font_color": "#ffffff", "bordercolor": "#171a2b"},
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="rgba(120, 130, 160, 0.16)", zeroline=False)
    return figure


def empty_figure(message: str = "No data for the current filters", *, height: int = 320) -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    figure.update_xaxes(visible=False)
    figure.update_yaxes(visible=False)
    return apply_base_layout(figure, height=height)
