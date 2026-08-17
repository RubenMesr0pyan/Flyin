"""The Graph: your own adjacency-list based graph structure.

No networkx, no graphlib -- this is the whole point of the project.

TODO (Day 3):
- Graph class holding zones (dict[str, Zone]) and adjacency info.
- add_zone(zone), add_connection(connection).
- neighbors(zone_name) -> list of reachable zone names (respecting the
  bidirectional nature of connections).
- Think about how you'll store connection metadata (max_link_capacity)
  so the simulator can look it up later.
"""
