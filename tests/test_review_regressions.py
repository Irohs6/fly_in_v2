"""Regression tests for validator errors and reroute cost decisions."""

import sys
from pathlib import Path

import pytest

import main
from src.model.graph import Graph
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.parser.validator import ValidatorError


def write_map(tmp_path: Path, lines: list[str]) -> Path:
    """Write a small valid or deliberately invalid map."""
    path = tmp_path / "test.map"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def test_validator_error_reaches_parser_caller(tmp_path: Path) -> None:
    """Validation failures are not converted into ParseError."""
    path = write_map(tmp_path, [
        "nb_drones: 1",
        "start_hub: start 0 0",
        "end_hub: goal 1 0",
        "connection: start-missing",
    ])
    with pytest.raises(ValidatorError, match="Line 4:.*unknown hub"):
        Parser(str(path)).parse()


def test_main_catches_validator_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The command-line entry point reports validator errors cleanly."""
    path = write_map(tmp_path, [
        "nb_drones: 1",
        "start_hub: start 0 0",
        "end_hub: goal 1 0",
        "connection: start-missing",
    ])
    monkeypatch.setattr(
        sys, "argv", ["main.py", str(path), "--no-view"],
    )
    assert main.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Line 4:" in captured.err
    assert "unknown hub" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    "detour_length, reroutes",
    [(3, True), (4, False)],
)
def test_reroute_cost_threshold(
    tmp_path: Path, detour_length: int, reroutes: bool,
) -> None:
    """A route costing over two extra turns is rejected and restored."""
    intermediates = [f"x{i}" for i in range(detour_length - 1)]
    lines = [
        "nb_drones: 1",
        "start_hub: start 0 0",
        "end_hub: goal 10 0",
    ]
    lines.extend(
        f"hub: {name} {index + 1} 0"
        for index, name in enumerate(intermediates)
    )
    lines.append("connection: start-goal")
    route = ["start", *intermediates, "goal"]
    lines.extend(
        f"connection: {source}-{target}"
        for source, target in zip(route, route[1:])
    )
    graph = Graph(Parser(str(write_map(tmp_path, lines))).parse())
    simulation = Simulation(graph)
    simulation.load_drones(1)
    drone = simulation.drones[0]
    direct = graph.get_connection(graph.start_hub, graph.end_hub)
    assert direct is not None
    direct.use_capacity()

    assert simulation._Simulation__move_or_wait(drone) is reroutes
    if reroutes:
        assert drone.current_position is graph.hubs["x0"]
    else:
        assert drone.current_position is graph.start_hub
        assert drone.status == "waiting"
        assert drone.path == [graph.end_hub]

        direct.used_capacity = 0
        assert simulation._Simulation__move_or_wait(drone) is True
        assert drone.current_position is graph.end_hub
