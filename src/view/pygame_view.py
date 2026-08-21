import pygame

from src.model.graph import Graph
from src.model.replay import ReplayFrame
from src.view.graph_renderer import GraphRenderer
from src.view.replay_player import ReplayPlayer
from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


class PygameView:

    SCREEN_W = 1600
    SCREEN_H = 900
    CELL_SIZE = 160

    def __init__(
        self,
        graph: Graph,
        replay_frames: list[ReplayFrame],
    ) -> None:
        self.graph = graph
        self.replay_frames = replay_frames

    def display(self) -> None:
        pygame.init()

        screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Fly'in")

        font = pygame.font.SysFont(
            "times_new_roman",
            30,
        )

        font_small = pygame.font.SysFont(
            "arial",
            20,
            bold=True,
        )

        clock = pygame.time.Clock()

        camera = Camera()

        coord = CoordinateSystem(
            cell_size=self.CELL_SIZE
        )

        coord.compute(
            self.graph.hubs.values()
        )

        renderer = GraphRenderer(
            graph=self.graph,
            screen=screen,
            font=font,
            font_small=font_small,
            coordinate_system=coord,
        )

        replay = ReplayPlayer(
            hub_positions=coord.world_positions,
            frames=self.replay_frames,
            turn_duration=1.0,
        )

        running = True

        while running:
            dt = clock.tick(60) / 1000.0

            screen_w, screen_h = (
                screen.get_size()
            )

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_c:
                        camera.reset()

                elif event.type == pygame.MOUSEWHEEL:
                    mouse_x, mouse_y = (
                        pygame.mouse.get_pos()
                    )

                    factor = (
                        1.15
                        if event.y > 0
                        else 1 / 1.15
                    )

                    camera.apply_zoom(
                        mouse_x,
                        mouse_y,
                        screen_w,
                        screen_h,
                        factor,
                    )

                elif (
                    event.type
                    == pygame.MOUSEBUTTONDOWN
                    and event.button in (2, 3)
                ):
                    camera.start_drag(
                        event.pos[0],
                        event.pos[1],
                    )

                elif (
                    event.type
                    == pygame.MOUSEBUTTONUP
                    and event.button in (2, 3)
                ):
                    camera.end_drag()

                elif event.type == pygame.MOUSEMOTION:
                    camera.drag(
                        event.pos[0],
                        event.pos[1],
                    )

                replay.handle_event(event)

            replay.update(dt)

            renderer.draw(camera)

            replay.draw(
                screen,
                camera,
                font_small,
            )

            replay.draw_overlay(
                screen,
                font_small,
            )

            pygame.display.flip()

        pygame.quit()
