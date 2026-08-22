"""Figure label helpers."""


def human_label(value: str) -> str:
    return str(value).replace("_", " ").strip().title()
