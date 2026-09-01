# Save this script as run_benchmarks.py in your root directory and run: python run_benchmarks.py

import glob
from pathlib import Path
from fly_in.parser import MapParser
from fly_in.pathfinding import PathFinder
from fly_in.drone import Drone
from fly_in.simulator import Simulator

targets = {
    "01_linear_path.txt": 6,
    "02_simple_fork.txt": 8,
    "03_basic_capacity.txt": 6,
    "01_dead_end_trap.txt": 12,
    "02_circular_loop.txt": 15,
    "03_priority_puzzle.txt": 12,
    "01_maze_nightmare.txt": 30,
    "02_capacity_hell.txt": 35,
    "03_ultimate_challenge.txt": 45,
    "01_the_impossible_dream.txt": 45,
}

parser = MapParser()
finder = PathFinder()

print(f"{'Map Name':<32} | {'Drones':<6} | {'Turns':<6} | {'Target':<6} | {'Status'}")
print("-" * 72)

for map_path in sorted(glob.glob("maps/*.txt")):
    filename = Path(map_path).name
    try:
        parsed = parser.parse(map_path)
        path = finder.dijkstra(parsed.graph, parsed.start_hub, parsed.end_hub)
        if not path:
            print(f"{filename:<32} | {parsed.nb_drones:<6} | {'FAIL':<6} | {targets.get(filename, '-'):<6} | No path")
            continue
        
        drones = [Drone(id=i, path=[z.name for z in path]) for i in range(1, parsed.nb_drones + 1)]
        sim = Simulator(parsed.graph, drones, end_hub=parsed.end_hub)
        turns = sim.run()
        
        turn_count = len(turns)
        target = targets.get(filename, "-")
        status = "PASS" if isinstance(target, int) and turn_count <= target else ("OVER TARGET" if target != "-" else "OPTIONAL")
        
        print(f"{filename:<32} | {parsed.nb_drones:<6} | {turn_count:<6} | {target:<6} | {status}")
    except Exception as e:
        print(f"{filename:<32} | Error: {e}")