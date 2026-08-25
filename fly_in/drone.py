"""The Drone: per-agent state.

TODO (Day 6):
- id, current position, status (waiting / moving / in-transit / delivered)
- planned path
- remaining turns for an in-progress restricted-zone transit
  (must arrive next turn, cannot wait mid-flight)
"""
"""Drone: per-agent state during the turn-by-turn simulation.

See simulator.py's module docstring for the full turn algorithm this
state feeds into -- this file is the data model Day 5's design landed
on. Unlike parser/graph/pathfinding, this one's given complete: it's
plumbing, not the algorithm a peer reviewer will actually probe.
"""
from dataclasses import dataclass
from enum import Enum


class DroneStatus(Enum):
    """Lifecycle states a drone moves through during the simulation."""

    WAITING = "waiting"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


@dataclass
class Drone:
    """Track one drone's position and progress along its planned path."""

    id: int
    path: list[str]
    path_index: int = 0
    status: DroneStatus = DroneStatus.WAITING
    transit_connection: tuple[str, str] | None = None

    @property
    def position(self) -> str:
        """Current zone name (last zone arrived at or departed from)."""
        return self.path[self.path_index]

    @property
    def next_zone(self) -> str | None:
        """The next zone in the plan, or None if already at the last one."""
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]

    @property
    def is_delivered(self) -> bool:
        """True once this drone has reached the final zone in its path."""
        return self.status == DroneStatus.DELIVERED