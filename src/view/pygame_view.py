import pygame

from src.model.state import TurnState
from src.view.errors import DisplayError
from src.view.graph_renderer import GraphRenderer
from src.view.replay_player import ReplayPlayer
from src.view.utils.coordinate_system import CoordinateSystem


class PygameView:

    """Interactive window displaying the network and recorded replay frames."""
    SCREEN_W = 0
    SCREEN_H = 0
    CELL_SIZE = 160

    def __init__(
        self,
        replay_frames: list[TurnState],
    ) -> None:
        """Store complete turn states without opening a window."""
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
        if not self.replay_frames:
            return
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

        coord = CoordinateSystem(
            cell_size=self.CELL_SIZE
        )
        world_positions = coord.compute(
            self.replay_frames[0].hubs.values()
        )

        renderer = GraphRenderer(
            screen=screen,
            font=font_small,
        )

        replay = ReplayPlayer(
            frames=self.replay_frames,
        )

        running = True

        while running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    running = False

                replay.handle_event(event)

            screen_w, screen_h = screen.get_size()
            max_x = max(
                (abs(x) for x, _ in world_positions.values()),
                default=0.0,
            )
            max_y = max(
                (abs(y) for _, y in world_positions.values()),
                default=0.0,
            )
            scale = min(
                1.0,
                (screen_w - 160) / (2 * max_x) if max_x else 1.0,
                (screen_h - 160) / (2 * max_y) if max_y else 1.0,
            )
            scale = max(0.0, scale)
            positions = {
                name: (
                    int(screen_w / 2 + x * scale),
                    int(screen_h / 2 + y * scale),
                )
                for name, (x, y) in world_positions.items()
            }

            frame = replay.frames[replay.current_index]
            renderer.draw(frame, positions)
            replay.draw(screen, font_small, positions)
            replay.draw_overlay(screen, font_small)

            pygame.display.flip()
