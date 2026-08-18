# Fly-in — Your 14-Day Roadmap (Zero to Submission)

*A step-by-step plan for a project you don't know yet, covering graph theory, Python, and everything in between — written so anyone could pick this up and follow it.*

---

## 0. Before anything: what is "Fly-in", in plain words?

Strip away the drone theme and Fly-in is this: **you write a Python program that moves a fleet of "drones" through a small network, one turn at a time, using the fewest turns possible, without breaking traffic rules.**

- The "network" is a **graph**: places (called *zones*) connected by *connections*. This is handed to you as a text file.
- Some zones cost more to enter (a `restricted` zone costs 2 turns and has a weird "no waiting mid-flight" rule), some are forbidden (`blocked`), some are simply nicer to use (`priority`).
- Zones and connections have a **capacity** — only so many drones can be in a zone or crossing a connection at the same time.
- Every "turn," every drone can move to a neighboring zone, or wait. You print out what happened that turn.
- You are **not allowed to use any graph library** (no `networkx`, no `graphlib`) — you build the graph data structure and every algorithm on it yourself.
- The code must be **fully object-oriented**, fully **type-checked** (`mypy`), **lint-clean** (`flake8`), documented, tested, and shipped with a `Makefile` and a `README.md` in a specific shape.
- You'll be peer-reviewed, and may be asked to explain or live-edit your code — so "I don't fully understand this part" is not a safe place to be on submission day.

That's the whole project. Everything below is how to get there in 14 days, in order, without drowning.

---

## 1. Quick map of the 14 days

| Day | Focus | You'll walk away with |
|---|---|---|
| 1 | Orientation + project setup | Repo skeleton, tooling installed, spec fully understood |
| 2 | Graph traversal basics (BFS/DFS) | Hand-written BFS/DFS on a toy graph, tested |
| 3 | Object model + file parser | `Zone`, `Connection`, `Graph`, working parser with error handling |
| 4 | Weighted shortest path | `Dijkstra`/`A*` routing a single drone correctly |
| 5 | Multi-agent scheduling theory | A written design for handling many drones at once |
| 6–7 | Simulation engine | Working turn-by-turn simulator, single-drone-safe |
| 8 | Conflict resolution & deadlocks | Simulator handles many drones without collisions or hangs |
| 9 | Output format | Output matches the required format exactly |
| 10 | Visual representation | Colored terminal (and optionally graphical) live view |
| 11 | Benchmarking & tuning | Turn counts measured against every target in the spec |
| 12 | Code quality pass | Clean `flake8` + `mypy --strict`, full docstrings |
| 13 | Makefile, README, tests | All non-code deliverables finished |
| 14 | Buffer + rehearsal + bonus | Ready to explain/modify code live; bonus attempted if time allows |

---

## 2. Vocabulary — read once, then use this as a glossary

| Term | Plain meaning |
|---|---|
| **Node / vertex** | A "place" in a graph. Here: a zone. |
| **Edge** | A connection between two nodes. Here: a connection between two zones. |
| **Weighted graph** | A graph where moving along an edge (or into a node) has a cost — here, the cost depends on the destination zone's type. |
| **Directed / undirected** | Directed = one-way edges. Undirected = two-way. Your connections are two-way (bidirectional). |
| **Adjacency list** | The standard way to store a graph in code: for each node, a list of the nodes it connects to. Efficient when most nodes *aren't* connected to most other nodes (true here). |
| **BFS (Breadth-First Search)** | Explore a graph level by level using a queue. Finds the path with the fewest *edges* — not necessarily the cheapest one. |
| **DFS (Depth-First Search)** | Explore as deep as possible before backtracking, using recursion or a stack. Good for checking "can I reach X at all," or detecting cycles. |
| **Dijkstra's algorithm** | Finds the cheapest path in a weighted graph (all costs positive) by always expanding the currently-cheapest-known node next, using a priority queue. |
| **A\*** | Dijkstra plus a *heuristic* guess of remaining distance (you have real x,y coordinates, so straight-line distance works) — usually faster in practice. |
| **Heuristic** | An estimate used to guide search toward the goal faster, without sacrificing correctness (if it never overestimates). |
| **Priority queue / heap** | A data structure that always gives you the smallest item first — Python's `heapq` module implements one. Core to Dijkstra/A*. |
| **MAPF (Multi-Agent Path Finding)** | The academic name for "route many agents through a shared graph without them colliding" — this is the real heart of Fly-in. |
| **Reservation table** | A lookup of "which zone/connection is occupied at which turn by which drone" — how you prevent collisions when many drones move at once. |
| **Deadlock** | Two or more drones each waiting on a zone the other currently occupies — nobody can ever move again unless you detect and break it. |
| **OOP (Object-Oriented Programming)** | Structuring code as classes with responsibilities (a `Graph` manages zones/connections, a `Drone` manages its own state, etc.) rather than one giant script. |
| **Dataclass** | A Python shortcut (`@dataclass`) for writing small typed "data holder" classes without boilerplate. |
| **Type hint / static typing** | Annotating variables and functions with expected types (`def foo(x: int) -> str:`) so a tool can catch mismatches before you run the code. |
| **`mypy`** | A static type checker — reads your type hints and flags inconsistencies without running your program. |
| **`flake8`** | A linter — flags style issues, unused imports, and common bugs. |
| **Docstring / PEP 257** | The standard way to document a Python function/class in a string right under its definition. |
| **Context manager (`with`)** | Python's way of guaranteeing cleanup (e.g., `with open(file) as f:` always closes the file, even on error). |
| **Makefile** | A file defining shortcut commands (`make install`, `make run`, etc.) so anyone can operate your project the same way. |
| **venv** | Python's built-in virtual environment tool — isolates your project's dependencies from your system Python. |

---

## 3. The shape of the solution (architecture)

You don't have to copy this exactly, but this is a sane, defensible OOP breakdown — and having a plan here on Day 1 saves you from a messy rewrite on Day 8.

```
fly_in/
├── fly_in/
│   ├── __init__.py
│   ├── models.py        # Zone, Connection, ZoneType (dataclasses + enum)
│   ├── graph.py          # Graph: stores zones + adjacency, exposes neighbors()
│   ├── parser.py         # reads a map file -> Graph + drone count, raises MapParseError
│   ├── pathfinding.py     # Dijkstra / A* on a Graph
│   ├── drone.py           # Drone: id, position, status, path, transit state
│   ├── simulator.py       # Scheduler/turn engine: reservation table, step(), run()
│   ├── renderer.py        # colored terminal / graphical output, kept separate from logic
│   └── main.py            # CLI entry point, wires everything together
├── maps/                  # provided maps + your own edge-case maps
├── tests/                 # pytest tests (not graded, but save you in peer review)
├── Makefile
├── .gitignore
└── README.md
```

**Why split it this way?** Each class has one job (single responsibility). The `Parser` doesn't know about pathfinding. The `Simulator` doesn't know how to draw itself. This is exactly what a peer reviewer will poke at when checking "is this really OO?" — and it's also just easier for *you* to reason about and test in isolation.

---

## 4. Day-by-day plan

### Day 1 — Orient yourself & set up shop

**Goal:** Fully understand the rules, and get a working, lint-ready repo skeleton before writing any real logic.

**Why:** Coding before understanding the constraints (zone costs, capacity exceptions at start/end, the "no waiting mid-flight on a restricted connection" rule) guarantees a rewrite later. Tooling set up on Day 1 means every day after this passes lint from the start instead of a scramble on Day 12.

**Learn:**
- What a graph is: nodes, edges, weighted vs. unweighted, directed vs. undirected.
- Adjacency list representation (vs. matrix) and why it fits a sparse graph like this one.
- Resources: [visualgo.net](https://visualgo.net/en) (interactive graph visualizations), any "intro to graphs" lecture from a data structures course (MIT 6.006 and CS50 both have free lecture videos on graphs — search "graphs" on their YouTube channels).

**Build:**
- `git init`, create the folder structure above.
- `python3 -m venv venv && source venv/bin/activate`
- `pip install flake8 mypy pytest rich` (or `colorama` — `rich` is more powerful for a grid-like live view).
- Write a `Makefile` skeleton with `install`, `run`, `debug`, `clean`, `lint`, `lint-strict` targets (they can be near-empty stubs today — just runnable).
- Write `.gitignore` (`venv/`, `__pycache__/`, `.mypy_cache/`, `*.pyc`, `.pytest_cache/`).
- Re-read the project subject slowly. For every rule (zone types + costs, capacity exceptions on start/end zones, restricted-zone "must arrive next turn" rule, output format), write one sentence of it in your own words in a `NOTES.md`. If you can't paraphrase a rule, you don't understand it yet — that's exactly what to ask about (me, a peer, or your own re-reading) before Day 3.

**Done when:** repo is pushed with the skeleton, `make lint` runs (even against near-empty files), and you can explain out loud what each of the four zone types costs and why start/end zones are special.

**Watch out for:** the urge to start pathfinding today. You don't have a `Graph` class yet — there's nothing to path-find on.

---

### Day 2 — Graph traversal fundamentals (BFS & DFS), on a toy graph

**Goal:** Hand-implement BFS and DFS from scratch on a disposable toy graph — not your project's real classes yet — until the algorithm is muscle memory.

**Why:** the library ban means you *will* write these yourself eventually; doing it once on a simple `dict[str, list[str]]` graph means that when you build it for real on Day 3–4, you're debugging your parser, not the algorithm.

**Learn:**
- BFS: explore neighbor-by-neighbor using a FIFO queue; the first time you reach a node is via the fewest edges.
- DFS: explore as deep as possible, using recursion or an explicit stack; useful for "can this node reach that node at all," and for cycle detection.
- Resources: [visualgo.net/en/dfsbfs](https://visualgo.net/en/dfsbfs) (step through both algorithms visually), Python's own `collections.deque` for an efficient FIFO queue.

**Build:** In a throwaway script (not part of the final submission), represent a small graph as `dict[str, list[str]]`, write `bfs(graph, start, goal) -> list[str] | None` and a `dfs_reachable(graph, start) -> set[str]`. Write 3–4 `pytest` cases, including a graph with no path between two nodes.

**Done when:** BFS returns the correct fewest-edges path on three different toy graphs, including a disconnected one (returns `None` cleanly, no crash).

**Watch out for:** forgetting a `visited` set (infinite loop on cycles); forgetting the project's graph is *bidirectional* — add both directions when you build the real adjacency list later.

---

### Day 3 — Object model + the parser

**Goal:** Turn the map-file format into a working, typed object model.

**Why:** OOP design is graded, and the parser is the foundation everything else stands on — a shaky `Graph` class means shaky pathfinding, simulation, and output.

**Learn:**
- `@dataclass` for lightweight, typed data-holder classes.
- `enum.Enum` for `ZoneType` (`NORMAL`, `BLOCKED`, `RESTRICTED`, `PRIORITY`) — avoids "stringly-typed" bugs where a typo silently does nothing.
- Designing a custom exception (e.g. `class MapParseError(Exception)`) that carries a line number and reason, so parsing failures are debuggable, not cryptic.
- Resources: [docs.python.org/3/library/dataclasses.html](https://docs.python.org/3/library/dataclasses.html), [docs.python.org/3/library/enum.html](https://docs.python.org/3/library/enum.html)

**Build:**
- `Zone` dataclass: `name: str, x: int, y: int, zone_type: ZoneType, color: str | None, max_drones: int`.
- `Connection` dataclass: `zone_a: str, zone_b: str, max_link_capacity: int`.
- `Graph` class: internal `dict[str, Zone]` for zones and an adjacency structure for connections; methods like `add_zone()`, `add_connection()`, `neighbors(zone_name)`.
- `Parser`: reads the file line by line, dispatches on the line prefix (`nb_drones:`, `start_hub:`, `end_hub:`, `hub:`, `connection:`, `#` for comments), parses the `[key=value ...]` metadata blocks, and validates everything the spec requires — unique start/end zone, no duplicate connections (`a-b` and `b-a` count as the same), valid zone types, positive capacities, no dashes/spaces in names.
- Write at least 5 deliberately broken map files (missing start zone, duplicate connection, invalid zone type, negative capacity, dash in a zone name) and assert each raises the right, specific error.

**Done when:** your parser correctly builds a `Graph` from the spec's example map, and cleanly rejects every malformed map you wrote, with a message that names the line and the problem.

**Watch out for:** the spec explicitly says `max_drones` on the start/end zones is *ignored*, not an error — don't over-validate there.

---

### Day 4 — Weighted shortest path (Dijkstra & A*)

**Goal:** Route a single drone correctly from start to end, respecting per-zone-type movement costs.

**Why:** plain BFS finds the fewest *hops*, not the cheapest route once a restricted zone costs double — you need a weighted algorithm. A* becomes valuable on larger maps (hard/challenger) because you have real coordinates for a good heuristic.

**Learn:**
- Dijkstra: repeatedly expand the node with the smallest known cumulative cost, using a min-heap (`heapq`).
- A*: Dijkstra plus a heuristic estimate of remaining cost (straight-line distance from `(x, y)` to the goal works well here).
- Resources: [redblobgames.com/pathfinding/a-star/introduction.html](https://www.redblobgames.com/pathfinding/a-star/introduction.html) — the best free, visual introduction to this exact topic — and [docs.python.org/3/library/heapq.html](https://docs.python.org/3/library/heapq.html).

**Build:** a `PathFinder` class with `dijkstra(graph, start, goal) -> list[Zone]` (and optionally `a_star(...)`). Entering a zone costs whatever its `ZoneType` says; `blocked` zones are simply never expanded. Test against every provided easy map for a single drone, and confirm the path avoids blocked zones and matches the expected minimal cost by hand-checking one map yourself.

**Done when:** you can print the correct cheapest path for a single drone on every provided map, and can explain *why* Dijkstra sometimes prefers a longer-hop-but-cheaper route over a shorter one.

**Watch out for:** scope creep — this only solves routing for *one* drone with no capacity limits. Multi-drone scheduling is tomorrow's problem on purpose.

---

### Day 5 — Understand the real problem: multi-agent scheduling

**Goal:** Shift your mental model from "find a path" to "schedule many drones through time without exceeding any capacity, anywhere, ever."

**Why:** this is the actual hard part of the project, and the reason it's not just "run Dijkstra five times." With multiple drones, zone/connection capacity, and simultaneous movement, drones can now collide with each other, jointly exceed `max_drones`, or conflict over who gets to use a restricted-zone transit slot.

**Learn (concept level — you're designing today, not coding a research-grade solver):**
- Think in **time-expanded** terms: instead of "is this zone free," ask "is this zone free *at turn T*."
- A **reservation table**: something like `dict[(zone_name, turn), drone_id]` (and an equivalent for connections mid-transit) that you check *before* committing any move.
- **Priority-based planning**: order drones somehow (by path length, or simply by ID), plan them one at a time against the reservations already made by earlier drones. It's not globally optimal, but it's implementable in the time you have, and it's a completely legitimate MAPF strategy.
- Optimal solvers like **Conflict-Based Search (CBS)** exist in the research literature, but are a large undertaking — worth knowing the name exists (see the survey below) but not worth chasing unless your mandatory part is done early and you're going for the bonus.
- Resources: skim the introduction and "prioritized planning" sections of Stern et al., *"Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks"* — [arXiv:1906.08291](https://arxiv.org/abs/1906.08291). You don't need the whole paper, just enough to recognize the vocabulary.

**Build:** a written design (a `DESIGN.md` in your repo is fine) describing your `Simulator`/`Scheduler`: what state it holds (reservation table, each drone's position/status/ETA), what happens in a single simulated turn, and — specifically — how you'll represent "this drone entered a restricted-zone connection and *must* arrive next turn, it cannot wait mid-flight."

**Done when:** you have a design, even an informal one, for exactly how your scheduler decides — turn by turn — which drone moves where, and how a restricted transit is treated as an atomic 2-turn commitment rather than two independent 1-turn moves.

**Watch out for:** skipping this design step. This is the part of the project most first attempts get wrong, and a shaky design here is what costs people Days 6–9 in rewrites.

---

### Day 6–7 — Build the turn-by-turn simulation engine

**Goal:** Implement the `Simulator` that actually advances drones turn by turn, using yesterday's design.

**Why:** this is where the parser, graph, and pathfinder become the actual deliverable the grader reads: the turn log.

**Learn:**
- Model each `Drone` as a small state machine: waiting at start → moving → in-transit through a restricted connection → delivered.
- The spec's subtlety: drones **leaving** a zone free its capacity in the *same* turn — so you must compute "who's leaving" before deciding "who's allowed to enter," not process drones one-by-one in isolation.

**Build:**
- **Day 6:** the `Drone` class (id, position, status, planned path, remaining transit turns for restricted moves), plus a first single-turn `step()` that, per drone, asks the `PathFinder` for the next hop and checks it against capacity before committing (or makes the drone wait).
- **Day 7:** the full loop — repeat `step()` until every drone is delivered; collect each turn's moves in the required `D<ID>-<zone>` format (and `D<ID>-<connection>` for drones mid-transit through a restricted connection); make sure drones that don't move are simply omitted from that turn's line.

**Done when:** running your simulator on the spec's worked example produces output with the same *shape* as the example (drones progressing zone by zone, restricted transits shown as `D<ID>-<connection>` for one turn then arriving the next) — not necessarily identical drones or zones, but structurally and logically correct.

**Watch out for:** the classic bug is processing drones in a fixed order and letting drone 1 take a zone slot drone 2 also needed, when computing *all* intended moves first, resolving conflicts, and *then* committing everyone would have let both through. Don't mutate shared state while you're still deciding who gets to move.

---

### Day 8 — Conflict resolution, priority zones, deadlock avoidance

**Goal:** Make the scheduler robust — no collisions, no capacity violations, priority zones genuinely preferred, and no infinite waits.

**Why:** this is what separates "works on the easy map" from something that meets the medium/hard benchmarks the spec lists.

**Learn:**
- **Deadlock**: two or more drones each waiting on a zone the other currently occupies, forever.
- **Livelock**: drones keep shuffling/waiting without net progress.
- Common fixes: detect "swap" conflicts (two drones trying to cross the same single-capacity link in opposite directions in the same turn), assign explicit wait/queue priority when a bottleneck connection is contested (e.g. first-come-first-served by arrival turn), and add a turn-count safety cutoff so a bug becomes a visible failure instead of a silent hang.

**Build:** conflict checks before any move is committed (zone capacity, connection capacity, swap conflicts); a tie-breaking rule that prefers `priority` zones when multiple valid next-hops exist at equal cost; a max-turns cutoff with logging.

**Done when:** every provided medium map solves without hanging, and you can point to at least one case in your output where a priority zone was visibly chosen over an equal-cost alternative.

**Watch out for:** bottleneck connections with `max_link_capacity=1` and several drones needing to cross — decide explicitly (and document) how they queue, rather than leaving it as undefined, order-dependent behavior.

---

### Day 9 — Exact output format

**Goal:** Lock the turn log down to match the required format precisely.

**Why:** it's explicitly part of what's graded — a logically correct simulation with the wrong formatting still fails.

**Learn:** nothing new conceptually — this is a "read the spec twice, implement to the letter" day.

**Build:** a dedicated formatter that takes your per-turn move list and prints one line per turn: space-separated `D<ID>-<target>` tokens, omitting drones that didn't move, stopping once every drone is delivered.

**Done when:** you've compared your output against the spec's worked example line by line, and manually traced two or three of your *own* maps to confirm every line matches what actually happened in the simulation.

---

### Day 10 — Visual representation

**Goal:** Add colored terminal output (the required minimum) and, if time allows, a simple graphical view.

**Why:** it's a required deliverable, and it's also the fastest way for you — and your peer reviewer — to sanity-check that the simulation is doing something sensible, rather than trusting raw text.

**Learn:** ANSI escape codes, or the `rich`/`colorama` libraries (`rich` in particular is well suited to a live-updating grid). For a graphical option with zero extra install, `tkinter` (standard library) is the lowest-effort route: draw zones as circles at their `(x, y)`, connections as lines, and drones as dots that move each turn.

**Build:** a `Renderer` class kept deliberately separate from your `Simulator` (so drawing logic never tangles with simulation logic) that takes the current world state and prints/draws it; wire it to run once per turn behind a `--visual` flag.

**Done when:** you can watch a map solve turn by turn, with zone types and drone positions visibly distinguishable (by color at minimum).

---

### Day 11 — Benchmarking & tuning

**Goal:** Run every provided map, record your turn counts, and compare them against the spec's performance targets.

**Why:** turn count is the primary scoring metric — this is your "how good is my solution, really" day.

**Learn:** basic profiling (`python -m cProfile`) if a hard map runs slowly; whether switching from Dijkstra to A* (using your coordinate heuristic) meaningfully shortens paths or speeds up planning.

**Build:** a small test-runner script that loops over your `maps/` folder, runs the simulator on each, and prints your turn count next to the target from the spec's benchmark table. Iterate on your scheduling heuristics (e.g. give longer-path drones planning priority) until you're meeting — or beating — the targets.

**Done when:** your turn counts meet the spec's stated targets for the easy, medium, and hard maps you have. Attempting the optional Challenger map is a nice-to-have here, not a requirement.

---

### Day 12 — Code quality pass

**Goal:** Get `flake8` and `mypy --strict` fully clean, complete every docstring, and harden error handling.

**Why:** these are explicit grading criteria, and they're far faster to finish now — on a codebase you understand — than they would have been on Day 3 while things were still shifting.

**Learn:**
- PEP 257 docstring conventions — pick a consistent style (Google or NumPy) and stick to it.
- What `mypy --strict` actually checks beyond the baseline flags, and how to read its error messages.
- Using `with` (context managers) for every file handle, so nothing leaks on error.
- Resources: [docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html), [realpython.com/python-type-checking](https://realpython.com/python-type-checking/), PEP 257 on [peps.python.org](https://peps.python.org/pep-0257/).

**Build:** run `flake8 .` and `mypy . --strict` repeatedly, fixing every warning as it appears; wrap parsing/file I/O in `try/except` with clear, user-facing messages instead of raw tracebacks; add a docstring to every public class and function.

**Done when:** `make lint` (and ideally `make lint-strict`) exits with zero warnings.

---

### Day 13 — Makefile, README, tests

**Goal:** Finish every non-code deliverable.

**Why:** the `README.md` and `Makefile` shapes are explicitly specified and graded; tests aren't graded directly, but they're your best evidence in peer review that you actually understand edge cases.

**Learn:** nothing new — this is assembly against the spec's own checklist (attribution line, Description, Instructions, Resources including how you used AI, your algorithm/strategy write-up, documentation of the visual features, and example input/output).

**Build:**
- Finalize the `Makefile` (`install`, `run`, `debug`, `clean`, `lint`, `lint-strict`, exactly as specified).
- Write `README.md`, section by section, against the required list.
- Write `pytest` tests for parser edge cases, BFS/Dijkstra correctness, and at least one full end-to-end simulation run.

**Done when:** someone who has never seen your repo could read the README, run `make install && make run`, and understand what they're looking at without asking you anything.

---

### Day 14 — Buffer, rehearsal, and bonus

**Goal:** Absorb any overrun from earlier days, and get ready for peer review.

**Why:** the evaluation may ask you to explain, or even live-modify, part of your code — you need to be able to walk through your `Graph`, `Scheduler`, and `Parser` from memory, not just have them work.

**Build:** re-read your entire codebase top to bottom, out loud if that helps; write yourself a one-page mental map of your own architecture; if the mandatory part is solid, attempt the bonus (meeting every benchmark target exactly, or the optional Challenger map).

**Done when:** you can explain, unprompted, how a drone travels through a restricted zone and what "must arrive next turn" looks like inside your reservation table — and your repo is pushed, clean, and matches what you'll actually submit.

---

## 5. Mandatory-part definition of done

- [ ] Python 3.10+, fully object-oriented design
- [ ] No graph libraries used anywhere (`networkx`, `graphlib`, etc. are forbidden)
- [ ] Parser reads the map format, validates it, and gives clear line-numbered errors on bad input
- [ ] Graph class with your own traversal/shortest-path logic (no shortcuts via a library)
- [ ] Simulator correctly enforces zone types/costs, zone capacity, connection capacity, and the restricted-zone "must arrive next turn" rule
- [ ] Multiple drones move simultaneously without collisions, capacity violations, or deadlocks
- [ ] Output format matches the spec exactly, turn by turn
- [ ] Visual representation: colored terminal output at minimum
- [ ] `flake8` clean and `mypy` clean (ideally `--strict`)
- [ ] Type hints throughout, docstrings on public classes/functions (PEP 257)
- [ ] Exceptions handled gracefully — no crash on bad input
- [ ] `Makefile` with `install`, `run`, `debug`, `clean`, `lint`, (`lint-strict` recommended)
- [ ] `.gitignore` present
- [ ] `README.md` with every required section, written in English
- [ ] You can explain and modify any part of this live

## 6. If you have time left: the bonus path

Only worth attempting once every box above is checked:
- Meet or beat the spec's performance target on *every* provided map (not just "under the limit").
- Attempt the optional Challenger map and try to beat the reference turn count — this is explicitly framed as a research-grade stretch goal, not something expected of every learner.

## 7. Using AI on this without sabotaging your peer review

The project's own instructions are worth taking seriously here: using AI (like this conversation) to understand concepts, get unstuck on a specific error, or review your approach is encouraged. Copy-pasting a whole function or algorithm you can't explain is exactly what tends to fail people at peer review, since you'll be asked to justify or modify your code live. A good pattern: ask for an explanation or a small illustrative example on a *toy* problem, implement the real thing yourself, then explain your reasoning to a peer (or back to me) to catch gaps before submission.

## 8. Final tips

- Don't skip the "toy graph" practice on Day 2 to save time — it pays for itself the moment you're debugging the real thing on Day 6.
- Build your own extra map files early (Day 3 onward) — the spec tells you to, and they're what will actually reveal bugs the provided maps don't.
- If any single day runs long, the plan has natural merge points: Days 6–7 and 8 are the most likely to spill into each other, and Day 14 exists specifically to absorb that.
- If you get stuck on a concept mid-project, come back and ask — walking through *why* an approach works (not just handing you the code) is the fastest way to actually be ready for peer review.
