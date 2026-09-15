import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pygame
import pytest

from src.model.graph import Graph
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.view.errors import DisplayError
from src.view.pygame_view import PygameView


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "assets/maps/easy/01_linear_path.txt"


@pytest.fixture
def view(monkeypatch: pytest.MonkeyPatch) -> PygameView:
    """Build a replay using SDL's in-memory video and audio drivers."""
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    simulation = Simulation(Graph(Parser(str(MAP)).parse()))
    simulation.load_drones(1)
    simulation.simulate()
    return PygameView(simulation.graph, simulation.recorder.frames)


@pytest.mark.parametrize("target", [
    "pygame.init",
    "pygame.display.set_mode",
    "src.view.graph_renderer.GraphRenderer.draw",
])
@pytest.mark.parametrize("error_type", [
    pygame.error, RuntimeError, KeyboardInterrupt,
])
def test_display_always_cleans_up_without_masking_unexpected_errors(
    view: PygameView, target: str, error_type: type[BaseException],
) -> None:
    error = error_type("test failure")
    expected = DisplayError if error_type is pygame.error else error_type
    with patch(target, side_effect=error), patch(
        "pygame.quit", wraps=pygame.quit,
    ) as quit_mock:
        with pytest.raises(expected) as caught:
            view.display()
        quit_mock.assert_called_once()
    if error_type is pygame.error:
        assert caught.value.__cause__ is error
        assert "Cannot display graphical replay" in str(caught.value)
    else:
        assert caught.value is error
    assert not pygame.get_init()


def test_normal_window_close_cleans_up(view: PygameView) -> None:
    event = pygame.event.Event(pygame.QUIT)
    with patch("pygame.event.get", return_value=[event]), patch(
        "pygame.quit", wraps=pygame.quit,
    ) as quit_mock:
        view.display()
        quit_mock.assert_called_once()
    assert not pygame.get_init()


@pytest.mark.parametrize("terminal_only", [False, True])
def test_cli_with_unavailable_video_driver(terminal_only: bool) -> None:
    env = os.environ.copy()
    env["SDL_VIDEODRIVER"] = "flyin_nonexistent_driver"
    env["SDL_AUDIODRIVER"] = "dummy"
    command = [sys.executable, "main.py", str(MAP)]
    if terminal_only:
        command.append("--no-gui")
    result = subprocess.run(
        command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=10,
    )
    assert result.stdout == (
        "D1-waypoint1\nD1-waypoint2 D2-waypoint1\n"
        "D1-goal D2-waypoint2\nD2-goal\n"
    )
    if terminal_only:
        assert result.returncode == 0
        assert result.stderr == ""
    else:
        assert result.returncode == 1
        assert result.stderr.startswith(
            "Error: Cannot display graphical replay",
        )
        assert len(result.stderr.splitlines()) == 1
        assert "Traceback" not in result.stderr
