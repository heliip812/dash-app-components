"""Generate the deterministic Parquet demonstration dataset."""

from src.data.sample_data import ensure_sample_parquet
from src.utils.paths import SAMPLE_PARQUET_PATH


if __name__ == "__main__":
    print(ensure_sample_parquet(SAMPLE_PARQUET_PATH))
