"""Map file parser: text file -> ParsedMap (Graph, nb_drones, hubs).

Reads a Fly-in map file line by line, dispatching on the line's prefix
(nb_drones: / start_hub: / end_hub: / hub: / connection:), and builds
a Graph out of it. Enforces every structural rule from subject chapter
VII.4, raising MapParseError with the offending line number and a clear reason.
"""

from dataclasses import dataclass

from .graph import Graph
from .models import Connection, Zone, ZoneType


class MapParseError(Exception):
    """Represent an error while parsing a Fly-in map."""

    def __init__(self, line_number: int, message: str) -> None:
        """Initialize a map parsing error.

        Args:
            line_number: Number of the invalid line.
            message: Explanation of the parsing problem.
        """
        self.line_number = line_number
        self.message = message
        super().__init__(f"Line {line_number}: {message}")


@dataclass
class ParsedMap:
    """Contain all data parsed from a Fly-in map."""

    graph: Graph
    nb_drones: int
    start_hub: str
    end_hub: str


class MapParser:
    """Parse a Fly-in map file into a graph."""

    _ZONE_TYPES = {
        ZoneType.NORMAL.value: ZoneType.NORMAL,
        ZoneType.BLOCKED.value: ZoneType.BLOCKED,
        ZoneType.RESTRICTED.value: ZoneType.RESTRICTED,
        ZoneType.PRIORITY.value: ZoneType.PRIORITY,
    }

    def parse(self, filename: str) -> ParsedMap:
        """Parse a map file.

        Args:
            filename: Path to the map file.

        Returns:
            Parsed map containing the graph and simulation metadata.

        Raises:
            MapParseError: If the map is invalid.
            OSError: If the file cannot be opened.
        """
        graph = Graph()
        nb_drones: int | None = None
        start_hub: str | None = None
        end_hub: str | None = None
        first_meaningful_line_seen = False

        with open(filename, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                if not first_meaningful_line_seen:
                    first_meaningful_line_seen = True
                    if not line.startswith("nb_drones:"):
                        self._error(
                            line_number,
                            "nb_drones must be the first line",
                        )

                try:
                    if line.startswith("nb_drones:"):
                        if nb_drones is not None:
                            self._error(
                                line_number,
                                "duplicate nb_drones definition",
                            )
                        nb_drones = self._parse_nb_drones(
                            line,
                            line_number,
                        )

                    elif line.startswith("start_hub:"):
                        if start_hub is not None:
                            self._error(
                                line_number,
                                "duplicate start_hub definition",
                            )
                        zone = self._parse_zone(
                            line,
                            line_number,
                            "start_hub",
                        )
                        graph.add_zone(zone)
                        start_hub = zone.name

                    elif line.startswith("end_hub:"):
                        if end_hub is not None:
                            self._error(
                                line_number,
                                "duplicate end_hub definition",
                            )
                        zone = self._parse_zone(
                            line,
                            line_number,
                            "end_hub",
                        )
                        graph.add_zone(zone)
                        end_hub = zone.name

                    elif line.startswith("hub:"):
                        zone = self._parse_zone(
                            line,
                            line_number,
                            "hub",
                        )
                        graph.add_zone(zone)

                    elif line.startswith("connection:"):
                        connection = self._parse_connection(
                            line,
                            line_number,
                        )
                        graph.add_connection(connection)

                    else:
                        self._error(
                            line_number,
                            "unknown line type",
                        )

                except ValueError as exc:
                    self._error(line_number, str(exc))

        if nb_drones is None:
            raise MapParseError(
                0,
                "missing nb_drones definition",
            )

        if start_hub is None:
            raise MapParseError(
                0,
                "missing start_hub definition",
            )

        if end_hub is None:
            raise MapParseError(
                0,
                "missing end_hub definition",
            )

        return ParsedMap(
            graph=graph,
            nb_drones=nb_drones,
            start_hub=start_hub,
            end_hub=end_hub,
        )

    def _parse_nb_drones(
        self,
        line: str,
        line_number: int,
    ) -> int:
        """Parse the number of drones."""
        prefix = "nb_drones:"
        value = line[len(prefix):].strip()

        if not value.isdigit():
            self._error(
                line_number,
                "nb_drones must be a positive integer",
            )

        nb_drones = int(value)

        if nb_drones <= 0:
            self._error(
                line_number,
                "nb_drones must be a positive integer",
            )

        return nb_drones

    def _parse_zone(
        self,
        line: str,
        line_number: int,
        prefix_name: str,
    ) -> Zone:
        """Parse a zone definition."""
        prefix = f"{prefix_name}:"
        content = line[len(prefix):].strip()

        metadata: dict[str, str] = {}

        if "[" in content or "]" in content:
            if not content.endswith("]"):
                self._error(
                    line_number,
                    "malformed metadata block",
                )

            metadata_start = content.rfind("[")

            if metadata_start == -1:
                self._error(
                    line_number,
                    "malformed metadata block",
                )

            metadata_text = content[
                metadata_start + 1:-1
            ].strip()

            content = content[:metadata_start].strip()
            metadata = self._parse_metadata(
                metadata_text,
                line_number,
            )

        parts = content.split()

        if len(parts) != 3:
            self._error(
                line_number,
                "zone must have name, x and y coordinates",
            )

        name, x_text, y_text = parts

        self._validate_zone_name(
            name,
            line_number,
        )

        try:
            x = int(x_text)
            y = int(y_text)
        except ValueError:
            self._error(
                line_number,
                "zone coordinates must be integers",
            )

        zone_type = self._parse_zone_type(
            metadata,
            line_number,
        )

        color = metadata.get("color")

        max_drones: int | None
        if prefix_name in ("start_hub", "end_hub"):
            max_drones = None
        else:
            max_drones = self._parse_positive_metadata(
                metadata,
                "max_drones",
                1,
                line_number,
            )

        return Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

    def _parse_connection(
        self,
        line: str,
        line_number: int,
    ) -> Connection:
        """Parse a connection definition."""
        prefix = "connection:"
        content = line[len(prefix):].strip()

        metadata: dict[str, str] = {}

        if "[" in content or "]" in content:
            if not content.endswith("]"):
                self._error(
                    line_number,
                    "malformed metadata block",
                )

            metadata_start = content.rfind("[")

            if metadata_start == -1:
                self._error(
                    line_number,
                    "malformed metadata block",
                )

            metadata_text = content[
                metadata_start + 1:-1
            ].strip()

            content = content[:metadata_start].strip()
            metadata = self._parse_metadata(
                metadata_text,
                line_number,
            )

        if not content:
            self._error(
                line_number,
                "connection cannot be empty",
            )

        if content.count("-") != 1:
            self._error(
                line_number,
                "connection must have exactly two zone names "
                "separated by '-'",
            )

        zone_a, zone_b = content.split("-")

        zone_a = zone_a.strip()
        zone_b = zone_b.strip()

        if not zone_a or not zone_b:
            self._error(
                line_number,
                "connection must contain two zone names",
            )

        max_link_capacity = self._parse_positive_metadata(
            metadata,
            "max_link_capacity",
            1,
            line_number,
        )

        return Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity,
        )

    def _parse_metadata(
        self,
        text: str,
        line_number: int,
    ) -> dict[str, str]:
        """Parse a metadata block."""
        if not text:
            return {}

        metadata: dict[str, str] = {}

        for item in text.split():
            if "=" not in item:
                self._error(
                    line_number,
                    f"invalid metadata item '{item}'",
                )

            key, value = item.split("=", 1)

            if not key or not value:
                self._error(
                    line_number,
                    f"invalid metadata item '{item}'",
                )

            if key in metadata:
                self._error(
                    line_number,
                    f"duplicate metadata key '{key}'",
                )

            metadata[key] = value

        return metadata

    def _parse_zone_type(
        self,
        metadata: dict[str, str],
        line_number: int,
    ) -> ZoneType:
        """Parse the zone type from metadata."""
        value = metadata.get(
            "zone",
            ZoneType.NORMAL.value,
        )

        if value not in self._ZONE_TYPES:
            self._error(
                line_number,
                f"invalid zone type '{value}'",
            )

        return self._ZONE_TYPES[value]

    def _parse_positive_metadata(
        self,
        metadata: dict[str, str],
        key: str,
        default: int,
        line_number: int,
    ) -> int:
        """Parse a positive integer metadata value."""
        if key not in metadata:
            return default

        value = metadata[key]

        if not value.isdigit():
            self._error(
                line_number,
                f"{key} must be a positive integer",
            )

        number = int(value)

        if number <= 0:
            self._error(
                line_number,
                f"{key} must be a positive integer",
            )

        return number

    def _validate_zone_name(
        self,
        name: str,
        line_number: int,
    ) -> None:
        """Validate a zone name."""
        if not name:
            self._error(
                line_number,
                "zone name cannot be empty",
            )

        if "-" in name:
            self._error(
                line_number,
                f"zone name '{name}' cannot contain '-'",
            )

        if any(char.isspace() for char in name):
            self._error(
                line_number,
                f"zone name '{name}' cannot contain spaces",
            )

    @staticmethod
    def _error(
        line_number: int,
        message: str,
    ) -> None:
        """Raise a line-numbered parsing error."""
        raise MapParseError(line_number, message)
