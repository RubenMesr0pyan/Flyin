"""Domain data types: Zone, Connection, ZoneType.

TODO (Day 3):
- Define `ZoneType` as an Enum: NORMAL, BLOCKED, RESTRICTED, PRIORITY.
- Define `Zone` as a dataclass: name, x, y, zone_type, color, max_drones.
- Define `Connection` as a dataclass: zone_a, zone_b, max_link_capacity.
- Think about: what's the *cost* of moving into a zone, based on its type?
  Where should that logic live -- on Zone itself, or in the pathfinder?
"""
from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    """Types of zones available in the Fly-in network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """Represent a zone in the drone network."""

    name: str
    x: int
    y: int
    zone_type: ZoneType
    color: str | None
    max_drones: int | None


@dataclass
class Connection:
    """Represent a bidirectional connection between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int
