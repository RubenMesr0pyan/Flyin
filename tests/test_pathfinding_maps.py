"""Integration tests for PathFinder against real map files."""

import pytest
from fly_in.parser import MapParser
from fly_in.pathfinding import PathFinder


@pytest.fixture
def parser() -> MapParser:
    return MapParser()


@pytest.fixture
def finder() -> PathFinder:
    return PathFinder()


def test_priority_preferred_over_normal(parser: MapParser, finder: PathFinder) -> None:
    parsed_map = parser.parse("maps/map_priority.txt")
    path = finder.dijkstra(parsed_map.graph, parsed_map.start_hub, parsed_map.end_hub)
    
    assert path is not None
    path_names = [z.name for z in path]
    assert path_names == ["start", "prio_b", "goal"]


def test_restricted_cost_eval(parser: MapParser, finder: PathFinder) -> None:
    parsed_map = parser.parse("maps/map_restricted_vs_detour.txt")
    path = finder.dijkstra(parsed_map.graph, parsed_map.start_hub, parsed_map.end_hub)
    
    assert path is not None
    path_names = [z.name for z in path]
    assert "restr_zone" in path_names or "mid1" in path_names


def test_blocked_zones_ignored(parser: MapParser, finder: PathFinder) -> None:
    parsed_map = parser.parse("maps/map_blocked.txt")
    path = finder.dijkstra(parsed_map.graph, parsed_map.start_hub, parsed_map.end_hub)
    
    assert path is not None
    path_names = [z.name for z in path]
    assert "trap" not in path_names
    assert path_names == ["start", "safe", "goal"]


def test_unreachable_returns_none(parser: MapParser, finder: PathFinder) -> None:
    parsed_map = parser.parse("maps/map_unreachable.txt")
    path = finder.dijkstra(parsed_map.graph, parsed_map.start_hub, parsed_map.end_hub)
    
    assert path is None