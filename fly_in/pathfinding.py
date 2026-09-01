"""Single-drone shortest-cost pathfinding using Dijkstra's algorithm.

Finds the minimum-cost route between start and goal hubs based on zone
entry costs (turns), ignoring BLOCKED zones completely.
"""

import heapq

from .graph import Graph
from .models import Zone, ZoneType

ZONE_COSTS: dict[ZoneType, int] = {
    ZoneType.NORMAL: 1,
    ZoneType.PRIORITY: 1,
    ZoneType.RESTRICTED: 2,
}

ZONE_PRIORITY: dict[ZoneType, int] = {
    ZoneType.PRIORITY: 0,
    ZoneType.NORMAL: 1,
    ZoneType.RESTRICTED: 1,
}


class PathFinder:
    """Compute single-drone shortest-cost paths over a Graph."""

    def dijkstra(
        self,
        graph: Graph,
        start: str,
        goal: str,
    ) -> list[Zone] | None:
        """Return the cheapest path from start to goal, or None.

        Args:
            graph: The zone graph to search.
            start: Name of the starting zone.
            goal: Name of the destination zone.

        Returns:
            The path as a list of Zone objects from start to goal
            (inclusive), or None if goal is unreachable.
        """
        if not graph.has_zone(start) or not graph.has_zone(goal):
            return None

        # Min-heap stores tuples of (cumulative_cost, priority, zone_name)
        heap: list[tuple[int, int, str]] = [(0, 1, start)]
        dist: dict[str, int] = {start: 0}
        came_from: dict[str, str | None] = {start: None}

        while heap:
            cost, _, current = heapq.heappop(heap)

            # Stale-entry guard for priority queue without decrease-key
            if cost > dist.get(current, float("inf")):
                continue

            # Goal reached: reconstruct path backwards as Zone objects
            if current == goal:
                path_names: list[str] = []
                curr: str | None = goal
                while curr is not None:
                    path_names.append(curr)
                    curr = came_from[curr]
                path_names.reverse()
                return [graph.get_zone(name) for name in path_names]

            # Relax edge transitions to neighbors
            for neighbor_name in graph.neighbors(current):
                neighbor_zone = graph.get_zone(neighbor_name)

                # BLOCKED zones are impassable and never expanded
                if neighbor_zone.zone_type == ZoneType.BLOCKED:
                    continue

                step_cost = ZONE_COSTS.get(neighbor_zone.zone_type, 1)
                new_cost = cost + step_cost

                if new_cost < dist.get(neighbor_name, float("inf")):
                    dist[neighbor_name] = new_cost
                    came_from[neighbor_name] = current
                    priority = ZONE_PRIORITY.get(neighbor_zone.zone_type, 1)
                    heapq.heappush(
                        heap,
                        (new_cost, priority, neighbor_name),
                    )

        return None
