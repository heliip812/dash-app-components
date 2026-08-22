from src.navigation.callbacks import navigation_state


def test_navigation_state_uses_button_id_without_routes():
    assert navigation_state("nav-pivot-lab", "overview") == "pivot-lab"
    assert navigation_state(None, "table-lab") == "table-lab"
    assert navigation_state("unknown", "invalid") == "overview"
