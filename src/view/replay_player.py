import pygame

from src.model.replay import DroneReplayState, ReplayFrame
from src.view.utils.camera import Camera


class ReplayPlayer:
    """Lit et affiche les frames enregistrées par la simulation."""

    DRONE_COLORS = (
            (100, 180, 255),
            (255, 180, 80),
            (100, 220, 120),
            (220, 100, 180),
            (180, 140, 255),
            (255, 220, 100),
        )

    def __init__(
        self,
        hub_positions: dict[str, tuple[float, float]],
        frames: list[ReplayFrame],
    ) -> None:
        self.hub_positions = hub_positions
        self.frames = frames

        self.current_index = 0

    def _drone_color(
        self,
        drone_id: int,
    ) -> tuple[int, int, int]:

        color_index = (
            drone_id - 1
        ) % len(self.DRONE_COLORS)

        return self.DRONE_COLORS[color_index]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        elif event.key == pygame.K_RIGHT:
            self.next_turn()

        elif event.key == pygame.K_LEFT:
            self.previous_turn()

        elif event.key == pygame.K_r:
            self.restart()

    def next_turn(self) -> None:
        if not self.frames:
            return

        self.current_index = min(
            self.current_index + 1,
            len(self.frames) - 1,
        )

    def previous_turn(self) -> None:
        self.current_index = max(
            self.current_index - 1,
            0,
        )

    def restart(self) -> None:
        self.current_index = 0

    def _state_position(
        self,
        state: DroneReplayState,
    ) -> tuple[float, float]:
        source = self.hub_positions[state.source]
        target = self.hub_positions[state.target]

        sx, sy = source
        tx, ty = target

        return (
            sx + (tx - sx) * state.progress,
            sy + (ty - sy) * state.progress,
        )

    def draw(
        self,
        screen: pygame.Surface,
        camera: Camera,
        font: pygame.font.Font,
    ) -> None:
        if not self.frames:
            return

        screen_w, screen_h = screen.get_size()

        current_frame = self.frames[
            self.current_index
        ]

        representatives: dict[str, int] = {}
        for drone_id, state in current_frame.drones.items():
            if state.source == state.target:
                representatives[state.source] = min(
                    drone_id, representatives.get(state.source, drone_id),
                )

        for drone_id, state in current_frame.drones.items():
            if (
                state.source == state.target
                and drone_id != representatives[state.source]
            ):
                continue

            position = self._state_position(
                state
            )

            screen_position = camera.world_to_screen(
                position[0],
                position[1],
                screen_w,
                screen_h,
            )

            self._draw_drone(
                screen,
                screen_position,
                drone_id,
                font,
            )

    def _draw_drone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        drone_id: int,
        font: pygame.font.Font,
    ) -> None:
        color = self._drone_color(drone_id)

        size = 10

        points = [
            (position[0], position[1] - size),
            (position[0] - size, position[1] + size),
            (position[0] + size, position[1] + size),
        ]

        pygame.draw.polygon(
            screen,
            color,
            points,
        )

        pygame.draw.polygon(
            screen,
            (255, 255, 255),
            points,
            2,
        )

        label = font.render(
            f"D_{drone_id}",
            True,
            (240, 240, 240),
        )

        screen.blit(
            label,
            (
                position[0] + 12,
                position[1] - 10,
            ),
        )

    def draw_overlay(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
    ) -> None:
        if not self.frames:
            return

        frame = self.frames[
            self.current_index
        ]

        info = font.render(
            (
                f"Turn {frame.turn}/"
                f"{self.frames[-1].turn} "
            ),
            True,
            (255, 255, 255),
        )

        screen.blit(info, (10, 10))

        controls = font.render(
            (
                "← Prev | → Next | R Restart"
            ),
            True,
            (180, 180, 180),
        )

        screen.blit(controls, (10, 35))
