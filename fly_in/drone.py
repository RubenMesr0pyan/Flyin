"""Drone: per-agent state during the turn-by-turn simulation.

This module defines the data model for individual drones, tracking their
current position, lifecycle status, path progress, and transit connections.
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
        """Return the current zone name."""
        return self.path[self.path_index]

    @property
    def next_zone(self) -> str | None:
        """Return the next zone in the path, or None if at the end."""
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]

    @property
    def is_delivered(self) -> bool:
        """Check if the drone has reached the final zone in its path."""
        return self.status == DroneStatus.DELIVERED
