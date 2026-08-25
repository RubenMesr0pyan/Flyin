"""Single-drone shortest-cost pathfinding: Dijkstra / A*.

TODO (Day 4):
- dijkstra(graph, start, goal) -> list[Zone] | None
- (optional) a_star(graph, start, goal) -> list[Zone] | None, using
  straight-line distance on (x, y) as the heuristic.
- Remember: cost of entering a zone depends on its ZoneType, not on
  number of hops. blocked zones are never expanded.
"""
"""Single-drone shortest-cost pathfinding: Dijkstra and (optional) A*.

Day 4's mandatory deliverable is dijkstra(). a_star() is a genuine
bonus -- read the admissibility note in TODO 3 before attempting it.

TODO 1 -- movement cost lookup
    Confirmed word-for-word against subject chapter VI:
        ZoneType.NORMAL     -> 1
        ZoneType.PRIORITY   -> 1   (same cost as normal -- "should be
            prioritized in pathfinding" is a Day 8 scheduling
            preference for tie-breaking, not a cost difference here)
        ZoneType.RESTRICTED -> 2
        ZoneType.BLOCKED    -> never expand this zone at all

    Where this lookup lives is your call -- a dict here in
    pathfinding.py, or a method/property on Zone in models.py (you
    flagged this as an open question back on Day 3; now's when it
    actually gets used, so it's a good moment to decide).

TODO 2 -- PathFinder.dijkstra(graph, start, goal) -> list[Zone] | None
    Same skeleton as your Day 2 BFS, with two changes:
      1. Swap the FIFO queue (collections.deque) for a min-heap
         (heapq), ordered by cumulative cost so far -- not arrival
         order.
      2. Replace the plain `visited` set with `dist: dict[str, int]`,
         the best known cost to reach each zone name so far. A node
         can be relaxed (found a cheaper way in) more than once
         before it's finalized.

    The core invariant is identical to BFS, just generalized: the
    FIRST time you pop a node off the heap, its cost is final --
    exactly like the first time BFS dequeued a node meaning fewest
    hops. A min-heap ordered by cost IS a priority queue; BFS's FIFO
    queue is just the special case where every edge costs exactly 1.

    heapq gotcha (new vs. Day 2): Python's heapq has no decrease-key
    operation. When you find a cheaper path to a node already on the
    heap, you can't update its entry -- you push a NEW (cost, name)
    tuple, leaving the old, worse one sitting in the heap. That means
    a pop can surface a stale entry for a node you already finalized
    more cheaply. Guard immediately after popping:
        if cost > dist.get(current, float("inf")):
            continue

    Structure sketch (fill in the real logic yourself):

        heap: list[tuple[int, str]] = [(0, start)]
        dist: dict[str, int] = {start: 0}
        came_from: dict[str, str | None] = {start: None}

        while heap:
            cost, current = heapq.heappop(heap)
            # ... stale-entry guard ...
            # ... if current == goal: reconstruct via came_from, return ...
            for neighbor_name in graph.neighbors(current):
                # ... look up the neighbor's Zone, get its entry cost ...
                # ... skip entirely if it's blocked ...
                # ... relax: if cost + step < dist.get(neighbor_name, inf):
                #     update dist/came_from, push (new_cost, neighbor_name) ...
        return None  # heap exhausted without reaching goal -- unreachable

TODO 3 (optional, read this first) -- PathFinder.a_star(...)
    A* only guarantees the cheapest path if its heuristic never
    OVERESTIMATES true remaining cost ("admissible"). The obvious
    choice -- straight-line (x, y) distance to the goal -- is what
    most generic A* tutorials recommend, and it works for grid games
    where moving one tile costs about one unit of distance.

    It does NOT hold here. Movement cost depends only on the
    DESTINATION ZONE'S TYPE (1 or 2), completely independent of
    coordinate distance. On the subject's own example map, hub is at
    (0,0) and goal at (10,10): straight-line distance is ~14.1, but
    the actual cheapest path costs 3. That heuristic overestimates by
    ~4.7x at the very start -- badly inadmissible. Using raw
    coordinate distance is not guaranteed to find the cheapest path.

    The safe alternative: run a plain unweighted BFS from every node
    to the goal first (ignoring zone costs, just counting hops), and
    use that hop-count as your heuristic. Since the cheapest possible
    real cost per hop is 1, hop-count-to-goal can never exceed true
    remaining cost -- admissible by construction. More setup than
    "just use the coordinates", but it's actually correct for this
    project's cost model.

    dijkstra() alone fully satisfies Day 4's "done when" bar. Treat
    this as an exploration, not a requirement.
"""
"""Single-drone shortest-cost pathfinding using Dijkstra's algorithm.

Finds the minimum-cost route between start and goal hubs based on zone
entry costs (turns), ignoring BLOCKED zones completely.
"""
import heapq

from .graph import Graph
from .models import Zone, ZoneType

# Map ZoneType to turn cost (entering cost)
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
        # Min-heap stores tuples of (cumulative_cost, zone_name)
        # heap: list[tuple[int, str]] = [(0, start)]
        heap: list[tuple[int, int, str]] = [(0, 1, start)]
        dist: dict[str, int] = {start: 0}
        came_from: dict[str, str | None] = {start: None}
        while heap:
            # cost, current = heapq.heappop(heap)
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
                    # heapq.heappush(heap, (new_cost, neighbor_name))
                    priority = ZONE_PRIORITY.get(neighbor_zone.zone_type, 1)
                    heapq.heappush(
                        heap,
                        (new_cost, priority, neighbor_name),
                        )
        return None