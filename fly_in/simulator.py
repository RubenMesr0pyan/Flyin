"""The Simulator/Scheduler: turn-by-turn orchestration.

This is the heart of the project (see Day 5-8 of the roadmap).

TODO:
- Reservation table: which (zone, turn) / (connection, turn) is taken,
  by whom.
- step(): for every drone, compute an *intended* move, resolve conflicts
  against the reservation table, THEN commit -- don't mutate state while
  you're still deciding who gets to go.
- run(): loop step() until every drone is delivered, collecting the
  per-turn move log in the required output format.
- Handle: zone/connection capacity, priority-zone preference, deadlock
  avoidance, the restricted-zone atomic 2-turn transit rule.
"""
"""Simulator/Scheduler: turn-by-turn orchestration of all drones.

Updated design: sequentially processes drones (by ID), strictly
verifying both connection and target zone capacities at the moment
of movement. Capacities for restricted zones are pre-reserved
at transit start.
"""

from .drone import Drone, DroneStatus
from .graph import Graph
from .models import ZoneType


class Simulator:
    """Advance all drones turn by turn until every one is delivered."""

    def __init__(self, graph: Graph, drones: list[Drone], end_hub: str) -> None:
        """Initialize the simulator with graph and planned drones."""
        self.graph = graph
        self.drones = drones
        self.end_hub = end_hub#

        self.zone_occupancy: dict[str, int] = {}
        # Tracks connections occupied by drones currently IN_TRANSIT
        self.connection_occupancy: dict[tuple[str, str], int] = {}

        for drone in self.drones:
            if not drone.is_delivered:
                z_name = drone.position
                self.zone_occupancy[z_name] = self.zone_occupancy.get(z_name, 0) + 1

    def _get_conn_key(self, z1: str, z2: str) -> tuple[str, str]:
        conn = self.graph.get_connection(z1, z2)
        if conn:
            return (conn.zone_a, conn.zone_b)
        return (z1, z2) if z1 < z2 else (z2, z1)

    def _get_conn_name(self, z1: str, z2: str) -> str:
        conn = self.graph.get_connection(z1, z2)
        if conn:
            return f"{conn.zone_a}-{conn.zone_b}"
        return f"{z1}-{z2}"

    def step(self) -> list[str]:
        """Advance the simulation by one turn."""
        turn_moves: list[str] = []
        acted_this_turn: set[int] = set()

        # Snapshot of connection occupancy to check capacity across BOTH 
        # persistent (in_transit) and temporary (1-turn) moves this turn.
        current_conn_occ = self.connection_occupancy.copy()

        # --- Phase 1: Forced arrivals (IN_TRANSIT finishing 2nd turn) ---
        for drone in self.drones:
            if drone.is_delivered or drone.status != DroneStatus.IN_TRANSIT:
                continue

            target_name = drone.next_zone
            if not target_name:
                continue

            # 1. Release the persistent connection capacity
            if drone.transit_connection:
                self.connection_occupancy[drone.transit_connection] = max(
                    0, self.connection_occupancy.get(drone.transit_connection, 0) - 1
                )
                # Sync the local tracker for the rest of this turn
                current_conn_occ[drone.transit_connection] = self.connection_occupancy[drone.transit_connection]

            # 2. Arrive (NOTE: target zone capacity was pre-reserved when transit started, 
            # so we do NOT increment self.zone_occupancy here!)
            drone.status = DroneStatus.WAITING
            drone.transit_connection = None
            drone.path_index += 1

            if drone.path_index == len(drone.path) - 1:
                drone.status = DroneStatus.DELIVERED

            turn_moves.append(f"D{drone.id}-{target_name}")
            acted_this_turn.add(drone.id)

        # --- Phase 2: Voluntary moves (WAITING) ---
        waiting_drones = [
            d for d in self.drones 
            if not d.is_delivered and d.status == DroneStatus.WAITING
        ]
        waiting_drones.sort(key=lambda d: d.id)

        for drone in waiting_drones:
            # Skip if drone already arrived from a transit this exact turn
            if drone.id in acted_this_turn:
                continue

            curr_name = drone.position
            next_name = drone.next_zone
            if not next_name:
                continue

            next_zone = self.graph.get_zone(next_name)

            # Universal Capacity Check 1: Link Capacity
            conn_key = self._get_conn_key(curr_name, next_name)
            conn_obj = self.graph.get_connection(curr_name, next_name)
            max_link = conn_obj.max_link_capacity if conn_obj else 1

            if current_conn_occ.get(conn_key, 0) >= max_link:
                continue

            # Universal Capacity Check 2: Zone Capacity
            # max_drones = next_zone.max_drones
            # if max_drones is not None and self.zone_occupancy.get(next_name, 0) >= max_drones:
            #     continue
            if next_name != self.end_hub:
                max_drones = next_zone.max_drones
                if (
        max_drones is not None
        and self.zone_occupancy.get(next_name, 0) >= max_drones
        ):
                    continue       



            # Both checks passed! Commit the move.
            if next_zone.zone_type == ZoneType.RESTRICTED:
                # Occupy link persistently (for next turn) AND locally (for this turn)
                self.connection_occupancy[conn_key] = self.connection_occupancy.get(conn_key, 0) + 1
                current_conn_occ[conn_key] = current_conn_occ.get(conn_key, 0) + 1
                
                # Pre-reserve destination capacity so no one steals it during our transit
                self.zone_occupancy[next_name] = self.zone_occupancy.get(next_name, 0) + 1
                
                # Free current zone capacity immediately for drones later in the queue
                self.zone_occupancy[curr_name] -= 1

                drone.status = DroneStatus.IN_TRANSIT
                drone.transit_connection = conn_key

                conn_name = self._get_conn_name(curr_name, next_name)
                turn_moves.append(f"D{drone.id}-{conn_name}")
                acted_this_turn.add(drone.id)
            
            else:
                # NORMAL / PRIORITY / HUB move (1 turn)
                # Occupy link locally (for this turn only, so multiple drones don't exceed max_link)
                current_conn_occ[conn_key] = current_conn_occ.get(conn_key, 0) + 1

                # Free current, occupy next immediately
                self.zone_occupancy[curr_name] -= 1
                self.zone_occupancy[next_name] = self.zone_occupancy.get(next_name, 0) + 1

                drone.path_index += 1
                if drone.path_index == len(drone.path) - 1:
                    drone.status = DroneStatus.DELIVERED

                turn_moves.append(f"D{drone.id}-{next_name}")
                acted_this_turn.add(drone.id)
                turn_moves.sort(
    key=lambda move: int(move.split("-", 1)[0][1:])
)

        return turn_moves

    def run(self) -> list[list[str]]:
        """Run the simulation to completion."""
        all_turns: list[list[str]] = []
        max_turns = 1000
        turn_count = 0

        while not all(d.is_delivered for d in self.drones):
            if turn_count >= max_turns:
                raise RuntimeError(
                    f"Simulation exceeded safety limit of {max_turns} turns. "
                    "Possible deadlock detected."
                )

            moves = self.step()
            all_turns.append(moves)
            turn_count += 1

        return all_turns