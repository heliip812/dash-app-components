import pandas as pd
import pytest

from src.data.loaders import load_csv, load_dataframe, load_parquet


def test_csv_loader_round_trip(tmp_path, sample_frame):
    path = tmp_path / "sample.csv"
    sample_frame.to_csv(path, index=False)
    loaded = load_csv(path, parse_dates=["date"])
    pd.testing.assert_frame_equal(loaded, sample_frame)


def test_parquet_loader_round_trip_and_column_projection(tmp_path, sample_frame):
    path = tmp_path / "sample.parquet"
    sample_frame.to_parquet(path, index=False)
    loaded = load_parquet(path, columns=["record_id", "value"])
    pd.testing.assert_frame_equal(loaded, sample_frame[["record_id", "value"]])
    pd.testing.assert_frame_equal(load_dataframe(path), sample_frame)


def test_dispatch_loader_rejects_unknown_format(tmp_path):
    with pytest.raises(ValueError, match="Unsupported"):
        load_dataframe(tmp_path / "sample.json")
