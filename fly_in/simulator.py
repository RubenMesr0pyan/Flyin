"""Simulator/Scheduler: turn-by-turn orchestration of all drones.

Handles turn advancement, connection and zone capacities, restricted zone
two-turn atomic transit, and move log generation sorted by drone ID.
"""

from .drone import Drone, DroneStatus
from .graph import Graph
from .models import ZoneType


class Simulator:
    """Advance all drones turn by turn until every one is delivered."""

    def __init__(
        self, graph: Graph, drones: list[Drone], end_hub: str
    ) -> None:
        """Initialize the simulator with graph, drones, and end hub.

        Args:
            graph: The network graph.
            drones: List of simulation drones.
            end_hub: Name of the destination hub.
        """
        self.graph = graph
        self.drones = drones
        self.end_hub = end_hub

        self.zone_occupancy: dict[str, int] = {}
        self.connection_occupancy: dict[tuple[str, str], int] = {}

        for drone in self.drones:
            if not drone.is_delivered:
                z_name = drone.position
                self.zone_occupancy[z_name] = (
                    self.zone_occupancy.get(z_name, 0) + 1
                )

    def _get_conn_key(self, z1: str, z2: str) -> tuple[str, str]:
        """Return a standardized, canonical connection tuple key."""
        conn = self.graph.get_connection(z1, z2)
        if conn:
            return (conn.zone_a, conn.zone_b)
        return (z1, z2) if z1 < z2 else (z2, z1)

    def _get_conn_name(self, z1: str, z2: str) -> str:
        """Return a hyphen-separated connection string name."""
        conn = self.graph.get_connection(z1, z2)
        if conn:
            return f"{conn.zone_a}-{conn.zone_b}"
        return f"{z1}-{z2}"

    def step(self) -> list[str]:
        """Advance the simulation by one turn.

        Returns:
            A sorted list of move strings executed during this turn.
        """
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
                    0,
                    self.connection_occupancy.get(
                        drone.transit_connection, 0
                    ) - 1,
                )
                current_conn_occ[drone.transit_connection] = (
                    self.connection_occupancy[drone.transit_connection]
                )

            # 2. Arrive at destination
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
            if drone.id in acted_this_turn:
                continue

            curr_name = drone.position
            next_name = drone.next_zone
            if not next_name:
                continue

            next_zone = self.graph.get_zone(next_name)

            # Capacity Check 1: Link Capacity
            conn_key = self._get_conn_key(curr_name, next_name)
            conn_obj = self.graph.get_connection(curr_name, next_name)
            max_link = conn_obj.max_link_capacity if conn_obj else 1

            if current_conn_occ.get(conn_key, 0) >= max_link:
                continue

            # Capacity Check 2: Zone Capacity (bypass check for end_hub)
            if next_name != self.end_hub:
                max_drones = next_zone.max_drones
                if (
                    max_drones is not None
                    and self.zone_occupancy.get(next_name, 0) >= max_drones
                ):
                    continue

            # Both checks passed! Commit the move.
            if next_zone.zone_type == ZoneType.RESTRICTED:
                self.connection_occupancy[conn_key] = (
                    self.connection_occupancy.get(conn_key, 0) + 1
                )
                current_conn_occ[conn_key] = (
                    current_conn_occ.get(conn_key, 0) + 1
                )

                self.zone_occupancy[next_name] = (
                    self.zone_occupancy.get(next_name, 0) + 1
                )
                self.zone_occupancy[curr_name] -= 1

                drone.status = DroneStatus.IN_TRANSIT
                drone.transit_connection = conn_key

                conn_name = self._get_conn_name(curr_name, next_name)
                turn_moves.append(f"D{drone.id}-{conn_name}")
                acted_this_turn.add(drone.id)
            else:
                current_conn_occ[conn_key] = (
                    current_conn_occ.get(conn_key, 0) + 1
                )

                self.zone_occupancy[curr_name] -= 1
                self.zone_occupancy[next_name] = (
                    self.zone_occupancy.get(next_name, 0) + 1
                )

                drone.path_index += 1
                if drone.path_index == len(drone.path) - 1:
                    drone.status = DroneStatus.DELIVERED

                turn_moves.append(f"D{drone.id}-{next_name}")
                acted_this_turn.add(drone.id)

        # Sort all moves for this turn by drone ID
        turn_moves.sort(key=lambda move: int(move.split("-", 1)[0][1:]))
        return turn_moves

    def run(self) -> list[list[str]]:
        """Run the simulation to completion.

        Returns:
            A list of turns, where each turn contains a list of move strings.

        Raises:
            RuntimeError: If the simulation exceeds safety turn
                limits (deadlock).
        """
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
