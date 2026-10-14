*This project has been created as part of the 42 curriculum by gacattan.*

# Fly-in — Drone Routing Simulation

> Route a fleet of autonomous drones through a network of zones from a start hub to an end hub in the fewest simulation turns possible.

---

## Description

**Fly-in** is a drone routing simulator built in Python with an optional Pygame graphical interface. Given a map file describing a graph of zones and their connections, the program routes drones turn by turn, prints their movements in the terminal, and opens a Pygame replay of the recorded states. Use `--view-desactivate` to run with terminal output only. The routing heuristic aims to reduce the total number of turns; it does not guarantee a globally optimal solution.

The core challenge is a constrained multi-agent pathfinding problem: drones must reach the destination in the minimum number of turns while respecting zone capacity limits, connection throughput, and zone-type movement costs (including 2-turn restricted zones).

---

## Architecture

The project separates its model, views and controller:

```
main.py
  └── Controller          (src/controller/controller.py)
        ├── Parser         (src/parser/parser.py)          — reads and validates the map file
        │     └── MapValidator (src/parser/validator.py)   — constraints and reachability
        ├── Graph          (src/model/graph.py)            — adjacency list, bidirectional edges
        ├── Hub            (src/model/hub.py)              — zone with type, capacity, coordinates
        ├── Connection     (src/model/connection.py)       — edge with throughput limit
        ├── Drone          (src/model/drone.py)            — agent with path, status, transit state
        ├── Simulation     (src/model/simulation.py)       — turn-by-turn engine
        ├── Dijkstra       (src/model/pathfinder.py)       — weighted shortest path (heapq)
        ├── Recorder       (src/model/recorder.py)         — complete history for both views
        ├── TurnState      (src/model/state.py)            — drone, hub and connection states
        ├── TerminalView   (src/view/terminal.py)          — required movement output
        └── PygameView     (src/view/pygame_view.py)       — graphical replay interface
              ├── GraphRenderer — draws hubs and connections
              ├── ReplayPlayer  — displays recorded turns and transit positions
              └── Camera        — zoom, pan, world↔screen projection
```

---

## Algorithm explanation

The parser validates the input before building the graph. A **breadth-first search (BFS)** checks that the end hub is reachable from the start without entering blocked hubs. This check only establishes reachability; movement costs are handled by the pathfinder.

`Graph` stores bidirectional connections in adjacency lists and indexes endpoint pairs for direct connection lookup. The implementation uses Python containers and `heapq`, without a graph library.

The routing engine uses **Dijkstra's algorithm** with dynamic replanning:

1. At simulation start, all drones receive the same shortest path (by weighted cost).
2. Each turn processes drones sequentially, ordered by the summed durations of the hubs remaining on their paths. This estimate includes the full destination duration for a drone already in transit. Each drone advances at most once per turn.
3. If a hub or connection is saturated, the drone retries Dijkstra from its current position, excluding the unavailable resources encountered during that turn. Rerouting also excludes the previous hub to avoid immediately going back. If no alternative is found, the drone waits and keeps its last path for the next turn.
4. Entering a `restricted` hub takes two turns: the drone occupies the connection on the first turn and arrives on the next. The destination is reserved before transit begins, so the drone cannot be left waiting on the connection.
5. A departing drone frees hub capacity immediately, allowing a later drone in the same turn to use it.
6. `Recorder` captures the initial state and each completed turn before connection counters are reset for the next turn. `TerminalView` and `PygameView` read this same history. The terminal uses each state's ordered list of moved drone IDs to print the required movements.

Connection capacity is shared by both directions. A one-turn crossing consumes capacity for the current turn; a restricted transit occupies the connection through its arrival turn. At the start of the next turn, connection counters are reset and ongoing transits are retained.

### Complete turn history

`Simulation.simulate()` returns `recorder.frames`, including turn zero. Each `TurnState` contains independent copies of the model's values:

| Recorded entity | Data |
|---|---|
| Drone | Hub or connection position, previous hub, remaining path, status, transit duration and elapsed transit turns |
| Hub | Name, coordinates, color, zone type, capacity, present drones and reserved arrival slots |
| Connection | Declared endpoints, capacity used during the turn and number of drones still in transit, plus maximum capacity |
| Turn | Turn number, start/end hub names and moved drone IDs in processing order |

`used_capacity` and `in_transit` describe different facts: a connection may have served two drones during a turn while containing none at its end. Recording before the next reset preserves both values. Snapshots contain no references to live hubs, connections or drone paths, so completing the simulation cannot rewrite earlier states.

The views only interpret these records. The graphical view derives interpolation from the saved transit counters; the recorder contains no animation-specific progress calculation. Returning to an earlier turn restores its hub reservations and connection usage as well as drone positions.

**Zone movement costs:**

| Zone type | Duration (turns) | Notes |
|---|---|---|
| `normal` | 1 | Default |
| `priority` | 1 | Dijkstra uses cost `1`; equal-duration paths favor more priority hubs |
| `restricted` | 2 | Drone must complete transit next turn |
| `blocked` | ∞ | Impassable |

### Complexity and trade-offs

With `V` hubs and `E` connections, the reachability check takes `O(V + E)` time. One Dijkstra search takes `O((V + E) log V)` on this simple graph, using a heap. Excluded hubs and connections are checked with set membership.

The simulation can run several searches for one drone in one turn. Its total runtime also depends on the number of drones, the number of turns, path lengths and congestion. Each turn recomputes path-duration estimates, sorts the drones and updates occupancy. A single Dijkstra complexity bound therefore does not describe the whole simulation.

Dynamic rerouting allows drones to use alternative paths without precomputing every route. Processing drones sequentially keeps capacity checks straightforward, but makes results depend on processing order: a waiting drone is not reconsidered if another drone frees its destination later in the same turn. Static reachability does not prove that every possible fleet configuration will finish, and there is no general deadlock detector.

For `T` turns, `N` drones and maximum remaining path length `L`, the complete history uses up to `O((T + 1) × (V + E + N × (L + 1)))` storage. This includes copies of the remaining paths. Both execution modes record the same states: `--view-desactivate` avoids the graphical window and Pygame import, but does not reduce history storage. There is no separate movement log.

---

## Performance Results

Rechecked on 13 October 2026 on all 11 maps in the repository, using their original drone counts and without Pygame. These are observed turn counts, not proofs of optimality:

| Map | Drones | Result |
|---|---|---|
| easy/01 — linear path | 2 | **4 turns** |
| easy/02 — simple fork | 4 | **4 turns** |
| easy/03 — basic capacity | 4 | **4 turns** |
| medium/01 — dead end trap | 5 | **8 turns** |
| medium/02 — circular loop | 6 | **15 turns** |
| medium/03 — priority puzzle | 5 | **7 turns** |
| hard/01 — maze nightmare | 8 | **13 turns** |
| hard/02 — capacity hell | 12 | **16 turns** |
| hard/03 — ultimate challenge | 15 | **26 turns** |
| challenger/01 — the impossible dream | 25 | **43 turns** |
| challenger/42 — spaghetti | 42 | **46 turns** |

Average turn counts are **4** for Easy, **10** for Medium and **18.33** for Hard. All nine Easy/Medium/Hard results meet their individual reference targets. Impossible Dream finishes below the 45-turn reference record.

---

## Instructions

### Requirements

- Python ≥ 3.10
- [Poetry](https://python-poetry.org/) (dependency manager)
- `make` for the Makefile commands
- A working graphical display for Pygame replay; `--view-desactivate` also works without a display

### Install

Run commands from the repository root. Poetry installs Pygame and the development tools declared in `pyproject.toml`.

```bash
make install
```

### Run

```bash
# Run with a map file
make run MAP=assets/maps/easy/01_linear_path.txt

# Or directly
poetry run python main.py assets/maps/easy/01_linear_path.txt

# Select another map
poetry run python main.py assets/maps/medium/02_circular_loop.txt
poetry run python main.py assets/maps/hard/03_ultimate_challenge.txt
poetry run python main.py assets/maps/challenger/01_the_impossible_dream.txt

# Terminal only: no Pygame import or window; history is still recorded
poetry run python main.py assets/maps/easy/01_linear_path.txt --view-desactivate
make run MAP=assets/maps/easy/01_linear_path.txt ARGS=--view-desactivate

# Export movements to a text file
poetry run python main.py assets/maps/easy/01_linear_path.txt --view-desactivate > movements.txt

# Debug mode (pdb)
make debug MAP=assets/maps/easy/01_linear_path.txt
```

If no map argument is supplied, the program uses `assets/maps/easy/02_simple_fork.txt`. Add `--view-desactivate` to any direct command above to keep terminal output only.

Creating a `Controller` only prepares its configuration. Each call to `run()` starts a fresh simulation. Pygame is imported only for graphical execution.

```python
from src.controller.controller import Controller

controller = Controller("assets/maps/easy/01_linear_path.txt")
controller.run(view_active=False)  # Terminal only; run() also opens the replay.
```

For direct model usage, create `Simulation(graph)`, call `load_drones(count)`, then `frames = simulation.simulate()`. The returned list is also available as `simulation.recorder.frames`. Recording is always complete; the previous `record_replay` option and separate `movements_log` have been removed. `PygameView(frames)` can replay the result without access to the live graph.

Map reading or validation failures and expected Pygame errors are reported on standard error with an `Error:` prefix and exit code `1`. Keyboard interruption returns `130`. Pygame resources are released when the replay closes or an exception occurs.

### Lint & type checking

```bash
make lint          # flake8 + mypy (standard flags)
make lint-strict   # optional: flake8 + mypy --strict
```

### Tests

```bash
make test

# Run all provided maps without Pygame and write per-map terminal reports
make test-maps
```

The development test suite covers model entities, parsing and validation, rerouting, same-turn capacity reuse, challenger maps, terminal formatting, complete recorded states, reservations, connection usage, large coordinates, execution modes and graphical error cleanup. Recorder tests reconstruct occupancy from drone positions on all eleven maps and verify that changes to the live model do not alter history.

`make test-maps` and `make test-maps-export` both write reports to `tests/results_by_map`. To choose another directory:

```bash
poetry run python tests/test_all_maps_terminal.py --output-dir /tmp/fly-in-reports
```

### Clean

```bash
make clean    # removes Python bytecode, caches and generated map reports
make fclean   # also removes the virtual environment
```

`make clean` removes `tests/results_by_map/` and `tests/results_maps_terminal.txt`. It preserves Git data and virtual environments (`.venv`, `.venv-*`, `venv`).

---

## Map file format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]
hub: roof1     3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: corridorA-roof1 [max_link_capacity=2]
connection: roof1-goal
# Comments start with #
```

### Metadata and validation

| Declaration | Metadata | Default |
|---|---|---|
| Hub | `zone=<type>`: `normal`, `priority`, `restricted` or `blocked` | `normal` |
| Hub | `color=<name>` | `gray` |
| Hub | `max_drones=<positive integer>` | `1`; ignored for start/end hubs |
| Connection | `max_link_capacity=<positive integer>` | `1` |

Map requirements from [the subject (version 1.6)](docs/subject.md):

- The first meaningful line must be `nb_drones: <positive integer>`; blank lines and comment-only lines starting with `#` are skipped
- Exactly one `start_hub` and one `end_hub`
- Zone names must be unique and must not contain dashes or spaces
- Coordinates must be integers; negative coordinates are accepted
- Connections use `source-target` and must follow the definitions of both hubs
- Duplicate connections are rejected, including reversed pairs such as `a-b` and `b-a`
- `max_drones` on start/end hubs is ignored (unlimited)
- Other hub and connection capacities must be positive integers
- `blocked` zones are impassable
- The end hub must be reachable from the start without crossing a blocked hub

The parser also accepts legacy `capacity` metadata for hubs and connections, and `drones` or `nb_drone` as aliases for `nb_drones`. The examples above use the subject's official names. Combining `capacity` with the corresponding official capacity key in one declaration is rejected.

### Drone count

The parser accepts any positive integer for `nb_drones`, with no application-specific upper limit.

---

## Example

### Input (`assets/maps/easy/01_linear_path.txt`)

```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Expected output (terminal)

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

Each line is one simulation turn. Format: `D<ID>-<zone>` on arrival at a hub, or `D<ID>-<source>-<target>` while in restricted transit. The connection name preserves the endpoint order declared in the map, even when traversed in reverse. Waiting drones and drones delivered on previous turns are omitted.

If `waypoint2` in this example is changed to `[zone=restricted color=blue]`, the output becomes:

```text
D1-waypoint1
D1-waypoint1-waypoint2 D2-waypoint1
D1-waypoint2
D1-goal D2-waypoint1-waypoint2
D2-waypoint2
D2-goal
```

---

## Graphical interface (Pygame)

After the simulation prints its movements, a Pygame window opens at the initial recorded state. Use the arrow keys to inspect successive turns. A drone in restricted transit is drawn between the connection endpoints using its recorded progress.

| Control | Action |
|---|---|
| `←` / `→` | Previous / Next turn |
| `R` | Return to the initial replay state |
| `C` | Reset camera |
| Mouse wheel | Zoom in / out (centered on cursor) |
| Middle or right click + drag | Pan the view |
| `ESC` | Quit |

The display shows:

- Hub circles sized by capacity and colored using the renderer's palette, with present/capacity labels and reserved slots
- Connection lines labeled with used/capacity for the selected turn and any remaining transits
- Drone positions for the selected turn, including intermediate restricted transit positions
- Current turn and total turns in the overlay

Stepping backward and forward helps inspect congestion and the two stages of restricted transit. For example, `0/2 +2 reserved` means that a hub is empty but both places are reserved by incoming drones. A connection labeled `2/2 (2 in transit)` used both slots and still carries two drones; `2/2` alone means both slots were used but no drone remains on the connection. Zoom and pan help explore larger graphs. When several drones share a hub, the replay draws the lowest drone ID as a representative and uses the occupancy label for the count.

The palette includes the colors used in the provided maps, including Spaghetti's `lightbrown`, `lightblue`, `teal` and `beige`. Unknown names use a light-gray fallback.

---

## Project structure

```
fly_in_v2/
├── main.py
├── Makefile
├── pyproject.toml
├── src/
│   ├── controller/
│   ├── model/          # Graph, entities, Simulation, Dijkstra, Recorder, complete turn states
│   ├── parser/
│   └── view/           # TerminalView, PygameView, GraphRenderer, ReplayPlayer, camera
├── assets/
│   └── maps/
│       ├── easy/       (3 maps)
│       ├── medium/     (3 maps)
│       ├── hard/       (3 maps)
│       └── challenger/ (2 maps)
├── tests/
└── docs/
```

---

## Resources

### References

- [Fly-in subject, version 1.6](docs/subject.md) — project requirements and map format
- Dijkstra's algorithm — <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>
- Multi-agent pathfinding (MAPF) — <https://en.wikipedia.org/wiki/Multi-agent_pathfinding>
- Yen's K-shortest paths — <https://en.wikipedia.org/wiki/Yen%27s_k-shortest_path_algorithm> (background on alternative paths; not implemented here)
- Python `heapq` module — <https://docs.python.org/3/library/heapq.html>
- Pygame documentation — <https://www.pygame.org/docs/>
- PEP 257 — Docstring conventions — <https://peps.python.org/pep-0257/>

### AI usage

Earlier assistance from GitHub Copilot and Claude covered the initial MVC structure, documentation, parser review and an initial animation prototype. The former `drone_animator.py` file is no longer part of the project; replay rendering now lives in `src/view/replay_player.py`.

OpenAI Codex was also used for reviews, code changes and verification, including:

- Parser and validator checks, malformed-input handling and regression tests in `src/parser/` and `tests/`
- Refactoring drone state, simulation responsibilities and terminal-only execution in `src/model/` and `src/controller/`
- Complete turn recording shared by terminal output and graphical replay, including reservations and connection usage, in `src/model/` and `src/view/`
- Replay rendering, large-coordinate handling and graphical exception cleanup in `src/view/`
- English docstrings and error messages, Makefile maintenance and README updates
- Comparing the implementation with the supplied subject and evaluation criteria, documenting findings in `docs/` and measuring results on the provided maps

Changes have been checked through automated tests, linting, type checking and map runs. These checks do not establish correctness on every graph; the author remains responsible for reviewing and explaining the submitted implementation and its limitations.
