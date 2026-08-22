"""Independent design-system component specimens."""

from dash import html

from src.components.cards import collapsible_panel, metric_card, panel, section_heading
from src.components.charts import graph_container
from src.components.controls import button, checkbox, dropdown, icon_button, search_input, text_input, toggle
from src.components.feedback import alert, badge, empty_state, loading_state, modal, status_badge, tooltip
from src.components.tables.base_table import dataframe_records
from src.components.tables.hierarchy_table import hierarchy_table
from src.components.tables.tabulator_table import tabulator_table
from src.components.tables.table_options import base_table_options
from src.transformations import build_hierarchy, group_dataframe
from src.figures import build_bar_figure
from src.utils.ids import view_id
from .config import VIEW_KEY


def specimen(title, body, description: str | None = None):
    return html.Article([html.H3(title), html.P(description) if description else None, html.Div(body, className="specimen__body")], className="specimen")


def layout(dataframes, tables):
    source = dataframes.get("sample")
    sample = source.head(12)
    hierarchy = build_hierarchy(source, levels=["category", "subcategory"], aggregations={"value": "sum", "quantity": "sum"})
    grouped = group_dataframe(source, ["category"], {"value": "sum"})
    return html.Section(
        id=view_id(VIEW_KEY),
        className="app-view",
        children=[
            html.Div(
                [html.Div([html.Span("Reusable design system", className="eyebrow"), html.H1("Component Gallery"), html.P("Develop and validate shared UI primitives here before composing analytical views.")])],
                className="view-header",
            ),
            section_heading("Actions & feedback", "Buttons, badges, alerts, tooltips, and states."),
            html.Div(
                [
                    specimen(
                        "Buttons",
                        [
                            button("Primary", element_id="gallery-primary"),
                            button("Secondary", element_id="gallery-secondary", variant="secondary"),
                            button("Ghost", element_id="gallery-ghost", variant="ghost"),
                            button("Danger", element_id="gallery-danger", variant="danger"),
                            icon_button("＋", element_id="gallery-icon", label="Add item"),
                            button("Open modal", element_id="gallery-open-modal", variant="secondary"),
                        ],
                    ),
                    specimen("Badges & status pills", [badge("Neutral"), badge("Information", "info"), status_badge("Active"), status_badge("Pending"), status_badge("Paused")]),
                    specimen("Tooltip", tooltip("Hover or focus for context", "Tooltips use CSS and require no server callback.")),
                    specimen("Loading", loading_state("Preparing compact result")),
                ],
                className="specimen-grid",
            ),
            html.Div([alert("Information", "This is a generic callout for workflow context."), alert("Check required", "Use warning tone for actionable caveats.", tone="warning")], className="gallery-alerts"),
            section_heading("Controls", "Labelled inputs with stable component classes."),
            html.Div(
                [
                    specimen("Text input", text_input("gallery-text", "Label", placeholder="Enter a value")),
                    specimen("Search input", search_input("gallery-search", placeholder="Search components…")),
                    specimen("Dropdown", dropdown("gallery-dropdown", "Category", [{"label": "Alpha", "value": "Alpha"}, {"label": "Beta", "value": "Beta"}], "Alpha")),
                    specimen("Checkbox", checkbox("gallery-checkbox", "Include inactive", checked=True)),
                    specimen("Toggle", toggle("gallery-toggle", "Live updates", value=True, description="Refresh compact results automatically.")),
                ],
                className="specimen-grid",
            ),
            section_heading("Cards & containers", "Composition patterns for metrics, content, charts, and empty states."),
            html.Div(
                [
                    metric_card("Total Records", f"{len(source):,}", helper="registry owned", tone="positive"),
                    metric_card("Average Value", f"{source['value'].mean():,.2f}", helper="synthetic sample", tone="info"),
                    panel("Content card", html.P("Panels own structure; view CSS controls view-specific placement."), description="Reusable panel component"),
                    collapsible_panel("Collapsible panel", html.P("Native details/summary preserves keyboard accessibility."), open_by_default=True),
                ],
                className="gallery-card-grid",
            ),
            html.Div(
                [
                    panel("Chart container", graph_container("gallery-chart", build_bar_figure(grouped, x="category", y="value", height=280)), description="Reusable Plotly wrapper."),
                    panel("Empty state", empty_state("Nothing here yet", "Add a reusable action when an analytical result is empty.", action_id="gallery-empty-action"), description="Neutral zero-data state."),
                ],
                className="dashboard-grid dashboard-grid--equal",
            ),
            section_heading("Table components", "The same integration supports flat and hierarchical datasets."),
            html.Div(
                [
                    panel(
                        "Tabulator table",
                        tabulator_table("gallery-standard-table", data=dataframe_records(sample), columns=tables.standard_columns(), options=base_table_options(height="330px", paginationSize=6)),
                        description="Filter toolbar, status cells, conditional numeric styling, sorting, and resizing.",
                    ),
                    panel(
                        "Hierarchy table",
                        hierarchy_table("gallery-tree-table", hierarchy=hierarchy, columns=tables.hierarchy_columns(), options={"height": "330px"}),
                        description="Custom chevrons with two nested levels.",
                    ),
                ],
                className="dashboard-grid dashboard-grid--equal",
            ),
            modal("gallery-modal", "Reusable modal", html.P("The modal shell is reusable; this demo only toggles lightweight UI state."), close_id="gallery-close-modal"),
        ],
    )
