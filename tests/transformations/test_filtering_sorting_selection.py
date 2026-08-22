import pytest

from src.transformations import filter_dataframe, select_columns, sort_dataframe


def test_filter_dataframe_composes_operators(sample_frame):
    result = filter_dataframe(
        sample_frame,
        [
            {"field": "category", "operator": "eq", "value": "B"},
            {"field": "value", "operator": "gte", "value": 40},
        ],
    )
    assert result["record_id"].tolist() == ["R4", "R5"]
    assert filter_dataframe(sample_frame, [{"field": "record_id", "operator": "contains", "value": "r1"}])["record_id"].tolist() == ["R1"]
    assert len(filter_dataframe(sample_frame, [{"field": "region", "operator": "in", "value": ["South"]}])) == 2
    assert len(filter_dataframe(sample_frame, [{"field": "quantity", "operator": "between", "value": [2, 4]}])) == 3


def test_filter_rejects_unknown_operator(sample_frame):
    with pytest.raises(ValueError, match="Unsupported"):
        filter_dataframe(sample_frame, [{"field": "value", "operator": "near", "value": 10}])


def test_sort_and_select_are_stable_and_explicit(sample_frame):
    result = sort_dataframe(sample_frame, ["category", "value"], [True, False])
    assert result["record_id"].tolist() == ["R2", "R1", "R5", "R4", "R3"]
    assert select_columns(result, ["record_id", "value"]).columns.tolist() == ["record_id", "value"]
