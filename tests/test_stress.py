"""Stress and regression tests for the Fly-in project.

Run with:
    pytest -q tests/test_stress.py

These tests intentionally exercise rules that are easy to miss:
- graph bidirectionality
- weighted Dijkstra
- blocked/unreachable routes
- priority tie-breaking
- unlimited start/end occupancy
- zone capacity
- connection capacity
- restricted two-turn transit
- restricted connection capacity
- same-turn capacity release
- simulator termination
"""

import pytest

from fly_in.drone import Drone, DroneStatus
from fly_in.graph import Graph
from fly_in.models import Connection, Zone, ZoneType
from fly_in.pathfinding import PathFinder
from fly_in.simulator import Simulator


def zone(
    name: str,
    zone_type: ZoneType = ZoneType.NORMAL,
    max_drones: int | None = 1,
) -> Zone:
    """Create a test zone."""
    return Zone(
        name=name,
        x=0,
        y=0,
        zone_type=zone_type,
        color=None,
        max_drones=max_drones,
    )


def graph_with(
    zones: list[Zone],
    connections: list[tuple[str, str, int]],
) -> Graph:
    """Create a graph from test zones and connections."""
    graph = Graph()

    for item in zones:
        graph.add_zone(item)

    for zone_a, zone_b, capacity in connections:
        graph.add_connection(
            Connection(zone_a, zone_b, capacity)
        )

    return graph


class TestGraph:
    """Regression tests for the graph model."""

    def test_connection_is_bidirectional(self) -> None:
        graph = graph_with(
            [zone("A"), zone("B")],
            [("A", "B", 3)],
        )

        assert graph.neighbors("A") == ["B"]
        assert graph.neighbors("B") == ["A"]
        assert graph.get_connection("A", "B").max_link_capacity == 3
        assert graph.get_connection("B", "A").max_link_capacity == 3

    def test_duplicate_connection_is_rejected_both_directions(self) -> None:
        graph = graph_with(
            [zone("A"), zone("B")],
            [("A", "B", 1)],
        )

        with pytest.raises(ValueError):
            graph.add_connection(Connection("B", "A", 1))


class TestDijkstra:
    """Regression tests for single-drone pathfinding."""

    def test_normal_shortest_path(self) -> None:
        graph = graph_with(
            [zone("A"), zone("B"), zone("C")],
            [("A", "B", 1), ("B", "C", 1)],
        )

        path = PathFinder().dijkstra(graph, "A", "C")

        assert path is not None
        assert [item.name for item in path] == ["A", "B", "C"]

    def test_cheaper_longer_route_beats_more_expensive_short_route(self) -> None:
        graph = graph_with(
            [
                zone("A"),
                zone("restricted", ZoneType.RESTRICTED),
                zone("normal_1"),
                zone("normal_2"),
                zone("C"),
            ],
            [
                ("A", "restricted", 1),
                ("restricted", "C", 1),
                ("A", "normal_1", 1),
                ("normal_1", "normal_2", 1),
                ("normal_2", "C", 1),
            ],
        )

        path = PathFinder().dijkstra(graph, "A", "C")

        assert path is not None
        assert [item.name for item in path] == [
            "A",
            "normal_1",
            "normal_2",
            "C",
        ]

    def test_blocked_zone_is_never_used(self) -> None:
        graph = graph_with(
            [
                zone("A"),
                zone("blocked", ZoneType.BLOCKED),
                zone("B"),
                zone("C"),
            ],
            [
                ("A", "blocked", 1),
                ("blocked", "C", 1),
                ("A", "B", 1),
                ("B", "C", 1),
            ],
        )

        path = PathFinder().dijkstra(graph, "A", "C")

        assert path is not None
        names = [item.name for item in path]
        assert "blocked" not in names
        assert names == ["A", "B", "C"]

    def test_unreachable_returns_none(self) -> None:
        graph = graph_with(
            [zone("A"), zone("B"), zone("C"), zone("D")],
            [("A", "B", 1), ("C", "D", 1)],
        )

        assert PathFinder().dijkstra(graph, "A", "D") is None

    def test_start_equals_goal(self) -> None:
        graph = graph_with([zone("A")], [])

        path = PathFinder().dijkstra(graph, "A", "A")

        assert path is not None
        assert [item.name for item in path] == ["A"]

    def test_priority_wins_equal_cost_tie(self) -> None:
        """Priority must win when two routes have identical total cost."""
        graph = graph_with(
            [
                zone("start"),
                zone("normal"),
                zone("priority", ZoneType.PRIORITY),
                zone("goal"),
            ],
            [
                ("start", "normal", 1),
                ("normal", "goal", 1),
                ("start", "priority", 1),
                ("priority", "goal", 1),
            ],
        )

        path = PathFinder().dijkstra(graph, "start", "goal")

        assert path is not None
        assert [item.name for item in path] == [
            "start",
            "priority",
            "goal",
        ]


class TestSimulator:
    """Stress tests for turn scheduling and capacity rules."""

    @staticmethod
    def make_drones(
        count: int,
        path: list[str],
    ) -> list[Drone]:
        """Create numbered drones following the same path."""
        return [
            Drone(id=index, path=list(path))
            for index in range(1, count + 1)
        ]

    def test_one_drone_reaches_goal_in_one_turn(self) -> None:
        graph = graph_with(
            [zone("start", max_drones=None), zone("goal", max_drones=None)],
            [("start", "goal", 1)],
        )
        drones = self.make_drones(1, ["start", "goal"])

        turns = Simulator(graph, drones, "goal").run()

        assert turns == [["D1-goal"]]
        assert drones[0].status == DroneStatus.DELIVERED

    def test_end_zone_has_unlimited_capacity(self) -> None:
        """All drones must be able to arrive at the end zone."""
        graph = graph_with(
            [zone("start", max_drones=1), zone("goal", max_drones=1)],
            [("start", "goal", 5)],
        )
        drones = self.make_drones(5, ["start", "goal"])

        turns = Simulator(graph, drones, "goal").run()

        assert len(turns) == 1
        assert turns[0] == [
            "D1-goal",
            "D2-goal",
            "D3-goal",
            "D4-goal",
            "D5-goal",
        ]
        assert all(drone.is_delivered for drone in drones)

    def test_zone_capacity_is_enforced(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("middle", max_drones=1),
                zone("goal", max_drones=None),
            ],
            [
                ("start", "middle", 2),
                ("middle", "goal", 2),
            ],
        )
        drones = self.make_drones(
            2,
            ["start", "middle", "goal"],
        )

        turns = Simulator(graph, drones, "goal").run()

        assert len(turns) == 3
        assert turns[0] == ["D1-middle"]
        assert turns[1] == ["D1-goal", "D2-middle"]
        assert turns[2] == ["D2-goal"]

    def test_connection_capacity_is_enforced(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("middle", max_drones=2),
                zone("goal", max_drones=None),
            ],
            [
                ("start", "middle", 1),
                ("middle", "goal", 2),
            ],
        )
        drones = self.make_drones(
            2,
            ["start", "middle", "goal"],
        )

        turns = Simulator(graph, drones, "goal").run()

        assert len(turns) == 3
        assert turns[0] == ["D1-middle"]
        assert turns[1] == ["D1-goal", "D2-middle"]
        assert turns[2] == ["D2-goal"]

    def test_restricted_zone_takes_exactly_two_turns_to_reach(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("restricted", ZoneType.RESTRICTED, max_drones=1),
                zone("goal", max_drones=None),
            ],
            [
                ("start", "restricted", 1),
                ("restricted", "goal", 1),
            ],
        )
        drones = self.make_drones(
            1,
            ["start", "restricted", "goal"],
        )

        turns = Simulator(graph, drones, "goal").run()

        assert turns == [
            ["D1-start-restricted"],
            ["D1-restricted"],
            ["D1-goal"],
        ]
        assert drones[0].is_delivered

    def test_restricted_connection_capacity_is_enforced(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("restricted", ZoneType.RESTRICTED, max_drones=2),
                zone("goal", max_drones=None),
            ],
            [
                ("start", "restricted", 1),
                ("restricted", "goal", 2),
            ],
        )
        drones = self.make_drones(
            2,
            ["start", "restricted", "goal"],
        )

        turns = Simulator(graph, drones, "goal").run()

        assert len(turns) == 4
        assert turns[0] == ["D1-start-restricted"]
        assert turns[1] == [
            "D1-restricted",
            "D2-start-restricted",
        ]
        assert turns[2] == ["D1-goal", "D2-restricted"]
        assert turns[3] == ["D2-goal"]

    def test_leaving_zone_frees_capacity_same_turn(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("middle", max_drones=1),
                zone("goal", max_drones=None),
            ],
            [
                ("start", "middle", 2),
                ("middle", "goal", 2),
            ],
        )
        drones = self.make_drones(
            2,
            ["start", "middle", "goal"],
        )

        simulator = Simulator(graph, drones, "goal")

        assert simulator.step() == ["D1-middle"]
        assert simulator.step() == ["D1-goal", "D2-middle"]
        assert simulator.step() == ["D2-goal"]

    def test_no_empty_turns_before_delivery(self) -> None:
        graph = graph_with(
            [
                zone("start", max_drones=None),
                zone("goal", max_drones=None),
            ],
            [("start", "goal", 3)],
        )
        drones = self.make_drones(3, ["start", "goal"])

        turns = Simulator(graph, drones, "goal").run()

        assert turns
        assert all(turn for turn in turns)
        assert all(drone.is_delivered for drone in drones)
