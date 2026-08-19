import pytest

from parser import MapParseError, MapParser


def write_map(
    tmp_path: object,
    content: str,
) -> str:
    """Create a temporary map file."""
    path = tmp_path / "test.map"  # type: ignore[attr-defined]
    path.write_text(content, encoding="utf-8")  # type: ignore[attr-defined]
    return str(path)


def test_parse_valid_map(tmp_path: object) -> None:
    """Parser should correctly parse a valid map."""
    content = """\
nb_drones: 5
start_hub: start 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: A 1 1 [zone=restricted color=red]
hub: B 2 2 [zone=priority max_drones=2]
connection: start-A
connection: A-B
connection: B-goal [max_link_capacity=2]
"""

    path = write_map(tmp_path, content)

    result = MapParser().parse(path)

    assert result.nb_drones == 5
    assert result.start_hub == "start"
    assert result.end_hub == "goal"

    assert result.graph.zone_count() == 4
    assert result.graph.connection_count() == 3

    assert result.graph.get_zone("A").zone_type.value == "restricted"
    assert result.graph.get_zone("B").max_drones == 2

    assert set(result.graph.neighbors("A")) == {
        "start",
        "B",
    }


def test_missing_start_hub(tmp_path: object) -> None:
    """Parser should reject maps without a start zone."""
    content = """\
nb_drones: 3
end_hub: goal 5 5
hub: A 1 1
connection: A-goal
"""

    path = write_map(tmp_path, content)

    with pytest.raises(MapParseError, match="missing start_hub"):
        MapParser().parse(path)


def test_duplicate_connection(tmp_path: object) -> None:
    """Parser should reject duplicate bidirectional connections."""
    content = """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 5 5
hub: A 1 1
connection: start-A
connection: A-start
connection: A-goal
"""

    path = write_map(tmp_path, content)

    with pytest.raises(
        MapParseError,
        match="already exists",
    ):
        MapParser().parse(path)


def test_invalid_zone_type(tmp_path: object) -> None:
    """Parser should reject unknown zone types."""
    content = """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 5 5
hub: A 1 1 [zone=super_fast]
connection: start-A
connection: A-goal
"""

    path = write_map(tmp_path, content)

    with pytest.raises(
        MapParseError,
        match="invalid zone type",
    ):
        MapParser().parse(path)


def test_negative_capacity(tmp_path: object) -> None:
    """Parser should reject negative zone capacities."""
    content = """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 5 5
hub: A 1 1 [max_drones=-2]
connection: start-A
connection: A-goal
"""

    path = write_map(tmp_path, content)

    with pytest.raises(
        MapParseError,
        match="max_drones must be a positive integer",
    ):
        MapParser().parse(path)


def test_dash_in_zone_name(tmp_path: object) -> None:
    """Parser should reject dashes in zone names."""
    content = """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 5 5
hub: bad-zone 1 1
connection: start-bad-zone
connection: bad-zone-goal
"""

    path = write_map(tmp_path, content)

    with pytest.raises(
        MapParseError,
        match="cannot contain '-'",
    ):
        MapParser().parse(path)


def test_connection_to_undefined_zone(tmp_path: object) -> None:
    """Parser should reject connections to undefined zones."""
    content = """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 5 5
connection: start-unknown
"""

    path = write_map(tmp_path, content)

    with pytest.raises(
        MapParseError,
        match="does not exist",
    ):
        MapParser().parse(path)


def test_comments_and_empty_lines(tmp_path: object) -> None:
    """Parser should ignore comments and empty lines."""
    content = """\
# Number of drones

nb_drones: 2

# Start and end
start_hub: start 0 0
end_hub: goal 5 5

# Connection
connection: start-goal
"""

    path = write_map(tmp_path, content)

    result = MapParser().parse(path)

    assert result.nb_drones == 2
    assert result.start_hub == "start"
    assert result.end_hub == "goal"


def test_start_and_end_capacity_is_accepted(
    tmp_path: object,
) -> None:
    """Start and end max_drones metadata should be ignored."""
    content = """\
nb_drones: 10
start_hub: start 0 0 [max_drones=1]
end_hub: goal 5 5 [max_drones=1]
connection: start-goal
"""

    path = write_map(tmp_path, content)

    result = MapParser().parse(path)

    assert result.nb_drones == 10
    assert result.start_hub == "start"
    assert result.end_hub == "goal"