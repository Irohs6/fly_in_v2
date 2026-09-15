import pygame

from src.model.graph import Graph
from src.model.replay import HubReplayState, ReplayFrame
from src.view.errors import DisplayError
from src.view.graph_renderer import GraphRenderer
from src.view.replay_player import ReplayPlayer
from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


class PygameView:

    """Interactive window displaying the network and recorded replay frames."""
    SCREEN_W = 0
    SCREEN_H = 0
    CELL_SIZE = 160

    def __init__(
        self,
        graph: Graph,
        replay_frames: list[ReplayFrame],
    ) -> None:
        """Store the graph and frames without opening a window."""
        self.graph = graph
        self.replay_frames = replay_frames

    def display(self) -> None:
        """Display the replay and always release Pygame resources.

        Wrap expected Pygame errors in DisplayError for the entry point.
        Other exceptions propagate after cleanup.
        """
        try:
            self._display_replay()
        except pygame.error as exc:
            raise DisplayError(
                f"Cannot display graphical replay: {exc}"
            ) from exc
        finally:
            pygame.quit()

    def _display_replay(self) -> None:
        """Initialize the window and run the interactive replay loop."""
        pygame.init()

        screen = pygame.display.set_mode(
            (self.SCREEN_W, self.SCREEN_H),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Fly'in")

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
            coordinate_system=coord,
            font=font_small,
        )

        replay = ReplayPlayer(
            hub_positions=coord.world_positions,
            frames=self.replay_frames,
        )

        running = True

        while running:
            clock.tick(60)

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

            hub_states: dict[str, HubReplayState] = {}

            if replay.frames:
                hub_states = replay.frames[
                    replay.current_index].hubs

            renderer.draw(camera, hub_states)

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
