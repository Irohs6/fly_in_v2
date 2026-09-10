*This project has been created as part of the 42 curriculum by gacattan.*

# fly_ing — Drone Routing Simulation

> Route a fleet of autonomous drones through a network of zones from a start hub to an end hub in the fewest simulation turns possible.

---

## Description

**fly_ing** is a drone routing simulator built in Python with a Pygame graphical interface. Given a map file describing a graph of zones and their connections, the program routes drones turn by turn, prints their movements in the terminal, and opens a Pygame replay of the recorded states. The routing heuristic aims to reduce the total number of turns; it does not guarantee a globally optimal solution.

The core challenge is a constrained multi-agent pathfinding problem: drones must reach the destination in the minimum number of turns while respecting zone capacity limits, connection throughput, and zone-type movement costs (including 2-turn restricted zones).

---

## Architecture

The project follows a clean **MVC pattern**:

```
main.py
  └── Controller          (src/controller/controller.py)
        ├── Parser         (src/parser/parser.py)          — reads and validates the map file
        ├── Graph          (src/model/graph.py)            — adjacency list, bidirectional edges
        ├── Hub            (src/model/hub.py)              — zone with type, capacity, coordinates
        ├── Connection     (src/model/connection.py)       — edge with throughput limit
        ├── Drone          (src/model/drone.py)            — agent with path, status, transit state
        ├── Simulation     (src/model/simulation.py)       — turn-by-turn engine
        ├── Dijkstra       (src/model/pathfinder.py)       — weighted shortest path (heapq)
        ├── Recorder       (src/model/recorder.py)         — snapshots for replay
        ├── ReplayFrame    (src/model/replay.py)           — recorded drone and hub states
        ├── TerminalView   (src/view/terminal.py)          — required movement output
        └── PygameView     (src/view/pygame_view.py)       — graphical replay interface
              ├── GraphRenderer — draws hubs and connections
              ├── ReplayPlayer  — displays recorded turns and transit positions
              └── Camera        — zoom, pan, world↔screen projection
```

---

## Algorithm

The routing engine uses **Dijkstra's algorithm** with dynamic replanning:

1. At simulation start, all drones receive the same shortest path (by weighted cost).
2. Each turn processes drones sequentially, ordered by the number of turns remaining on their current paths. `_try_drone_move()` attempts one move per drone.
3. If a hub or connection is saturated, the drone retries Dijkstra from its current position, excluding unavailable resources. If no alternative is found, it waits.
4. Entering a `restricted` hub takes two turns: the drone occupies the connection on the first turn and arrives on the next. The destination is reserved before transit begins, so the drone cannot be left waiting on the connection.
5. A departing drone frees hub capacity immediately, allowing a later drone in the same turn to use it.
6. `Simulation` logs the reached `Hub` or occupied `Connection`; `TerminalView` formats the output. `Recorder` captures the initial state and each completed turn when replay recording is enabled. Terminal-only mode skips these snapshots.

Runtime depends on the number of turns, drones, and rerouting attempts. A drone can trigger multiple Dijkstra searches in one turn; each search also checks the excluded connections.

**Zone movement costs:**

| Zone type | Duration (turns) | Notes |
|---|---|---|
| `normal` | 1 | Default |
| `priority` | 1 | Dijkstra uses cost `1`; equal-duration paths favor more priority hubs |
| `restricted` | 2 | Drone must complete transit next turn |
| `blocked` | ∞ | Impassable |

---

## Performance Results

Measured with the current implementation on all 11 provided maps, without Pygame. These are observed turn counts, not proofs of optimality:

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

---

## Instructions

### Requirements

- Python ≥ 3.10
- [Poetry](https://python-poetry.org/) (dependency manager)

### Install

```bash
make install
```

### Run

```bash
# Run with a map file
make run MAP=assets/maps/easy/01_linear_path.txt

# Or directly
poetry run python main.py assets/maps/easy/01_linear_path.txt

# Terminal only: no Pygame import and no replay frames
poetry run python main.py assets/maps/easy/01_linear_path.txt --no-gui
make run MAP=assets/maps/easy/01_linear_path.txt ARGS=--no-gui

# Export movements to a text file
poetry run python main.py assets/maps/easy/01_linear_path.txt --no-gui > movements.txt

# Debug mode (pdb)
make debug MAP=assets/maps/easy/01_linear_path.txt
```

Creating a `Controller` only prepares its configuration. Call `controller.run()` for simulation and graphical replay, or `controller.run(gui=False)` for terminal output only. Each call starts a fresh simulation. Pygame is imported only for graphical execution.

For direct model usage, `Simulation(graph, record_replay=False)` disables replay snapshots; `simulation.recorder.frames` stays empty. The movement log is still retained. Recording remains enabled by default.

### Lint & type checking

```bash
make lint          # flake8 + mypy (standard flags)
make lint-strict   # flake8 + mypy --strict
```

### Tests

```bash
make test

# Run all provided maps without Pygame and write per-map terminal reports
make test-maps
```

`make test` covers model entities, parsing and validation, rerouting, same-turn capacity reuse, challenger maps, terminal formatting, and restricted transit replay states.

`make test-maps` and `make test-maps-export` both write reports to `tests/results_by_map`. To choose another directory:

```bash
poetry run python tests/test_all_maps_terminal.py --output-dir /tmp/fly-in-reports
```

### Clean

```bash
make clean    # removes __pycache__, .mypy_cache
make fclean   # also removes the virtual environment
```

---

## Map file format

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]
hub: roof1     3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green capacity=2]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: corridorA-roof1 [capacity=2]
connection: roof1-goal
# Comments start with #
```

Map requirements from [the subject (version 1.6)](docs/subject_fr_v3.md):

- First line must be `nb_drones: <positive integer>`
- Exactly one `start_hub` and one `end_hub`
- Zone names must not contain dashes or spaces
- Connections use `source-target` and must follow the definitions of both hubs
- `capacity` on start/end hubs is ignored (unlimited)
- `blocked` zones are impassable

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

- Hub circles sized by capacity and colored per map definition, with recorded occupancy labels
- Connection lines between hubs
- Drone positions for the selected turn, including intermediate restricted transit positions
- Current turn and total turns in the overlay

---

## Project structure

```
fly_in_v2/
├── main.py
├── Makefile
├── pyproject.toml
├── src/
│   ├── controller/
│   ├── model/          # Graph, Hub, Connection, Drone, Simulation, Dijkstra, Recorder, replay states
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

- Dijkstra's algorithm — <https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm>
- Multi-agent pathfinding (MAPF) — <https://en.wikipedia.org/wiki/Multi-agent_pathfinding>
- Yen's K-shortest paths — <https://en.wikipedia.org/wiki/Yen%27s_k-shortest_path_algorithm>
- Python `heapq` module — <https://docs.python.org/3/library/heapq.html>
- Pygame documentation — <https://www.pygame.org/docs/>
- PEP 257 — Docstring conventions — <https://peps.python.org/pep-0257/>

### AI usage

AI (GitHub Copilot / Claude) was used to assist with:
- Initial scaffolding of the MVC file structure
- Drafting docstrings and inline comments
- Reviewing algorithmic logic and edge cases in the parser
- Generating the initial `drone_animator.py` interpolation code

All AI-generated content was reviewed, tested, and adapted by the author. No code was copied without full understanding and validation.
