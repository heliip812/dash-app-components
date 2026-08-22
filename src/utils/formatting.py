"""Server-side value formatting for narrative UI and tests."""

from numbers import Number


def format_number(value: Number | None, decimals: int = 0) -> str:
    if value is None:
        return "—"
    return f"{value:,.{decimals}f}"


def format_percentage(value: Number | None, decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}%}"


def humanize_count(value: Number | None) -> str:
    if value is None:
        return "—"
    absolute = abs(float(value))
    for threshold, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if absolute >= threshold:
            return f"{value / threshold:.1f}{suffix}"
    return f"{value:,.0f}"
