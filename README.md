*This project has been created as part of the 42 curriculum by rmesropy.*

## Description
Fly-in is an efficient drone routing simulator designed to navigate a fleet of drones through a connected network of zones from a starting hub to a destination hub. The core objective is to minimize the total number of simulation turns while strictly adhering to complex movement constraints. The simulation enforces zone capacities, connection link capacities, and specific behavioral rules for different zone types (normal, priority, restricted, and blocked). The project is built entirely from scratch in Python 3, emphasizing a fully object-oriented architecture and static type safety without the use of external graph libraries.

## Instructions
The project includes a `Makefile` to automate environment setup, execution, and testing. 

**1. Installation:**
Install the required dependencies (requires a virtual environment).
```bash
make install
```

**2. Execution (Standard CLI Mode):**
Run the simulation on a specific map file. The output will print the turn-by-turn movements.
```bash
make run ARGS="maps/02_circular_loop.txt"
```

**3. Execution (Visualizer Mode):**
Run the simulation with the 2D Matplotlib animation UI.
```bash
make run ARGS="maps/02_circular_loop.txt --visual"
```

**4. Code Quality & Testing:**
Run strict type checking (`mypy`), linting (`flake8`), and cache cleanup.
```bash
make lint
make clean
```

## Algorithm Explanation & Design Decisions
The system relies on a custom-built Graph data structure and is strictly object-oriented.
* **Pathfinding:** The project implements Dijkstra's algorithm to calculate the optimal weighted route for each drone. Movement costs are dynamically evaluated based on zone types: Normal and Priority zones cost 1 turn, while Restricted zones cost 2 turns. The algorithm explicitly prefers Priority zones during route calculations to optimize overall traffic flow.
* **Multi-Agent Path Finding (MAPF):** The simulation engine orchestrates drone movements turn-by-turn. It processes voluntary moves sequentially based on drone ID to ensure predictable and sorted execution.
* **Capacity Management:** A dynamic reservation system tracks real-time `zone_occupancy` and `connection_occupancy`. Drones are only allowed to move if both the target connection's `max_link_capacity` and the target zone's `max_drones` limits are respected, effectively preventing deadlocks and overpopulation.
* **Restricted Zone Transits:** Movement into Restricted zones is handled as an atomic two-turn sequence. The engine prioritizes forced arrivals (drones completing their second turn of transit) before evaluating voluntary moves, guaranteeing network throughput and strict formatting compliance.

## Visual Representation
The project features a 2D animation visualizer built with Matplotlib to provide clear, actionable feedback on the network state and enhance the user experience:
* **Color-Coded Network:** Nodes (zones) and edges (connections) are rendered dynamically based on their metadata. The visualizer explicitly uses the colors specified in the map file (e.g., `[color=blue]`), allowing for immediate visual identification of different zone types and bottlenecks.
* **Live Animation:** Drones are represented by dots that smoothly transition along the connection edges between turns using mathematical easing functions.
* **Real-Time Telemetry:** An overlay displays the current turn number, the count of actively moving drones, and the total number of successfully delivered drones, providing a clear understanding of the simulation's progress.

## Example Input & Expected Output
**Input Map (example.txt):**
```text
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: tunnel 1 0 [zone=restricted color=red]
end_hub: goal 2 0 [color=yellow]

connection: start-tunnel
connection: tunnel-goal
```

**Expected Output:**
```text
D1-start-tunnel D2-start-tunnel
D1-tunnel D2-tunnel
D1-goal D2-goal
```

## Resources & AI Usage
* **Graph Theory:** Classic Multi-Agent Path Finding (MAPF) concepts and adjacency list representations were utilized to structure the core routing logic without relying on `networkx`.
* **AI Assistance:** Artificial Intelligence (LLM) was utilized ethically as a thought partner throughout development. Specific use cases included:
  * Structuring the Python OOP architecture and standardizing strict typing (`mypy`) practices.
  * Formulating the logic to correctly format hyphenated connection names for restricted zone transits.
  * Debugging third-party library states, specifically resolving a Matplotlib `IndexError` related to safely updating empty 2D coordinate arrays during the visualizer's animation loop.