import pandas as pd
import pytest


@pytest.fixture
def sample_frame():
    return pd.DataFrame(
        {
            "record_id": ["R1", "R2", "R3", "R4", "R5"],
            "category": ["A", "A", "B", "B", "B"],
            "subcategory": ["X", "Y", "X", "X", "Y"],
            "region": ["North", "South", "North", "South", "North"],
            "product": ["P1", "P1", "P2", "P2", "P3"],
            "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]),
            "value": [10.0, 20.0, 30.0, 40.0, 50.0],
            "quantity": [1, 2, 3, 4, 5],
            "percentage": [0.1, 0.2, 0.3, 0.4, 0.5],
            "status": ["Active", "Pending", "Active", "Review", "Paused"],
        }
    )
