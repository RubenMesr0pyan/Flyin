"""Domain data types: Zone, Connection, ZoneType.

TODO (Day 3):
- Define `ZoneType` as an Enum: NORMAL, BLOCKED, RESTRICTED, PRIORITY.
- Define `Zone` as a dataclass: name, x, y, zone_type, color, max_drones.
- Define `Connection` as a dataclass: zone_a, zone_b, max_link_capacity.
- Think about: what's the *cost* of moving into a zone, based on its type?
  Where should that logic live -- on Zone itself, or in the pathfinder?
"""
