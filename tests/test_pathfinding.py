"""Dijkstra tests -- Day 4.

Every expected value below was verified against a reference
implementation before being written here -- not hand-computed and
hoped for. Trust these numbers; if your code disagrees, the bug is in
your code (or, tell me, and we'll check together).

TODO: adjust the import if you named your class/method differently.
"""
from fly_in.parser import MapParser
from fly_in.pathfinding import PathFinder

MAPS = "maps"


def _names(path):
    """Helper: turn a list[Zone] into a list[str] of zone names."""
    return [zone.name for zone in path] if path is not None else None


# def test_example_map_prefers_the_cheaper_equal_length_path():
#     # hub -> corridorA -> tunnelB -> goal costs 1+1+1 = 3.
#     # hub -> roof1 -> roof2 -> goal costs 2+1+1 = 4, despite being the
#     # SAME number of hops (3). This is the whole point of Day 4: BFS
#     # could not tell these two apart, Dijkstra must.
#     result = MapParser().parse(f"{MAPS}/example.txt")
#     path = PathFinder().dijkstra(result.graph, result.start_hub, result.end_hub)
#     assert _names(path) == ["hub", "corridorA", "tunnelB", "goal"]


def test_straightforward_map_all_normal_zones():
    # Sanity baseline: no restricted/priority/blocked zones at all, so
    # this should behave exactly like BFS. Cost = hop count = 3.
    result = MapParser().parse(f"{MAPS}/straightforward.txt")
    path = PathFinder().dijkstra(result.graph, result.start_hub, result.end_hub)
    assert _names(path) == ["s", "a", "b", "e"]


def test_blocked_zone_is_never_used_even_as_a_shortcut():
    # 's' connects directly to 'mid' which connects directly to 'e' --
    # the shortest-HOP path -- but 'mid' is blocked. The correct
    # answer must detour through alt1/alt2 instead, and must never
    # contain 'mid' anywhere in the path.
    result = MapParser().parse(f"{MAPS}/blocked_detour.txt")
    path = PathFinder().dijkstra(result.graph, result.start_hub, result.end_hub)
    names = _names(path)
    assert names == ["s", "alt1", "alt2", "e"]
    assert "mid" not in names


def test_unreachable_goal_returns_none_cleanly():
    # 'island' has a connection from 's' but nothing connects to 'e'
    # at all. No crash, no infinite loop -- just None.
    result = MapParser().parse(f"{MAPS}/unreachable.txt")
    path = PathFinder().dijkstra(result.graph, result.start_hub, result.end_hub)
    assert path is None
