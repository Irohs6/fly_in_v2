import pygame

from src.model.replay import DroneReplayState, ReplayFrame
from src.view.utils.camera import Camera


class ReplayPlayer:
    """Lit et affiche les frames enregistrées par la simulation."""

    def __init__(
        self,
        hub_positions: dict[str, tuple[float, float]],
        frames: list[ReplayFrame],
        turn_duration: float = 1.0,
    ) -> None:
        self.hub_positions = hub_positions
        self.frames = frames

        self.turn_duration = turn_duration

        self.current_index = 0
        self.elapsed = 0.0
        self.playing = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.playing = not self.playing

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

        self.elapsed = 0.0
        self.playing = False

    def previous_turn(self) -> None:
        self.current_index = max(
            self.current_index - 1,
            0,
        )

        self.elapsed = 0.0
        self.playing = False

    def restart(self) -> None:
        self.current_index = 0
        self.elapsed = 0.0
        self.playing = True

    def update(self, dt: float) -> None:
        if not self.playing:
            return

        if self.current_index >= len(self.frames) - 1:
            self.playing = False
            return

        self.elapsed += dt

        if self.elapsed < self.turn_duration:
            return

        self.elapsed -= self.turn_duration
        self.current_index += 1

        if self.current_index >= len(self.frames) - 1:
            self.current_index = len(self.frames) - 1
            self.elapsed = 0.0
            self.playing = False

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

    def _drone_position(
        self,
        drone_id: str,
    ) -> tuple[float, float] | None:
        if not self.frames:
            return None

        current_frame = self.frames[self.current_index]

        current_state = current_frame.drones.get(
            drone_id
        )

        if current_state is None:
            return None

        current_pos = self._state_position(
            current_state
        )

        if self.current_index >= len(self.frames) - 1:
            return current_pos

        next_frame = self.frames[
            self.current_index + 1
        ]

        next_state = next_frame.drones.get(
            drone_id
        )

        if next_state is None:
            return current_pos

        next_pos = self._state_position(
            next_state
        )

        progress = min(
            1.0,
            self.elapsed / self.turn_duration,
        )

        cx, cy = current_pos
        nx, ny = next_pos

        return (
            cx + (nx - cx) * progress,
            cy + (ny - cy) * progress,
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

        for drone_id, state in current_frame.drones.items():
            position = self._drone_position(
                drone_id
            )

            if position is None:
                continue

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
                state.status,
                font,
            )

    def _draw_drone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        drone_id: str,
        status: str,
        font: pygame.font.Font,
    ) -> None:
        color = (100, 180, 255)

        if status == "in_transit":
            color = (255, 180, 80)

        elif status == "waiting":
            color = (160, 160, 160)

        elif status == "delivered":
            color = (100, 220, 120)

        pygame.draw.circle(
            screen,
            color,
            position,
            9,
        )

        label = font.render(
            drone_id,
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

        state = (
            "PLAYING"
            if self.playing
            else "PAUSED"
        )

        info = font.render(
            (
                f"Turn {frame.turn}/"
                f"{self.frames[-1].turn} "
                f"[{state}]"
            ),
            True,
            (255, 255, 255),
        )

        screen.blit(info, (10, 10))

        controls = font.render(
            (
                "SPACE Play/Pause | "
                "← Prev | → Next | R Restart"
            ),
            True,
            (180, 180, 180),
        )

        screen.blit(controls, (10, 35))
