"""Range expansion and A1 parsing."""

from fsaslab.addresses import expand_range, format_address, neighbours, parse_address


def test_parse_and_format_round_trip():
    assert parse_address("B5") == (4, 1)
    assert format_address(4, 1) == "B5"
    assert parse_address("AA1") == (0, 26)


def test_expand_range_column():
    assert expand_range("B2:B4") == ["B2", "B3", "B4"]
    assert expand_range("b2") == ["B2"]


def test_expand_range_block():
    assert expand_range("B2:C3") == ["B2", "C2", "B3", "C3"]


def test_neighbours_include_adjacent_row():
    nbs = neighbours("B4")
    assert "B5" in nbs
    assert "B3" in nbs
