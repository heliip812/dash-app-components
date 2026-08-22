from src.data.registry import DataFrameRegistry
from src.services import DataFrameService, PivotRequest, PivotService, TableService


def test_dataframe_and_pivot_services_orchestrate(sample_frame):
    registry = DataFrameRegistry()
    registry.register("sample", sample_frame)
    dataframes = DataFrameService(registry)
    result = dataframes.table_slice(
        "sample",
        filters=[{"field": "category", "operator": "eq", "value": "B"}],
        columns=["record_id", "value"],
        limit=2,
    )
    assert result.filtered_rows == 3
    assert len(result.frame) == 2

    pivot = PivotService(dataframes).run(PivotRequest("sample", ("category",), ("region",), "value", "sum"))
    assert pivot.table.shape == (2, 3)
    assert pivot.matrix.shape == (2, 2)


def test_table_service_caps_presentation_to_structured_payload(sample_frame):
    config = TableService().standard_config("example", sample_frame)
    assert config["hostId"] == "example"
    assert len(config["data"]) == 5
    assert config["options"]["pagination"] is True
