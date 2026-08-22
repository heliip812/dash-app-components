"""Presentation-neutral table configuration helpers."""

import json
from typing import Any
import pandas as pd


def dataframe_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Return browser-safe records, including ISO dates and Python scalars."""
    if frame.empty:
        return []
    return json.loads(frame.to_json(orient="records", date_format="iso", date_unit="ms"))


def table_config(
    table_id: str,
    data: list[dict],
    columns: list[dict],
    options: dict,
) -> dict:
    return {"hostId": table_id, "data": data, "columns": columns, "options": options}
