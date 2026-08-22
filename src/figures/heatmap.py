"""Generic heatmap builder from a matrix-like DataFrame."""

import pandas as pd
from plotly import graph_objects as go

from .base import apply_base_layout, empty_figure


def build_heatmap_figure(
    matrix: pd.DataFrame,
    *,
    row_labels: list | None = None,
    column_labels: list | None = None,
    height: int = 340,
) -> go.Figure:
    if matrix.empty or matrix.shape[1] == 0:
        return empty_figure(height=height)
    numeric = matrix.apply(pd.to_numeric, errors="coerce").fillna(0)
    figure = go.Figure(
        go.Heatmap(
            z=numeric.to_numpy(),
            x=column_labels or [str(column) for column in numeric.columns],
            y=row_labels or [str(index) for index in numeric.index],
            colorscale=[[0, "#f3f1ff"], [0.5, "#9c91ff"], [1, "#5644e8"]],
            hovertemplate="%{y} · %{x}<br><b>%{z:,.2f}</b><extra></extra>",
            colorbar={"thickness": 10, "outlinewidth": 0},
        )
    )
    return apply_base_layout(figure, height=height)
