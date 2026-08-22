"""Repository path definitions."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample"
SAMPLE_PARQUET_PATH = SAMPLE_DATA_DIR / "sample_records.parquet"
