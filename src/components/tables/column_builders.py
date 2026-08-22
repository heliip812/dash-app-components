"""Composable Python builders for Tabulator column definitions."""


def _column(title: str, field: str, **overrides) -> dict:
    result = {"title": title, "field": field, "headerSort": True}
    result.update({key: value for key, value in overrides.items() if value is not None})
    return result


def text_column(title: str, field: str, *, header_filter: bool = True, **overrides) -> dict:
    return _column(title, field, headerFilter="input" if header_filter else None, **overrides)


def numeric_column(title: str, field: str, *, decimals: int = 2, **overrides) -> dict:
    return _column(
        title,
        field,
        sorter="number",
        hozAlign="right",
        headerHozAlign="right",
        formatter="dash:decimal",
        formatterParams={"decimals": decimals},
        **overrides,
    )


def integer_column(title: str, field: str, **overrides) -> dict:
    return _column(
        title,
        field,
        sorter="number",
        hozAlign="right",
        headerHozAlign="right",
        formatter="dash:integer",
        **overrides,
    )


def percentage_column(title: str, field: str, *, decimals: int = 1, **overrides) -> dict:
    return _column(
        title,
        field,
        sorter="number",
        hozAlign="right",
        headerHozAlign="right",
        formatter="dash:percentage",
        formatterParams={"decimals": decimals},
        **overrides,
    )


def currency_column(title: str, field: str, *, symbol: str = "¤", **overrides) -> dict:
    return _column(
        title,
        field,
        sorter="number",
        hozAlign="right",
        headerHozAlign="right",
        formatter="dash:currency",
        formatterParams={"symbol": symbol},
        **overrides,
    )


def date_column(title: str, field: str, **overrides) -> dict:
    return _column(title, field, sorter="date", formatter="dash:date", **overrides)


def status_column(title: str = "Status", field: str = "status", **overrides) -> dict:
    return _column(
        title,
        field,
        headerFilter="list",
        headerFilterParams={"valuesLookup": True, "clearable": True},
        formatter="dash:statusBadge",
        **overrides,
    )


def signed_column(title: str, field: str, *, decimals: int = 1, **overrides) -> dict:
    return _column(
        title,
        field,
        sorter="number",
        hozAlign="right",
        formatter="dash:signed",
        formatterParams={"decimals": decimals},
        **overrides,
    )


def expandable_column(title: str, field: str = "label", **overrides) -> dict:
    return _column(title, field, frozen=True, minWidth=220, headerFilter="input", **overrides)
