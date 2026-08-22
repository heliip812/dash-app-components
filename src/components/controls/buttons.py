"""Button primitives."""

from dash import html


def button(label: str, *, element_id: str | None = None, variant: str = "primary", icon: str | None = None, **props):
    children = [html.Span(icon, className="button__icon", **{"aria-hidden": "true"})] if icon else []
    children.append(html.Span(label))
    if element_id:
        props["id"] = element_id
    return html.Button(children, className=f"button button--{variant}", **props)


def icon_button(icon: str, *, element_id: str | None = None, label: str, variant: str = "ghost"):
    props = {"aria-label": label}
    if element_id:
        props["id"] = element_id
    return html.Button(icon, className=f"icon-button icon-button--{variant}", **props)
