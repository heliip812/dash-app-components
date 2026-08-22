"""Build structured Tabulator payloads without defining Dash layout."""

import pandas as pd

from src.components.tables.base_table import dataframe_records, table_config
from src.components.tables.column_builders import (
    date_column,
    expandable_column,
    integer_column,
    numeric_column,
    percentage_column,
    status_column,
    text_column,
)
from src.components.tables.table_options import base_table_options, tree_table_options, virtual_table_options


class TableService:
    @staticmethod
    def standard_columns() -> list[dict]:
        return [
            text_column("Record", "record_id", frozen=True, minWidth=132),
            text_column("Category", "category"),
            text_column("Region", "region"),
            text_column("Product", "product", minWidth=130),
            date_column("Date", "date", minWidth=116),
            numeric_column("Value", "value"),
            integer_column("Quantity", "quantity"),
            percentage_column("Percentage", "percentage"),
            status_column(),
        ]

    @staticmethod
    def hierarchy_columns() -> list[dict]:
        return [
            expandable_column("Hierarchy", "label"),
            integer_column("Records", "record_count"),
            numeric_column("Value", "value"),
            integer_column("Quantity", "quantity"),
        ]

    def standard_config(self, table_id: str, frame: pd.DataFrame, *, page_size: int = 12) -> dict:
        return table_config(
            table_id,
            dataframe_records(frame),
            self.standard_columns(),
            base_table_options(paginationSize=page_size),
        )

    def virtual_config(self, table_id: str, frame: pd.DataFrame) -> dict:
        return table_config(table_id, dataframe_records(frame), self.standard_columns(), virtual_table_options())

    def hierarchy_config(self, table_id: str, hierarchy: list[dict]) -> dict:
        return table_config(table_id, hierarchy, self.hierarchy_columns(), tree_table_options())

    def pivot_config(self, table_id: str, frame: pd.DataFrame, row_fields: tuple[str, ...]) -> dict:
        columns: list[dict] = []
        for column in frame.columns:
            if column in row_fields:
                columns.append(text_column(column.replace("_", " ").title(), column, frozen=not columns, minWidth=140))
            else:
                columns.append(numeric_column(str(column), str(column), decimals=2, minWidth=120))
        options = base_table_options(index=row_fields[0], height="350px", paginationSize=15, selectableRows=False)
        return table_config(table_id, dataframe_records(frame), columns, options)
