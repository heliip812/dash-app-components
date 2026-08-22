"""Always-mounted single-page application shell."""

from dash import dcc, html

from src.layout.sidebar import sidebar
from src.layout.topbar import topbar
from src.navigation.config import DEFAULT_VIEW
from src.views.component_gallery.layout import layout as component_gallery_layout
from src.views.overview.layout import layout as overview_layout
from src.views.pivot_lab.layout import layout as pivot_lab_layout
from src.views.table_lab.layout import layout as table_lab_layout
from src.views.visualisation_lab.layout import layout as visualisation_lab_layout


def app_shell(services):
    return html.Div(
        id="app-shell",
        className="app-shell",
        children=[
            dcc.Store(id="active-view", data=DEFAULT_VIEW, storage_type="memory"),
            sidebar(),
            html.Button("", id="sidebar-overlay", className="sidebar-overlay", **{"aria-label": "Close navigation"}),
            html.Div(
                className="app-main",
                children=[
                    topbar(),
                    html.Main(
                        id="workspace",
                        className="workspace",
                        children=[
                            overview_layout(services.dataframes),
                            table_lab_layout(services.dataframes, services.tables),
                            pivot_lab_layout(services.pivots, services.tables),
                            visualisation_lab_layout(services.dataframes, services.visualisations),
                            component_gallery_layout(services.dataframes, services.tables),
                        ],
                    ),
                ],
            ),
        ],
    )
