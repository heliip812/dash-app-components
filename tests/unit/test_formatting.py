from src.utils.formatting import format_number, format_percentage, humanize_count


def test_numeric_formatters():
    assert format_number(12345.678, 2) == "12,345.68"
    assert format_percentage(0.1234) == "12.3%"
    assert humanize_count(1_250_000) == "1.2M"
    assert format_number(None) == "—"
