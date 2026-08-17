"""Map file parser: text file -> (Graph, nb_drones).

TODO (Day 3):
- Read the file line by line.
- Dispatch on prefix: nb_drones:, start_hub:, end_hub:, hub:, connection:, # comment.
- Parse the [key=value ...] metadata blocks.
- Validate everything the subject requires (unique start/end, no duplicate
  connections, valid zone types, positive capacities, no dashes/spaces in
  names, etc.) and raise a clear, line-numbered MapParseError on violation.

Define your own exception, e.g.:

class MapParseError(Exception):
    ...
"""
