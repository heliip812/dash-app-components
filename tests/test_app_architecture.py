from pathlib import Path

from dash import dcc

from app import app, server
from src.callbacks.register import ALL_TABLE_IDS
from src.navigation.config import VIEW_KEYS


ROOT = Path(__file__).resolve().parents[1]


def _walk(component):
    yield component
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            if child is not None:
                yield from _walk(child)
    elif children is not None and hasattr(children, "children"):
        yield from _walk(children)


def test_app_uses_one_url_and_all_views_are_mounted():
    components = list(_walk(app.layout))
    ids = {getattr(component, "id", None) for component in components}
    assert {f"view-{key}" for key in VIEW_KEYS}.issubset(ids)
    assert not any(isinstance(component, dcc.Location) for component in components)
    assert "active-view" in ids
    assert server is app.server


def test_all_tabulator_hosts_have_client_bridge_callbacks():
    callback_outputs = " ".join(app.callback_map)
    for table_id in ALL_TABLE_IDS:
        assert table_id in callback_outputs


def test_registry_loaded_sample_once_and_reuses_object():
    first = app.data_registry.get("sample")
    second = app.data_registry.get("sample")
    assert first is second
    assert app.data_registry.metadata("sample").attributes["load_count"] == 1
    assert len(first) == 75_000


def test_segregated_assets_exist():
    required = [
        "assets/css/global/tokens.css",
        "assets/css/components/tables.css",
        "assets/css/views/pivot_lab.css",
        "assets/js/components/tabulator_factory.js",
        "assets/js/components/table_formatters.js",
        "assets/js/views/table_lab.js",
    ]
    assert all((ROOT / path).is_file() for path in required)
    assert Path(app.config.assets_folder) == ROOT / "assets"
