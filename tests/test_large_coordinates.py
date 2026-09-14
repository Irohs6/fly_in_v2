from pathlib import Path

import pygame
import pytest

from src.model.graph import Graph
from src.model.hub import Hub
from src.model.simulation import Simulation
from src.parser.parser import Parser
from src.view.graph_renderer import GraphRenderer
from src.view.replay_player import ReplayPlayer
from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


@pytest.mark.parametrize("value", [2**31 - 1, 2**31, -(2**31) - 1, 10**400])
@pytest.mark.parametrize("axis", [0, 1])
def test_large_coordinates_parse_simulate_and_render(
    tmp_path: Path, value: int, axis: int,
) -> None:
    coordinates = [0, 0]
    coordinates[axis] = value
    path = tmp_path / "large.txt"
    path.write_text(
        "nb_drones: 1\nstart_hub: start 0 0\n"
        f"hub: a {coordinates[0]} {coordinates[1]} [zone=restricted]\n"
        "end_hub: end 1 1\n"
        "connection: start-a\nconnection: a-end\n"
    )
    graph = Graph(Parser(str(path)).parse())
    assert (graph.hubs["a"].x, graph.hubs["a"].y) == tuple(coordinates)
    simulation = Simulation(graph)
    simulation.load_drones(1)
    simulation.simulate()
    assert simulation.turn == 3

    coord = CoordinateSystem(160)
    coord.compute(graph.hubs.values())
    pygame.font.init()
    try:
        screen = pygame.Surface((800, 600))
        font = pygame.font.Font(None, 20)
        renderer = GraphRenderer(graph, screen, coord, font)
        replay = ReplayPlayer(
            coord.world_positions, simulation.recorder.frames,
        )
        camera = Camera()
        for zoom in (camera.zoom_min, 1.0, camera.zoom_max):
            camera.zoom = zoom
            for index, frame in enumerate(replay.frames):
                replay.current_index = index
                renderer.draw(camera, frame.hubs)
                replay.draw(screen, camera, font)
    finally:
        pygame.font.quit()


def test_large_offset_preserves_small_distances() -> None:
    offset = 10**400
    hubs = [Hub("a", x=offset, y=offset),
            Hub("b", x=offset + 2, y=offset + 4)]
    assert CoordinateSystem(160).compute(hubs) == {
        "a": (-160.0, -320.0), "b": (160.0, 320.0),
    }


def test_large_extent_preserves_proportions() -> None:
    hubs = [Hub("a"), Hub("b", x=10**400, y=2 * 10**400)]
    positions = CoordinateSystem(160).compute(hubs)
    assert positions == {
        "a": (-2500.0, -5000.0), "b": (2500.0, 5000.0),
    }
