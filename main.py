"""CLI entry point: wires Parser -> Graph -> Simulator -> Renderer together.

TODO:
- argument parsing (map file path, drone count override if any, --visual flag)
- run the simulation, print the turn log in the required format
"""

import sys

from fly_in.parser import MapParseError, MapParser


def main() -> None:
    """Parse and display a Fly-in map."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        return

    filename = sys.argv[1]

    try:
        parsed_map = MapParser().parse(filename)
    except MapParseError as exc:
        print(f"Error: {exc}")
        return
    except OSError as exc:
        print(f"Error: cannot open map file: {exc}")
        return

    graph = parsed_map.graph

    print(f"Drones: {parsed_map.nb_drones}")
    print(f"Start: {parsed_map.start_hub}")
    print(f"End: {parsed_map.end_hub}")
    print(f"Zones: {graph.zone_count()}")
    print(f"Connections: {graph.connection_count()}")

    print("\nNeighbors:")
    for zone_name in (
        parsed_map.start_hub,
        parsed_map.end_hub,
    ):
        print(
            f"  {zone_name}: "
            f"{graph.neighbors(zone_name)}"
        )


if __name__ == "__main__":
    main()
