from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

from src.controller.controller import Controller
from src.model.graph import Graph
from src.model.replay import DroneReplayState, ReplayFrame
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.view.replay_player import ReplayPlayer
from src.view.terminal import TerminalView
from src.view.utils.camera import Camera


ROOT = Path(__file__).resolve().parents[1]
MAP = "assets/maps/easy/01_linear_path.txt"


def test_controller_construction_has_no_execution(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    with patch.object(Parser, "parse", side_effect=AssertionError):
        controller = Controller(tmp_path / "missing.txt")
    assert controller.data is None
    assert controller.graph is None
    assert controller.simulation is None
    assert controller.view is None
    assert capsys.readouterr().out == ""


def test_terminal_mode_does_not_import_pygame() -> None:
    result = subprocess.run(
        [sys.executable, "-c", (
            "import sys; import main; "
            "result = main.main(); "
            "assert 'pygame' not in sys.modules; "
            "raise SystemExit(result)"
        ), MAP, "--no-gui"],
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
    assert controller.simulation is not None
    assert len(controller.simulation.recorder.frames) == 5
    assert controller.view is not None

    controller.run(is_view=False)
    assert capsys.readouterr().out == graphic_output
    assert controller.simulation.recorder.frames == []
    assert controller.view is None


@pytest.mark.parametrize("restricted", [False, True])
def test_recording_is_optional_without_changing_movements(
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
    outputs = []
    for recording in (True, False):
        simulation = Simulation(Graph(data), record_replay=recording)
        buffer = StringIO()
        with patch.object(
            simulation.recorder, "record", wraps=simulation.recorder.record,
        ) as record:
            simulation.load_drones(data["nb_drones"])
            with redirect_stdout(buffer):
                TerminalView().display(simulation.simulate())
        if not recording:
            record.assert_not_called()
        outputs.append(buffer.getvalue())
        assert bool(simulation.recorder.frames) is recording
        assert all(d.status == "delivered" for d in simulation.drones)
    assert outputs[0] == outputs[1]


def test_replay_draws_lowest_id_per_hub_and_all_transits() -> None:
    frame = ReplayFrame(turn=1, hubs={}, drones={
        5: DroneReplayState("a", "a", 1.0, "waiting"),
        2: DroneReplayState("a", "a", 1.0, "waiting"),
        4: DroneReplayState("a", "b", 0.5, "in_transit"),
        3: DroneReplayState("b", "b", 1.0, "moving"),
        6: DroneReplayState("a", "b", 0.5, "in_transit"),
    })
    replay = ReplayPlayer({"a": (0.0, 0.0), "b": (10.0, 0.0)}, [frame])
    screen = Mock()
    screen.get_size.return_value = (800, 600)
    with patch.object(replay, "_draw_drone") as draw:
        replay.draw(screen, Camera(), Mock())
    assert [call.args[2] for call in draw.call_args_list] == [2, 4, 3, 6]
