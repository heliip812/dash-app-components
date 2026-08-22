"""Consistent Plotly graph wrapper."""

from dash import dcc, html


def graph_container(graph_id: str, figure, *, loading: bool = True, class_name: str = ""):
    graph = dcc.Graph(id=graph_id, figure=figure, config={"displayModeBar": False, "responsive": True})
    content = dcc.Loading(graph, type="circle", className="graph-loading") if loading else graph
    return html.Div(content, className=f"graph-container {class_name}".strip())
