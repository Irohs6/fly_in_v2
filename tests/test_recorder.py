from collections import Counter
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock

import pygame
import pytest

from src.model.graph import Graph
from src.model.simulation import Simulation
from src.model.state import DroneState
from src.parser.parser import Parser
from src.view.graph_renderer import GraphRenderer
from src.view.replay_player import ReplayPlayer
from src.view.terminal import TerminalView
from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


def make_simulation(
    tmp_path: Path, restricted: bool = True, reverse: bool = False,
) -> Simulation:
    """Build a capacity-two route with an unused blocked branch."""
    edge = "a-start" if reverse else "start-a"
    zone = "restricted" if restricted else "normal"
    path = tmp_path / "recording.txt"
    path.write_text(
        "nb_drones: 3\nstart_hub: start 0 0 [color=green]\n"
        f"hub: a 1 0 [zone={zone} color=teal max_drones=2]\n"
        "hub: unused 1 1 [zone=blocked color=beige max_drones=5]\n"
        "end_hub: goal 2 0 [color=red]\n"
        f"connection: {edge} [max_link_capacity=2]\n"
        "connection: a-goal [max_link_capacity=2]\n"
        "connection: a-unused\n",
        encoding="utf-8",
    )
    simulation = Simulation(Graph(Parser(str(path)).parse()))
    simulation.load_drones(3)
    return simulation


@pytest.mark.parametrize("restricted", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
def test_complete_turn_keeps_capacity_usage_before_reset(
    tmp_path: Path, restricted: bool, reverse: bool,
) -> None:
    simulation = make_simulation(tmp_path, restricted, reverse)
    initial = deepcopy(simulation.recorder.frames[0])
    frames = simulation.simulate()
    edge = ("a", "start") if reverse else ("start", "a")

    assert frames[0] == initial
    assert initial.moved_drones == ()
    assert initial.hubs["start"].nb_drones == 3
    assert initial.hubs["start"].capacity == float("inf")
    assert initial.drones[1].path == ("a", "goal")
    assert initial.connections[edge].used_capacity == 0
    assert (initial.start_hub, initial.end_hub) == ("start", "goal")

    first = frames[1]
    assert first.moved_drones == (1, 2)
    assert first.hubs["start"].nb_drones == 1
    assert first.connections[edge].capacity == 2
    assert first.connections[edge].used_capacity == 2
    assert first.connections[edge].in_transit == (2 if restricted else 0)
    assert first.hubs["a"].nb_drones == (0 if restricted else 2)
    assert first.hubs["a"].reserved == (2 if restricted else 0)
    assert first.drones[3].status == "waiting"
    assert first.drones[3].current_position == "start"
    assert first.drones[1].previous_zone == "start"
    assert first.drones[1].current_position == (edge if restricted else "a")

    unused = first.hubs["unused"]
    assert (unused.name, unused.x, unused.y) == ("unused", 1, 1)
    assert (unused.zone_type, unused.color) == ("blocked", "beige")
    assert (unused.nb_drones, unused.reserved, unused.capacity) == (0, 0, 5)
    assert first.connections[("a", "unused")].used_capacity == 0

    if restricted:
        arrival = frames[2]
        assert arrival.connections[edge].used_capacity == 2
        assert arrival.connections[edge].in_transit == 0
        assert arrival.hubs["a"].nb_drones == 2
        assert arrival.hubs["a"].reserved == 0
        assert arrival.drones[1].path == ("goal",)
        assert first.drones[1].path == ("a", "goal")
        assert first.drones[1].transit_turns == 1
        assert first.drones[1].transit_duration == 2
        assert arrival.drones[1].transit_turns == 0
        assert arrival.drones[1].transit_duration == 0

    assert frames[-1].hubs["goal"].nb_drones == 3
    assert frames[-1].connections[("a", "goal")].used_capacity == 1
    assert all(state.status == "delivered"
               for state in frames[-1].drones.values())
    assert all(state.path == () for state in frames[-1].drones.values())


def test_history_survives_live_model_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    simulation = make_simulation(tmp_path)
    frames = simulation.simulate()
    saved = deepcopy(frames)
    TerminalView().display(frames)
    expected_output = capsys.readouterr().out

    for hub in simulation.graph.hubs.values():
        hub.nb_drones = 99
        hub.reserved = 99
        hub.capacity = 99
        hub.name = "changed"
        hub.color = "changed"
        hub.zone_type = "changed"
        hub.x = 99
        hub.y = 99
    for connection in simulation.graph.connections:
        connection.used_capacity = 99
        connection.capacity = 99
    for drone in simulation.drones:
        drone.path.append(simulation.graph.start_hub)
        drone.current_position = simulation.graph.start_hub
        drone.previous_zone = None
        drone.status = "changed"
        drone.transit_turns = 99
        drone.transit_duration = 99
    simulation.graph.hubs.clear()
    simulation.graph.connections.clear()

    assert frames == saved
    TerminalView().display(frames)
    assert capsys.readouterr().out == expected_output


@pytest.mark.parametrize("edge", [("a", "b"), ("b", "a")])
def test_replay_uses_transit_direction_and_raw_counters(
    edge: tuple[str, str],
) -> None:
    state = DroneState(edge, "a", ("b",), "in_transit", 4, 1)
    positions = {"a": (0.0, 0.0), "b": (100.0, 20.0)}
    assert ReplayPlayer([])._state_position(state, positions) == (25.0, 5.0)


def test_visual_labels_follow_selected_turn(tmp_path: Path) -> None:
    simulation = make_simulation(tmp_path)
    frames = simulation.simulate()
    pygame.font.init()
    try:
        font = Mock(wraps=pygame.font.Font(None, 20))
        renderer = GraphRenderer(pygame.Surface((1000, 600)), font)
        coord = CoordinateSystem(160)
        for turn in (1, 2, 0, 1):
            font.reset_mock()
            frame = frames[turn]
            positions = coord.compute(frame.hubs.values())
            renderer.draw(Camera(), frame, positions)
            labels = [call.args[0] for call in font.render.call_args_list]
            if turn == 1:
                assert "0/2 +2 reserved" in labels
                assert "2/2 (2 in transit)" in labels
            elif turn == 2:
                assert "2/2" in labels
                assert not any("reserved" in label or "in transit" in label
                               for label in labels)
            else:
                assert "3/∞" in labels
                assert "0/2" in labels
    finally:
        pygame.font.quit()


@pytest.mark.parametrize(
    "map_path", sorted(Path("assets/maps").rglob("*.txt")),
)
def test_recorded_occupancy_matches_drone_positions(map_path: Path) -> None:
    """Check capacities using drone positions and consecutive turns."""
    data = Parser(str(map_path)).parse()
    simulation = Simulation(Graph(data))
    simulation.load_drones(data["nb_drones"])
    frames = simulation.simulate()
    for index, frame in enumerate(frames):
        present: Counter[str] = Counter()
        reserved: Counter[str] = Counter()
        transit: Counter[tuple[str, str]] = Counter()
        usage: Counter[tuple[str, str]] = Counter()
        for drone in frame.drones.values():
            position = drone.current_position
            if isinstance(position, str):
                present[position] += 1
            else:
                transit[position] += 1
                reserved[drone.path[0]] += 1
        if index:
            previous = frames[index - 1]
            for drone_id, before in previous.drones.items():
                departure = before.current_position
                arrival = frame.drones[drone_id].current_position
                if isinstance(departure, tuple):
                    usage[departure] += 1
                elif drone_id in frame.moved_drones:
                    if isinstance(arrival, tuple):
                        usage[arrival] += 1
                    else:
                        edge = (departure, arrival)
                        if edge not in frame.connections:
                            edge = (arrival, departure)
                        usage[edge] += 1
        for name, hub in frame.hubs.items():
            assert hub.nb_drones == present[name]
            assert hub.reserved == reserved[name]
            assert hub.nb_drones + hub.reserved <= hub.capacity
        for edge, connection in frame.connections.items():
            assert connection.in_transit == transit[edge]
            assert connection.used_capacity == usage[edge]
            assert connection.in_transit <= connection.used_capacity
            assert connection.used_capacity <= connection.capacity
