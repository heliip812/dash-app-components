"""Explicitly register server and client callback modules."""

from dash import ClientsideFunction, Input, Output

from src.navigation import callbacks as navigation_callbacks
from src.utils.ids import table_config_id
from src.views.component_gallery import callbacks as gallery_callbacks
from src.views.component_gallery.config import TABLE_IDS as GALLERY_TABLE_IDS
from src.views.overview import callbacks as overview_callbacks
from src.views.overview.config import TABLE_IDS as OVERVIEW_TABLE_IDS
from src.views.pivot_lab import callbacks as pivot_callbacks
from src.views.pivot_lab.config import TABLE_IDS as PIVOT_TABLE_IDS
from src.views.table_lab import callbacks as table_callbacks
from src.views.table_lab.config import TABLE_IDS as TABLE_LAB_TABLE_IDS
from src.views.visualisation_lab import callbacks as visualisation_callbacks


ALL_TABLE_IDS = OVERVIEW_TABLE_IDS + TABLE_LAB_TABLE_IDS + PIVOT_TABLE_IDS + GALLERY_TABLE_IDS


def _register_tabulator_bridges(app) -> None:
    for table_id in ALL_TABLE_IDS:
        app.clientside_callback(
            ClientsideFunction(namespace="dashApp", function_name="syncTabulator"),
            Output(table_id, "title"),
            Input(table_config_id(table_id), "data"),
        )


def register_callbacks(app, services) -> None:
    navigation_callbacks.register(app)
    overview_callbacks.register(app, services.dataframes)
    table_callbacks.register(app, services.dataframes, services.tables, services.visualisations)
    pivot_callbacks.register(app, services.pivots, services.tables)
    visualisation_callbacks.register(app, services.dataframes, services.visualisations)
    gallery_callbacks.register(app)
    _register_tabulator_bridges(app)
