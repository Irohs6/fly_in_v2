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
        turn_duration: float = 1.0,
    ) -> None:
        self.hub_positions = hub_positions
        self.frames = frames

        self.turn_duration = turn_duration

        self.current_index = 0
        self.elapsed = 0.0
        self.playing = True

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

            if state.source == state.target:
                first_id = min(
                    (
                        current_id
                        for current_id, current_state
                        in current_frame.drones.items()
                        if current_state.source == state.source
                        and current_state.target == state.target
                    ),
                    default=None,
                )

                if drone_id != first_id:
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

        pygame.draw.circle(
            screen,
            color,
            position,
            9,
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

    def draw_info_hub(
        self,
        screen: pygame.Surface,
        camera: Camera,
        font: pygame.font.Font,
    ) -> None:
        """Affiche le nombre de drones présents sur chaque hub."""

        if not self.frames:
            return

        frame = self.frames[self.current_index]

        screen_w, screen_h = screen.get_size()

        for hub_id, hub_state in frame.hubs.items():

            info = font.render(
                f"{hub_state.nb_drones} / {hub_state.capacity}",
                True,
                (255, 255, 255),
            )

            hub_position = camera.world_to_screen(
                self.hub_positions[hub_id][0],
                self.hub_positions[hub_id][1],
                screen_w,
                screen_h,
            )

            info_rect = info.get_rect()

            info_rect.midtop = (
                hub_position[0],
                hub_position[1] + 30,
            )

            screen.blit(info, info_rect)
