"""Generic bar-figure builder."""

import pandas as pd
from plotly import graph_objects as go

from .base import PALETTE, apply_base_layout, empty_figure
from .formatting import human_label


def build_bar_figure(
    frame: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str | None = None,
    orientation: str = "v",
    height: int = 320,
) -> go.Figure:
    if frame.empty:
        return empty_figure(height=height)
    figure = go.Figure()
    groups = frame.groupby(color, observed=True, sort=True) if color else [(human_label(y), frame)]
    for index, (name, group) in enumerate(groups):
        horizontal = orientation == "h"
        figure.add_trace(
            go.Bar(
                x=group[y] if horizontal else group[x],
                y=group[x] if horizontal else group[y],
                name=str(name),
                orientation=orientation,
                marker={"color": PALETTE[index % len(PALETTE)], "line": {"width": 0}},
                hovertemplate="%{y}: <b>%{x:,.2f}</b><extra></extra>" if horizontal else "%{x}: <b>%{y:,.2f}</b><extra></extra>",
            )
        )
    figure.update_layout(bargap=0.32, barmode="group")
    return apply_base_layout(figure, height=height, legend=bool(color))
