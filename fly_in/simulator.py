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
