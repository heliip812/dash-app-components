"""Generic scatter-figure builder."""

import pandas as pd
from plotly import graph_objects as go

from .base import PALETTE, apply_base_layout, empty_figure
from .formatting import human_label


def build_scatter_figure(
    frame: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str | None = None,
    size: str | None = None,
    hover_name: str | None = None,
    height: int = 320,
) -> go.Figure:
    if frame.empty:
        return empty_figure(height=height)
    figure = go.Figure()
    groups = frame.groupby(color, observed=True, sort=True) if color else [(human_label(y), frame)]
    size_values = frame[size].clip(lower=1) if size else None
    size_reference = (2.0 * float(size_values.max()) / 34**2) if size is not None and float(size_values.max()) else 1
    for index, (name, group) in enumerate(groups):
        marker = {"color": PALETTE[index % len(PALETTE)], "opacity": 0.76, "line": {"color": "white", "width": 1}}
        if size:
            marker.update({"size": group[size].clip(lower=1), "sizemode": "area", "sizeref": size_reference, "sizemin": 5})
        customdata = group[hover_name] if hover_name else None
        figure.add_trace(
            go.Scatter(
                x=group[x],
                y=group[y],
                name=str(name),
                mode="markers",
                marker=marker,
                customdata=customdata,
                hovertemplate=("<b>%{customdata}</b><br>" if hover_name else "")
                + f"{human_label(x)}: %{{x:,.2f}}<br>{human_label(y)}: %{{y:,.2f}}<extra>{name}</extra>",
            )
        )
    return apply_base_layout(figure, height=height, legend=bool(color))
