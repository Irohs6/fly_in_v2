*This project has been created as part of the 42 curriculum by gacattan.*

# fly_ing — Drone Routing Simulation

> Route a fleet of autonomous drones through a network of zones from a start hub to an end hub in the fewest simulation turns possible.

---

## Description

**fly_ing** is a drone routing simulator built in Python with a Pygame graphical interface. Given a map file describing a graph of zones and their connections, the program computes optimal paths for all drones simultaneously and animates their movements turn by turn.

The core challenge is a constrained multi-agent pathfinding problem: drones must reach the destination in the minimum number of turns while respecting zone capacity limits, connection throughput, and zone-type movement costs (including 2-turn restricted zones).

---

## Architecture

The project follows a clean **MVC pattern**:

```
main.py
  └── Controller          (src/controller/controller.py)
        ├── Parser         (src/parser/parser.py)          — reads and validates the map file
        ├── Graph          (src/model/graph.py)            — adjacency list, bidirectional edges
        ├── Zone           (src/model/zone.py)             — hub with type, capacity, coordinates
        ├── Connection     (src/model/connection.py)       — edge with throughput limit
        ├── Drone          (src/model/drone.py)            — agent with path, status, transit state
        ├── Simulation     (src/model/simulation.py)       — turn-by-turn engine
        ├── Dijkstra       (src/model/pathfinder.py)       — weighted shortest path (heapq)
        └── Pygame_view    (src/view/pygame_view.py)       — graphical replay interface
              ├── GraphRenderer     — draws zones and connections
              ├── DroneAnimationLayer — interpolated drone movement
              └── Camera            — zoom, pan, world↔screen projection
```

---

## Algorithm

The routing engine uses **Dijkstra's algorithm** with dynamic replanning:

1. At simulation start, all drones receive the same shortest path (by weighted cost).
2. At each turn, `_try_move()` attempts to advance each drone one step along its path.
3. If the next zone is at capacity, the drone tries an **alternative path** excluding the blocked zone, recalculating with Dijkstra from its current position.
4. Drones in **restricted zone transit** occupy the link for 2 turns and must complete transit — they cannot be interrupted.
5. Drones leaving a zone free its capacity on the same turn, allowing others to enter.

**Complexity:** O(T × N × (V + E) log V) where T = total turns, N = number of drones, V = zones, E = connections.

**Zone movement costs:**

| Zone type | Cost (turns) | Notes |
|---|---|---|
| `normal` | 1 | Default |
| `priority` | 1 | Preferred in pathfinding |
| `restricted` | 2 | Drone must complete transit next turn |
| `blocked` | ∞ | Impassable |

---

## Performance Results

All provided maps are solved within or well below the target turn counts:

| Map | Drones | Result | Target |
|---|---|---|---|
| easy/01 — linear path | 2 | **6 turns** | ≤ 6 |
| easy/02 — simple fork | 4 | **6 turns** | ≤ 8 |
| easy/03 — basic capacity | 4 | **4 turns** | ≤ 6 |
| medium/01 — dead end trap | 5 | **8 turns** | ≤ 12 |
| medium/02 — circular loop | 6 | **15 turns** | ≤ 15 |
| medium/03 — priority puzzle | 5 | **8 turns** | ≤ 12 |
| hard/01 — maze nightmare | 8 | **13 turns** | ≤ 30 |
| hard/02 — capacity hell | 12 | **16 turns** | ≤ 35 |
| hard/03 — ultimate challenge | 15 | **27 turns** | ≤ 45 |

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
python main.py assets/maps/easy/01_linear_path.txt

# Debug mode (pdb)
make debug MAP=assets/maps/easy/01_linear_path.txt
```

### Lint & type checking

```bash
make lint          # flake8 + mypy (standard flags)
make lint-strict   # mypy --strict
```

### Tests

```bash
make test
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

Rules:
- First line must be `nb_drones: <positive integer>`
- Exactly one `start_hub` and one `end_hub`
- Zone names must not contain dashes or spaces
- `capacity` on start/end hubs is ignored (unlimited)
- `blocked` zones are impassable

---

## Example

### Input (`assets/maps/easy/01_linear_path.txt`)

```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [zone=restricted color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

### Expected output (terminal)

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D2-waypoint2
D1-goal D2-goal
```

Each line is one simulation turn. Format: `D<ID>-<zone>` for normal moves, `D<ID>-<zone1>-<zone2>` for restricted transit. Drones that do not move are omitted.

---

## Graphical interface (Pygame)

After the simulation computes the solution, a Pygame window opens and replays the drone movements with smooth animation.

| Control | Action |
|---|---|
| `SPACE` | Play / Pause replay |
| `←` / `→` | Previous / Next turn |
| `R` | Restart replay |
| Mouse wheel | Zoom in / out (centered on cursor) |
| Middle or right click + drag | Pan the view |
| `ESC` | Quit |

The display shows:
- Zone circles sized by `capacity` capacity, colored per map definition
- Connection lines with live drone count / capacity labels
- Drone positions interpolated between turns
- Current turn and total turns in the overlay

---

## Project structure

```
fly_ing/
├── main.py
├── Makefile
├── pyproject.toml
├── src/
│   ├── controller/
│   ├── model/          # Graph, Zone, Connection, Drone, Simulation, Dijkstra
│   ├── parser/
│   └── view/           # Pygame view, graph renderer, drone animator, camera
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
