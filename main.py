"""CLI entry point for the Fly-in simulation."""

from pathlib import Path
import sys

from fly_in.drone import Drone
from fly_in.formatter import OutputFormatter
from fly_in.parser import MapParseError, MapParser
from fly_in.pathfinding import PathFinder
from fly_in.simulator import Simulator


def main() -> None:
    """Parse, pathfind, simulate and optionally render a Fly-in map."""
    args = sys.argv[1:]

    visual_mode = "--visual" in args
    if visual_mode:
        args.remove("--visual")

    if len(args) != 1:
        print(
            "Usage: python main.py [--visual] <path_to_map.txt>",
            file=sys.stderr,
        )
        sys.exit(1)

    map_path = args[0]

    if not Path(map_path).is_file():
        print(
            f"Error: File '{map_path}' not found.",
            file=sys.stderr,
        )
        sys.exit(1)

    parser = MapParser()

    try:
        parsed_map = parser.parse(map_path)
    except MapParseError as error:
        print(
            f"Parsing Error: {error}",
            file=sys.stderr,
        )
        sys.exit(1)

    finder = PathFinder()
    path_zones = finder.dijkstra(
        parsed_map.graph,
        parsed_map.start_hub,
        parsed_map.end_hub,
    )

    if not path_zones:
        print(
            "Error: No valid path found between hubs!",
            file=sys.stderr,
        )
        sys.exit(1)

    path_names = [zone.name for zone in path_zones]

    drones = [
        Drone(
            id=i,
            path=path_names,
        )
        for i in range(1, parsed_map.nb_drones + 1)
    ]

    simulator = Simulator(
        parsed_map.graph,
        drones,
        end_hub=parsed_map.end_hub,
    )

    try:
        turns = simulator.run()

        formatter = OutputFormatter()
        output = formatter.format(turns)
        print(output)

        print("\n==============================")
        print("Stats")
        print("==============================")
        print(
            f"Drones Delivered: {parsed_map.nb_drones}"
        )
        print(
            f"Path len:         {len(path_names) - 1} steps"
        )
        print(
            f"Total turns:      {len(turns)}"
        )
        print("==============================")

        if visual_mode:
            from fly_in.visualizer import MapVisualizer

            print("Launching Matplotlib visualizer...")
            visualizer = MapVisualizer(parsed_map, turns)
            visualizer.play()

    except RuntimeError as error:
        print(
            f"Simulation Error: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
