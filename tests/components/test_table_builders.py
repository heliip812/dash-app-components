from src.components.tables.column_builders import date_column, numeric_column, percentage_column, status_column, text_column
from src.components.tables.table_options import base_table_options, merge_options, tree_table_options


def test_column_builders_emit_structured_tabulator_config():
    assert text_column("Name", "name")["headerFilter"] == "input"
    assert numeric_column("Value", "value")["formatter"] == "dash:decimal"
    assert percentage_column("Rate", "rate")["formatterParams"]["decimals"] == 1
    assert date_column("Date", "date")["sorter"] == "date"
    assert status_column()["formatter"] == "dash:statusBadge"
    assert status_column()["headerFilterParams"]["valuesLookup"] is True


def test_option_builders_compose_without_mutating_defaults():
    options = base_table_options(height="500px", columnDefaults={"tooltip": False})
    assert options["height"] == "500px"
    assert options["columnDefaults"] == {"resizable": True, "tooltip": False}
    assert base_table_options()["height"] == "360px"
    tree = tree_table_options(dataTreeStartExpanded=False)
    assert tree["dataTree"] is True
    assert tree["dataTreeStartExpanded"] is False
    assert tree["dataTreeToggleStyle"] == "chevron"


def test_merge_options_is_recursive():
    assert merge_options({"a": {"b": 1, "c": 2}}, {"a": {"b": 3}}) == {"a": {"b": 3, "c": 2}}
