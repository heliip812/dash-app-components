"""Reusable chart workflows assembled from transformations and figure builders."""

import pandas as pd

from src.figures import build_bar_figure, build_heatmap_figure, build_line_figure, build_scatter_figure
from src.transformations import group_dataframe, pivot_dataframe


class VisualisationService:
    def time_series(self, frame: pd.DataFrame, *, frequency: str = "ME"):
        # APPLICATION-SPECIFIC FUNCTION GOES HERE: add domain measures in a new
        # service method while keeping the generic figure builder unchanged.
        if frame.empty:
            return build_line_figure(frame, x="date", y="value")
        working = frame.loc[:, ["date", "value"]].copy()
        working["date"] = pd.to_datetime(working["date"]).dt.to_period(frequency[0]).dt.to_timestamp()
        grouped = working.groupby("date", observed=True, as_index=False)["value"].sum()
        return build_line_figure(grouped, x="date", y="value", height=330)

    def category_bar(self, frame: pd.DataFrame, *, dimension: str = "category", value: str = "value"):
        grouped = group_dataframe(frame, [dimension], {value: "sum"}).sort_values(value, ascending=False)
        return build_bar_figure(grouped, x=dimension, y=value, height=310)

    def scatter(self, frame: pd.DataFrame, *, limit: int = 600):
        sample = frame.iloc[:limit]
        return build_scatter_figure(
            sample,
            x="quantity",
            y="value",
            color="category",
            size="percentage",
            hover_name="record_id",
            height=330,
        )

    def heatmap(self, frame: pd.DataFrame):
        pivot = pivot_dataframe(frame, rows=["category"], columns=["region"], values="value", aggregation="mean")
        if pivot.empty:
            return build_heatmap_figure(pd.DataFrame(), height=330)
        labels = pivot["category"].astype(str).tolist()
        matrix = pivot.drop(columns=["category"])
        return build_heatmap_figure(matrix, row_labels=labels, height=330)

    def record_context(self, frame: pd.DataFrame, selected_record: dict | None):
        if not selected_record:
            return self.category_bar(frame.head(0))
        category = selected_record.get("category")
        subset = frame.loc[frame["category"].astype(str) == str(category)]
        grouped = group_dataframe(subset, ["product"], {"value": "mean"}).sort_values("value", ascending=False)
        return build_bar_figure(grouped, x="product", y="value", height=260)
