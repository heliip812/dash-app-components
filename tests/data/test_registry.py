import pytest

from src.data.registry import DataFrameRegistry


def test_registry_returns_same_server_side_object(sample_frame):
    registry = DataFrameRegistry()
    metadata = registry.register("sample", sample_frame, source="memory")
    assert registry.get("sample") is sample_frame
    assert registry.get("sample") is registry.get("sample")
    assert metadata.rows == 5
    assert metadata.source == "memory"
    assert registry.contains("sample")


def test_registry_prevents_accidental_replacement(sample_frame):
    registry = DataFrameRegistry()
    registry.register("sample", sample_frame)
    with pytest.raises(KeyError, match="already registered"):
        registry.register("sample", sample_frame)
    registry.register("sample", sample_frame.head(1), replace=True)
    assert len(registry.get("sample")) == 1


def test_registry_unknown_dataset(sample_frame):
    registry = DataFrameRegistry()
    with pytest.raises(KeyError, match="Unknown dataset"):
        registry.get("missing")
