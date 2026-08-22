"""Mounted view navigation configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavItem:
    key: str
    label: str
    eyebrow: str
    icon: str


NAV_ITEMS = (
    NavItem("overview", "Overview", "Workspace", "⌂"),
    NavItem("table-lab", "Table Lab", "Components", "▦"),
    NavItem("pivot-lab", "Pivot Lab", "Analysis", "⌗"),
    NavItem("visualisation-lab", "Visualisation Lab", "Charts", "◒"),
    NavItem("component-gallery", "Component Gallery", "Design system", "◇"),
)

DEFAULT_VIEW = "overview"
VIEW_KEYS = tuple(item.key for item in NAV_ITEMS)
