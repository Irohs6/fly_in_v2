from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

from src.controller.controller import Controller
from src.model.graph import Graph
from src.model.state import DroneState, TurnState
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.view.replay_player import ReplayPlayer
from src.view.utils.camera import Camera


ROOT = Path(__file__).resolve().parents[1]
MAP = "assets/maps/easy/01_linear_path.txt"


def test_controller_construction_has_no_execution(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "missing.txt"
    with patch.object(Parser, "parse", side_effect=AssertionError):
        controller = Controller(map_path=str(map_path))
    assert controller.map_path == str(map_path)
    assert capsys.readouterr().out == ""


def test_terminal_mode_does_not_import_pygame() -> None:
    result = subprocess.run(
        [sys.executable, "-c", (
            "import sys; import main; "
            "result = main.main(); "
            "assert 'pygame' not in sys.modules; "
            "raise SystemExit(result)"
        ), MAP, "--view-desactivate"],
        cwd=ROOT, text=True, capture_output=True, timeout=10, check=True,
    )
    assert result.stdout == (
        "D1-waypoint1\nD1-waypoint2 D2-waypoint1\n"
        "D1-goal D2-waypoint2\nD2-goal\n"
    )
    assert result.stderr == ""


def test_controller_can_run_both_modes_again(
    capsys: pytest.CaptureFixture[str],
) -> None:
    controller = Controller(MAP)
    with patch("src.view.pygame_view.PygameView.display") as display:
        controller.run()
        display.assert_called_once()
        graphic_output = capsys.readouterr().out

        controller.run(view_active=False)
        assert capsys.readouterr().out == graphic_output
        display.assert_called_once()


@pytest.mark.parametrize("restricted", [False, True])
def test_complete_history_is_recorded_once_per_turn(
    tmp_path: Path, restricted: bool,
) -> None:
    content = (ROOT / MAP).read_text()
    if restricted:
        content = content.replace(
            "hub: waypoint2 2 0 [color=blue]",
            "hub: waypoint2 2 0 [zone=restricted color=blue]",
        )
    path = tmp_path / "map.txt"
    path.write_text(content)
    data = Parser(str(path)).parse()
    simulation = Simulation(Graph(data))
    simulation.load_drones(data["nb_drones"])
    frames = simulation.simulate()
    assert frames is simulation.recorder.frames
    assert [frame.turn for frame in frames] == list(range(simulation.turn + 1))
    assert all(frame.connections for frame in frames)
    assert all(d.status == "delivered" for d in simulation.drones)
    completed_count = len(frames)
    assert simulation.simulate() is frames
    assert len(frames) == completed_count


def test_replay_draws_lowest_id_per_hub_and_all_transits() -> None:
    frame = TurnState(
        turn=1, start_hub="a", end_hub="b", hubs={}, connections={},
        drones={
            5: DroneState("a", None, ("b",), "waiting"),
            2: DroneState("a", None, ("b",), "waiting"),
            4: DroneState(("a", "b"), "a", ("b",), "in_transit"),
            3: DroneState("b", "a", (), "moving"),
            6: DroneState(("a", "b"), "a", ("b",), "in_transit"),
        },
    )
    replay = ReplayPlayer([frame])
    screen = Mock()
    screen.get_size.return_value = (800, 600)
    with patch.object(replay, "_draw_drone") as draw:
        replay.draw(screen, Camera(), Mock(),
                    {"a": (0.0, 0.0), "b": (10.0, 0.0)})
    assert [call.args[2] for call in draw.call_args_list] == [2, 4, 3, 6]
