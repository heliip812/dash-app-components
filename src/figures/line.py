"""Generic line-figure builder."""

import pandas as pd
from plotly import graph_objects as go

from .base import PALETTE, apply_base_layout, empty_figure
from .formatting import human_label


def build_line_figure(frame: pd.DataFrame, *, x: str, y: str, color: str | None = None, height: int = 320) -> go.Figure:
    if frame.empty:
        return empty_figure(height=height)
    figure = go.Figure()
    groups = frame.groupby(color, observed=True, sort=True) if color else [(human_label(y), frame)]
    for index, (name, group) in enumerate(groups):
        figure.add_trace(
            go.Scatter(
                x=group[x],
                y=group[y],
                name=str(name),
                mode="lines+markers",
                line={"color": PALETTE[index % len(PALETTE)], "width": 2.4},
                marker={"size": 5},
                hovertemplate=f"%{{x}}<br>{human_label(y)}: <b>%{{y:,.2f}}</b><extra>{name}</extra>",
            )
        )
    figure.update_layout(hovermode="x unified")
    return apply_base_layout(figure, height=height, legend=bool(color))
