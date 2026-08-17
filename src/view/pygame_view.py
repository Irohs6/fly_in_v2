import pygame

from pygame.locals import (
    QUIT,
    KEYDOWN,
    K_ESCAPE,
    K_r,
    MOUSEWHEEL,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
)

from src.model.graph import Graph
from src.view.graph_renderer import GraphRenderer
from src.view.drone_animator import DroneAnimationLayer
from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


class Pygame_view:
    SCREEN_W = 1600
    SCREEN_H = 900
    CELL_SIZE = 160

    BG_COLOR = (40, 40, 45)

    def __init__(self, graph: Graph, simulation=None):
        self.graph = graph
        self.simulation = simulation
        self.animation_layer = None

    def display(self):
        pygame.init()
        screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H), pygame.RESIZABLE
        )
        pygame.display.set_caption("Fly'in")

        font = pygame.font.SysFont("time_new_roman", 30)
        font_small = pygame.font.SysFont("arial", 20, bold=True)
        clock = pygame.time.Clock()

        # Camera & Coordinate system
        camera = Camera()
        coord = CoordinateSystem(cell_size=self.CELL_SIZE)
        coord.compute(self.graph.zones.values())

        # Renderer
        renderer = GraphRenderer(
            graph=self.graph,
            screen=screen,
            font=font,
            font_small=font_small,
            coordinate_system=coord,
        )

        # Drone animation layer
        if self.simulation and self.simulation.replay_frames:
            self.animation_layer = DroneAnimationLayer(
                hub_positions=coord.world_positions,
                replay_frames=self.simulation.replay_frames,
                graph=self.graph,
                auto_replay_speed=1.5,
            )

        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            screen_w, screen_h = screen.get_size()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_r:
                        camera.reset()

                # Camera events
                elif event.type == MOUSEWHEEL:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    factor = 1.15 if event.y > 0 else 1 / 1.15
                    camera.apply_zoom(mouse_x, mouse_y, screen_w,
                                      screen_h, factor)

                elif event.type == MOUSEBUTTONDOWN and event.button in (2, 3):
                    camera.start_drag(event.pos[0], event.pos[1])

                elif event.type == MOUSEBUTTONUP and event.button in (2, 3):
                    camera.end_drag()

                elif event.type == MOUSEMOTION:
                    camera.drag(event.pos[0], event.pos[1])

                # Drone replay controls
                if self.animation_layer:
                    self.animation_layer.handle_event(event)

            # Update drone animation
            if self.animation_layer:
                self.animation_layer.update(dt)

            # Draw graph
            renderer.draw(camera)

            # Draw drones + overlay
            if self.animation_layer:
                self.animation_layer.draw(
                    screen,
                    camera,
                    screen_w,
                    screen_h,
                    camera.zoom,
                    font_small,
                )
                self.animation_layer.draw_overlay(
                    screen,
                    font_small,
                    screen_w,
                    screen_h,
                )

            pygame.display.flip()

        pygame.quit()
