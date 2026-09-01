"""The Graph: your own adjacency-list based graph structure.

No networkx, no graphlib -- this is the whole point of the project.
"""

from .models import Connection, Zone


class Graph:
    """Represent the Fly-in network as an adjacency graph."""

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._zones: dict[str, Zone] = {}
        self._adjacency: dict[str, dict[str, Connection]] = {}

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: Zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self._zones:
            raise ValueError(
                f"Zone '{zone.name}' already exists"
            )

        self._zones[zone.name] = zone
        self._adjacency[zone.name] = {}

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional connection between two existing zones.

        Args:
            connection: Connection to add.

        Raises:
            ValueError: If a referenced zone does not exist or if the
                connection already exists.
        """
        zone_a = connection.zone_a
        zone_b = connection.zone_b

        if zone_a not in self._zones:
            raise ValueError(
                f"Zone '{zone_a}' does not exist"
            )

        if zone_b not in self._zones:
            raise ValueError(
                f"Zone '{zone_b}' does not exist"
            )

        if zone_b in self._adjacency[zone_a]:
            raise ValueError(
                f"Connection '{zone_a}-{zone_b}' already exists"
            )

        self._adjacency[zone_a][zone_b] = connection
        self._adjacency[zone_b][zone_a] = connection

    def get_zone(self, name: str) -> Zone:
        """Return a zone by name.

        Args:
            name: Name of the zone.

        Returns:
            The requested zone.

        Raises:
            KeyError: If the zone does not exist.
        """
        return self._zones[name]

    def neighbors(self, zone_name: str) -> list[str]:
        """Return the names of zones directly connected to a zone.

        Args:
            zone_name: Name of the zone.

        Returns:
            List of neighboring zone names.

        Raises:
            KeyError: If the zone does not exist.
        """
        if zone_name not in self._zones:
            raise KeyError(
                f"Zone '{zone_name}' does not exist"
            )

        return list(self._adjacency[zone_name].keys())

    def get_connection(
        self,
        zone_a: str,
        zone_b: str,
    ) -> Connection:
        """Return the connection between two zones.

        Args:
            zone_a: First zone name.
            zone_b: Second zone name.

        Returns:
            The connection between the zones.

        Raises:
            KeyError: If either zone does not exist or no connection
                exists between them.
        """
        if zone_a not in self._zones:
            raise KeyError(
                f"Zone '{zone_a}' does not exist"
            )

        if zone_b not in self._adjacency[zone_a]:
            raise KeyError(
                f"No connection between '{zone_a}' and '{zone_b}'"
            )

        return self._adjacency[zone_a][zone_b]

    def all_zones(self) -> dict[str, Zone]:
        """Return every zone in the graph, keyed by name.

        Returns:
            A shallow copy of the internal zone mapping -- safe to
            iterate without risking mutation of the graph's own state.
        """
        return dict(self._zones)

    def all_connections(self) -> list[Connection]:
        """Return every connection in the graph, each listed once.

        Returns:
            A list of Connection objects (a-b and b-a are the same
            connection and appear only once).
        """
        seen: set[frozenset[str]] = set()
        result: list[Connection] = []
        for zone_a, neighbors in self._adjacency.items():
            for zone_b, connection in neighbors.items():
                key = frozenset((zone_a, zone_b))
                if key not in seen:
                    seen.add(key)
                    result.append(connection)
        return result

    def has_zone(self, name: str) -> bool:
        """Return whether a zone exists in the graph.

        Args:
            name: Zone name.

        Returns:
            True if the zone exists, otherwise False.
        """
        return name in self._zones

    def zone_count(self) -> int:
        """Return the number of zones in the graph."""
        return len(self._zones)

    def connection_count(self) -> int:
        """Return the number of unique connections in the graph."""
        total = sum(
            len(neighbors)
            for neighbors in self._adjacency.values()
        )
        return total // 2
