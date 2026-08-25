# """CLI entry point: wires Parser -> Graph -> Simulator -> Renderer together.

# TODO:
# - argument parsing (map file path, drone count override if any, --visual flag)
# - run the simulation, print the turn log in the required format
# """

# import sys

# from fly_in.parser import MapParseError, MapParser


# def main() -> None:
#     """Parse and display a Fly-in map."""
#     if len(sys.argv) != 2:
#         print("Usage: python main.py <map_file>")
#         return

#     filename = sys.argv[1]

#     try:
#         parsed_map = MapParser().parse(filename)
#     except MapParseError as exc:
#         print(f"Error: {exc}")
#         return
#     except OSError as exc:
#         print(f"Error: cannot open map file: {exc}")
#         return

#     graph = parsed_map.graph

#     print(f"Drones: {parsed_map.nb_drones}")
#     print(f"Start: {parsed_map.start_hub}")
#     print(f"End: {parsed_map.end_hub}")
#     print(f"Zones: {graph.zone_count()}")
#     print(f"Connections: {graph.connection_count()}")

#     print("\nNeighbors:")
#     for zone_name in (
#         parsed_map.start_hub,
#         parsed_map.end_hub,
#     ):
#         print(
#             f"  {zone_name}: "
#             f"{graph.neighbors(zone_name)}"
#         )


# if __name__ == "__main__":
#     main()
import sys
from pathlib import Path

from fly_in.drone import Drone
from fly_in.parser import MapParser, MapParseError
from fly_in.pathfinding import PathFinder
from fly_in.simulator import Simulator


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_map.txt>", file=sys.stderr)
        sys.exit(1)

    map_path = sys.argv[1]
    if not Path(map_path).is_file():
        print(f"Error: File '{map_path}' not found.", file=sys.stderr)
        sys.exit(1)

    parser = MapParser()
    try:
        parsed_map = parser.parse(map_path)
    except MapParseError as e:
        print(f"Parsing Error: {e}", file=sys.stderr)
        sys.exit(1)

    finder = PathFinder()
    path_zones = finder.dijkstra(parsed_map.graph, parsed_map.start_hub, parsed_map.end_hub)

    if not path_zones:
        print("Error: No valid path found between hubs!", file=sys.stderr)
        sys.exit(1)

    path_names = [z.name for z in path_zones]

    drones = [
        Drone(id=i, path=path_names)
        for i in range(1, parsed_map.nb_drones + 1)
    ]

    simulator = Simulator(parsed_map.graph, drones, end_hub=parsed_map.end_hub)

    try:
        turns = simulator.run()
        
        total_turns = 0
        for turn_moves in turns:
            if turn_moves:
                total_turns += 1
                print(" ".join(turn_moves))
        
        # Вывод статистики в конце
        print("\n==============================")
        print("Stats")
        print("==============================")
        print(f"Drones Deliverd: {parsed_map.nb_drones}")
        print(f"Path len:    {len(path_names) - 1} steps")
        print(f"Finded Path:   {' -> '.join(path_names)}")
        print(f"Total moves:       {total_turns}")
        print("==============================")
                
    except RuntimeError as e:
        print(f"Simulation Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()