"""Domain data types: Zone, Connection, ZoneType.

This module defines the core data structures for zones, zone types,
and connections within the Fly-in network.
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
