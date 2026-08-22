"""Deterministic, domain-neutral sample-data generation."""

from pathlib import Path
import numpy as np
import pandas as pd


CATEGORIES = ("Alpha", "Beta", "Gamma", "Delta")
SUBCATEGORIES = ("Core", "Growth", "Support")
REGIONS = ("North", "South", "East", "West")
PRODUCTS = ("Product A", "Product B", "Product C", "Product D", "Product E")
STATUSES = ("Active", "Pending", "Review", "Paused")


def generate_sample_dataframe(rows: int = 75_000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, rows), unit="D")
    frame = pd.DataFrame(
        {
            "record_id": [f"REC-{index:07d}" for index in range(1, rows + 1)],
            "category": rng.choice(CATEGORIES, rows),
            "subcategory": rng.choice(SUBCATEGORIES, rows),
            "region": rng.choice(REGIONS, rows),
            "product": rng.choice(PRODUCTS, rows),
            "date": dates,
            "value": np.round(rng.gamma(5.5, 220.0, rows), 2),
            "quantity": rng.integers(1, 250, rows),
            "percentage": np.clip(rng.normal(0.52, 0.18, rows), -0.15, 1.25),
            "status": rng.choice(STATUSES, rows, p=(0.58, 0.20, 0.14, 0.08)),
        }
    )
    for column in ("category", "subcategory", "region", "product", "status"):
        frame[column] = frame[column].astype("category")
    return frame.sort_values("date", kind="stable").reset_index(drop=True)


def ensure_sample_parquet(path: str | Path, rows: int = 75_000) -> Path:
    target = Path(path)
    if target.exists():
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    generate_sample_dataframe(rows=rows).to_parquet(target, index=False, compression="snappy")
    return target
