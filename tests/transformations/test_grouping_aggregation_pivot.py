from src.transformations import aggregate_dataframe, group_dataframe, pivot_dataframe


def test_group_dataframe(sample_frame):
    grouped = group_dataframe(sample_frame, ["category"], {"value": "sum", "quantity": "mean"})
    assert grouped.set_index("category").loc["A", "value"] == 30
    assert grouped.set_index("category").loc["B", "quantity"] == 4


def test_aggregate_dataframe(sample_frame):
    result = aggregate_dataframe(sample_frame, {"value": "sum", "quantity": "max"})
    assert result.to_dict("records") == [{"value_sum": 150.0, "quantity_max": 5}]


def test_pivot_dataframe_supports_required_aggregations(sample_frame):
    for aggregation in ("sum", "mean", "count", "min", "max"):
        pivot = pivot_dataframe(sample_frame, rows=["category"], columns=["region"], values="value", aggregation=aggregation)
        assert pivot.columns.tolist() == ["category", "North", "South"]
        assert len(pivot) == 2
