import pytest

from fly_in.drone import Drone, DroneStatus
from fly_in.graph import Graph
from fly_in.models import Connection, Zone, ZoneType
from fly_in.simulator import Simulator


def make_zone(
    name: str,
    zone_type: ZoneType = ZoneType.NORMAL,
    max_drones: int | None = None,
) -> Zone:
    return Zone(
        name=name,
        x=0,
        y=0,
        zone_type=zone_type,
        color=None,
        max_drones=max_drones,
    )


def make_graph(
    zones: list[Zone],
    connections: list[tuple[str, str, int]],
) -> Graph:
    graph = Graph()

    for zone in zones:
        graph.add_zone(zone)

    for zone_a, zone_b, capacity in connections:
        graph.add_connection(
            Connection(
                zone_a=zone_a,
                zone_b=zone_b,
                max_link_capacity=capacity,
            )
        )

    return graph


# ---------------------------------------------------------
# Basic movement
# ---------------------------------------------------------


def test_single_drone_reaches_goal():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("middle"),
            make_zone("goal"),
        ],
        [
            ("start", "middle", 1),
            ("middle", "goal", 1),
        ],
    )

    drone = Drone(
        id=1,
        path=["start", "middle", "goal"],
    )

    simulator = Simulator(graph, [drone], end_hub="goal")
    turns = simulator.run()

    assert turns == [
        ["D1-middle"],
        ["D1-goal"],
    ]

    assert drone.is_delivered
    assert drone.position == "goal"


def test_drone_does_not_move_more_than_one_zone_per_turn():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("a"),
            make_zone("b"),
            make_zone("goal"),
        ],
        [
            ("start", "a", 1),
            ("a", "b", 1),
            ("b", "goal", 1),
        ],
    )

    drone = Drone(
        id=1,
        path=["start", "a", "b", "goal"],
    )

    simulator = Simulator(graph, [drone], end_hub="goal")

    turns = simulator.run()

    assert len(turns) == 3

    assert turns[0] == ["D1-a"]
    assert turns[1] == ["D1-b"]
    assert turns[2] == ["D1-goal"]


# ---------------------------------------------------------
# Multiple drones
# ---------------------------------------------------------


def test_multiple_drones_are_all_delivered():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 12),
        ],
    )

    drones = [
        Drone(id=i, path=["start", "goal"])
        for i in range(1, 13)
    ]

    simulator = Simulator(graph, drones, end_hub="goal")
    turns = simulator.run()

    assert all(drone.is_delivered for drone in drones)

    assert turns == [
        [
            "D1-goal",
            "D2-goal",
            "D3-goal",
            "D4-goal",
            "D5-goal",
            "D6-goal",
            "D7-goal",
            "D8-goal",
            "D9-goal",
            "D10-goal",
            "D11-goal",
            "D12-goal",
        ]
    ]


def test_moves_are_sorted_by_drone_id():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 10),
        ],
    )

    drones = [
        Drone(id=5, path=["start", "goal"]),
        Drone(id=2, path=["start", "goal"]),
        Drone(id=9, path=["start", "goal"]),
        Drone(id=1, path=["start", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    assert turns[0] == [
        "D1-goal",
        "D2-goal",
        "D5-goal",
        "D9-goal",
    ]


# ---------------------------------------------------------
# Zone capacity
# ---------------------------------------------------------


def test_zone_capacity_blocks_extra_drone():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("middle", max_drones=1),
            make_zone("goal"),
        ],
        [
            ("start", "middle", 2),
            ("middle", "goal", 1),
        ],
    )

    drones = [
        Drone(id=1, path=["start", "middle", "goal"]),
        Drone(id=2, path=["start", "middle", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    first_turn = simulator.step()

    assert first_turn == ["D1-middle"]

    assert drones[0].position == "middle"
    assert drones[1].position == "start"


def test_leaving_zone_frees_capacity():
    graph = make_graph(
        [
            make_zone("start", max_drones=2),
            make_zone("middle", max_drones=1),
            make_zone("goal"),
        ],
        [
            ("start", "middle", 2),
            ("middle", "goal", 1),
        ],
    )

    drones = [
        Drone(id=1, path=["start", "middle", "goal"]),
        Drone(id=2, path=["start", "middle", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    assert simulator.step() == ["D1-middle"]

    assert simulator.step() == [
        "D1-goal",
        "D2-middle",
    ]


# ---------------------------------------------------------
# Connection capacity
# ---------------------------------------------------------


def test_connection_capacity_is_enforced():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 1),
        ],
    )

    drones = [
        Drone(id=1, path=["start", "goal"]),
        Drone(id=2, path=["start", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    assert turns == [
        ["D1-goal"],
        ["D2-goal"],
    ]


def test_high_connection_capacity_allows_parallel_moves():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 5),
        ],
    )

    drones = [
        Drone(id=i, path=["start", "goal"])
        for i in range(1, 6)
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    assert len(turns) == 1
    assert len(turns[0]) == 5


# ---------------------------------------------------------
# Restricted zones
# ---------------------------------------------------------


def test_restricted_zone_takes_two_turns():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone(
                "restricted",
                ZoneType.RESTRICTED,
                max_drones=2,
            ),
            make_zone("goal"),
        ],
        [
            ("start", "restricted", 1),
            ("restricted", "goal", 1),
        ],
    )

    drone = Drone(
        id=1,
        path=["start", "restricted", "goal"],
    )

    simulator = Simulator(graph, [drone], end_hub="goal")

    turn1 = simulator.step()

    assert turn1 == ["D1-start-restricted"]
    assert drone.status == DroneStatus.IN_TRANSIT

    turn2 = simulator.step()

    assert turn2 == ["D1-restricted"]
    assert drone.status == DroneStatus.WAITING
    assert drone.position == "restricted"

    turn3 = simulator.step()

    assert turn3 == ["D1-goal"]
    assert drone.is_delivered


def test_restricted_drone_cannot_move_again_same_turn():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("restricted"),
            make_zone("goal"),
        ],
        [
            ("start", "restricted", 1),
            ("restricted", "goal", 1),
        ],
    )

    drone = Drone(
        id=1,
        path=["start", "restricted", "goal"],
    )

    simulator = Simulator(graph, [drone], end_hub="goal")

    moves = simulator.step()

    assert moves == ["D1-start-restricted"]

    assert drone.position == "start"
    assert drone.status == DroneStatus.IN_TRANSIT


# ---------------------------------------------------------
# End hub
# ---------------------------------------------------------


def test_end_hub_has_unlimited_capacity():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal", max_drones=None),
        ],
        [
            ("start", "goal", 10),
        ],
    )

    drones = [
        Drone(id=i, path=["start", "goal"])
        for i in range(1, 11)
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    assert len(turns) == 1
    assert len(turns[0]) == 10
    assert all(drone.is_delivered for drone in drones)


# ---------------------------------------------------------
# Output / turn counting
# ---------------------------------------------------------


def test_empty_turns_are_not_counted_as_moves():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("middle", max_drones=1),
            make_zone("goal"),
        ],
        [
            ("start", "middle", 1),
            ("middle", "goal", 1),
        ],
    )

    drones = [
        Drone(id=1, path=["start", "middle", "goal"]),
        Drone(id=2, path=["start", "middle", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    non_empty_turns = [turn for turn in turns if turn]

    assert len(non_empty_turns) == 3


def test_total_turns_for_two_drones_with_capacity_one():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 1),
        ],
    )

    drones = [
        Drone(id=1, path=["start", "goal"]),
        Drone(id=2, path=["start", "goal"]),
    ]

    simulator = Simulator(graph, drones, end_hub="goal")

    turns = simulator.run()

    assert len(turns) == 2
    assert turns[0] == ["D1-goal"]
    assert turns[1] == ["D2-goal"]


# ---------------------------------------------------------
# Occupancy consistency
# ---------------------------------------------------------


def test_start_occupancy_decreases_after_move():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("goal"),
        ],
        [
            ("start", "goal", 1),
        ],
    )

    drone = Drone(id=1, path=["start", "goal"])

    simulator = Simulator(graph, [drone], end_hub="goal")

    assert simulator.zone_occupancy["start"] == 1

    simulator.step()

    assert simulator.zone_occupancy["start"] == 0


def test_destination_occupancy_increases_after_normal_move():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("middle"),
            make_zone("goal"),
        ],
        [
            ("start", "middle", 1),
            ("middle", "goal", 1),
        ],
    )

    drone = Drone(id=1, path=["start", "middle", "goal"])

    simulator = Simulator(graph, [drone], end_hub="goal")

    simulator.step()

    assert simulator.zone_occupancy["start"] == 0
    assert simulator.zone_occupancy["middle"] == 1


def test_all_drones_end_at_goal():
    graph = make_graph(
        [
            make_zone("start"),
            make_zone("a"),
            make_zone("goal"),
        ],
        [
            ("start", "a", 5),
            ("a", "goal", 5),
        ],
    )

    drones = [
        Drone(id=i, path=["start", "a", "goal"])
        for i in range(1, 6)
    ]

    simulator = Simulator(graph, drones, end_hub="goal")
    simulator.run()

    assert all(drone.position == "goal" for drone in drones)
    assert all(drone.status == DroneStatus.DELIVERED for drone in drones)