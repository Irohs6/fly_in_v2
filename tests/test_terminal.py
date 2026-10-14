from pathlib import Path

import pytest

from src.model.graph import Graph
from src.model.simulation import Simulation
from src.model.state import TurnState
from src.parser.parser import Parser
from src.view.terminal import TerminalView


def make_simulation(
    tmp_path: Path,
    *,
    restricted: bool = False,
    connection: str = "start-a",
) -> Simulation:
    map_path = tmp_path / "terminal.txt"
    zone_type = "restricted" if restricted else "normal"
    map_path.write_text(
        "\n".join([
            "nb_drones: 3",
            "start_hub: start 0 0",
            f"hub: a 1 0 [zone={zone_type} capacity=1]",
            "hub: b 2 0 [capacity=1]",
            "end_hub: goal 3 0",
            f"connection: {connection}",
            "connection: a-b",
            "connection: b-goal",
        ]),
        encoding="utf-8",
    )
    data = Parser(str(map_path)).parse()
    simulation = Simulation(Graph(data))
    simulation.load_drones(data["nb_drones"])
    return simulation


def test_terminal_pipeline(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    simulation = make_simulation(tmp_path)
    turns = simulation.simulate()
    assert capsys.readouterr().out == ""
    TerminalView().display(turns)

    assert capsys.readouterr().out == (
        "D1-a\n"
        "D1-b D2-a\n"
        "D1-goal D2-b D3-a\n"
        "D2-goal D3-b\n"
        "D3-goal\n"
    )
    assert turns[1].drones[1].current_position == "a"
    assert simulation.turn == 5


@pytest.mark.parametrize("connection", ["start-a", "a-start"])
def test_terminal_restricted_transit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    connection: str,
) -> None:
    simulation = make_simulation(
        tmp_path, restricted=True, connection=connection,
    )
    turns = simulation.simulate()
    TerminalView().display(turns)

    assert capsys.readouterr().out == (
        f"D1-{connection}\n"
        "D1-a\n"
        f"D1-b D2-{connection}\n"
        "D1-goal D2-a\n"
        f"D2-b D3-{connection}\n"
        "D2-goal D3-a\n"
        "D3-b\n"
        "D3-goal\n"
    )
    assert turns[1].drones[1].current_position == tuple(connection.split("-"))
    assert turns[2].drones[1].current_position == "a"

    # Both views use the same recorded states.
    frames = simulation.recorder.frames
    assert frames is turns
    assert len(frames) == simulation.turn + 1
    transit = frames[1].drones[1]
    assert transit.previous_zone == "start"
    assert transit.path == ("a", "b", "goal")
    assert transit.status == "in_transit"
    assert (transit.transit_turns, transit.transit_duration) == (1, 2)
    arrival = frames[2].drones[1]
    assert arrival.current_position == "a"
    assert (arrival.transit_turns, arrival.transit_duration) == (0, 0)


def test_terminal_empty_turn(capsys: pytest.CaptureFixture[str]) -> None:
    TerminalView().display([TurnState(1, "start", "end", {}, {}, {})])
    assert capsys.readouterr().out == "\n"


def test_terminal_no_turns(capsys: pytest.CaptureFixture[str]) -> None:
    TerminalView().display([])
    assert capsys.readouterr().out == ""
