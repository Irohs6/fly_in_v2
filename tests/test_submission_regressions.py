import os
from pathlib import Path
import subprocess
import sys

import pytest

from src.model.graph import Graph
from src.model.pathfinder import Dijkstra
from src.model.simulation import Simulation
from src.parser.parser import Parser


ROOT = Path(__file__).resolve().parents[1]


def make_graph(tmp_path: Path, lines: list[str]) -> Graph:
    path = tmp_path / "map.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    return Graph(Parser(str(path)).parse())


@pytest.mark.parametrize(
    "normal_count, priority_count, expected_prefix",
    [(11, 12, "n"), (11, 11, "p"), (12, 11, "p")],
)
def test_priority_never_overrides_shorter_duration(
    tmp_path: Path,
    normal_count: int,
    priority_count: int,
    expected_prefix: str,
) -> None:
    lines = [
        "nb_drones: 1", "start_hub: start 0 0", "end_hub: goal 20 0",
    ]
    for prefix, count, zone in [
        ("n", normal_count, "normal"), ("p", priority_count, "priority"),
    ]:
        lines.extend(
            f"hub: {prefix}{i} {i} 1 [zone={zone}]" for i in range(count)
        )
    for prefix, count in [("n", normal_count), ("p", priority_count)]:
        route = ["start"] + [f"{prefix}{i}" for i in range(count)] + ["goal"]
        lines.extend(
            f"connection: {a}-{b}" for a, b in zip(route, route[1:])
        )
    graph = make_graph(tmp_path, lines)
    finder = Dijkstra(graph)
    path = finder.shortest_path()
    assert path[1].name == expected_prefix + "0"
    assert finder.distance_to(graph.start_zone, graph.end_zone) == (
        min(normal_count, priority_count) + 1
    )


def test_priority_tie_after_restricted_route(tmp_path: Path) -> None:
    graph = make_graph(tmp_path, [
        "nb_drones: 1", "start_hub: start 0 0", "end_hub: goal 4 0",
        "hub: r 1 0 [zone=restricted]",
        "hub: a 1 1", "hub: p 2 1 [zone=priority]",
        "hub: merge 3 0",
        "connection: start-r", "connection: r-merge",
        "connection: start-a", "connection: a-p",
        "connection: p-merge", "connection: merge-goal",
    ])
    finder = Dijkstra(graph)
    assert [hub.name for hub in finder.shortest_path()] == [
        "start", "a", "p", "merge", "goal",
    ]
    # Les exclusions utilisées pour le reroutage restent respectées.
    assert [hub.name for hub in finder.shortest_path(
        saturated_conns={(graph.hubs["p"], graph.hubs["a"])},
    )] == ["start", "r", "merge", "goal"]


@pytest.mark.parametrize("zone_type", ["normal", "restricted"])
def test_delivered_status_in_arrival_frame(
    tmp_path: Path, zone_type: str,
) -> None:
    graph = make_graph(tmp_path, [
        "nb_drones: 2", "start_hub: start 0 0",
        f"end_hub: goal 1 0 [zone={zone_type}]",
        "connection: start-goal",
    ])
    simulation = Simulation(graph)
    simulation.load_drones(2)
    turns = simulation.simulate()
    for frame in simulation.recorder.frames:
        for drone_id, state in frame.drones.items():
            if state.source == state.target == "goal":
                assert state.status == "delivered"
    assert all(drone.status == "delivered" for drone in simulation.drones)
    assert all(
        state.status == "delivered"
        for state in simulation.recorder.frames[-1].drones.values()
    )
    assert turns[-1][2] is graph.end_zone


def test_main_prints_only_movements() -> None:
    environment = os.environ.copy()
    environment.pop("PYGAME_HIDE_SUPPORT_PROMPT", None)
    result = subprocess.run(
        [sys.executable, "-c", (
            "import main; "
            "from src.view.pygame_view import PygameView; "
            "PygameView.display = lambda self: None; "
            "raise SystemExit(main.main())"
        ), "assets/maps/easy/01_linear_path.txt"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )
    assert result.stdout == (
        "D1-waypoint1\n"
        "D1-waypoint2 D2-waypoint1\n"
        "D1-goal D2-waypoint2\n"
        "D2-goal\n"
    )
    assert result.stderr == ""
