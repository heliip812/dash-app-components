"""Application factory and dependency composition root."""

from dataclasses import dataclass

from dash import Dash

from src.callbacks import register_callbacks
from src.data.bootstrap import bootstrap_registry
from src.data.cache import DataFrameResultCache
from src.data.registry import DataFrameRegistry
from src.layout import app_shell
from src.services import DataFrameService, PivotService, TableService, VisualisationService
from src.utils.paths import PROJECT_ROOT


TABULATOR_VERSION = "6.3.1"
TABULATOR_CSS = f"https://unpkg.com/tabulator-tables@{TABULATOR_VERSION}/dist/css/tabulator.min.css"
TABULATOR_JS = f"https://unpkg.com/tabulator-tables@{TABULATOR_VERSION}/dist/js/tabulator.min.js"


@dataclass(frozen=True)
class AppServices:
    dataframes: DataFrameService
    pivots: PivotService
    tables: TableService
    visualisations: VisualisationService


def build_services(registry: DataFrameRegistry) -> AppServices:
    dataframes = DataFrameService(registry)
    return AppServices(
        dataframes=dataframes,
        pivots=PivotService(dataframes, DataFrameResultCache(max_entries=32)),
        tables=TableService(),
        visualisations=VisualisationService(),
    )


def create_app(registry: DataFrameRegistry | None = None) -> Dash:
    """Create a single-URL Dash app with one process-local data registry."""
    registry = bootstrap_registry(registry)
    services = build_services(registry)
    app = Dash(
        __name__,
        assets_folder=str(PROJECT_ROOT / "assets"),
        title="Dashwork · reusable analytical workstation",
        update_title=None,
        suppress_callback_exceptions=False,
        external_stylesheets=[TABULATOR_CSS],
        external_scripts=[TABULATOR_JS],
    )
    app.layout = app_shell(services)
    app.data_registry = registry
    app.services = services
    register_callbacks(app, services)
    return app
