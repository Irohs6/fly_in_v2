import pygame
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.model.drone import Drone


class DroneSprite:
    def __init__(self, drone: "Drone"):
        self.drone = drone

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self._draw()

        self.rect = self.image.get_rect()

    def _draw(self):
        pygame.draw.circle(self.image, (80, 80, 80), (20, 20), 8)

        pygame.draw.line(self.image, (51, 51, 102), (20, 20), (5, 5), 8)
        pygame.draw.line(self.image,  (51, 51, 102), (20, 20), (35, 5), 8)
        pygame.draw.line(self.image,  (51, 51, 102), (20, 20), (5, 35), 8)
        pygame.draw.line(self.image,  (51, 51, 102), (20, 20), (35, 35), 8)

        pygame.draw.circle(self.image,  (200, 104, 51), (5, 5), 8)
        pygame.draw.circle(self.image,  (200, 104, 51), (35, 5), 8)
        pygame.draw.circle(self.image,  (200, 104, 51), (5, 35), 8)
        pygame.draw.circle(self.image,  (200, 104, 51), (35, 35), 8)

    def update(self):
        # Position calculée à partir de la zone du drone
        self.rect.center = self.drone.current_zone.screen_position

    def draw(self, screen, position=None):
        if position is not None:
            self.rect.center = position
        screen.blit(self.image, self.rect)


"""

from __future__ import annotations

import math
import pygame


    # ---------- Dimensions ----------
    SIZE = 48
    CENTER = (SIZE // 2, SIZE // 2)

    BODY_RADIUS = 8
    ARM_LENGTH = 14
    ARM_WIDTH = 4

    PROPELLER_RADIUS = 5
    LED_RADIUS = 2

    # ---------- Couleurs ----------
    BODY_COLOR = (90, 90, 90)
    ARM_COLOR = (51, 51, 102)
    PROPELLER_COLOR = (200, 104, 51)

    LED_IDLE = (0, 220, 0)
    LED_MOVING = (0, 150, 255)
    LED_ERROR = (255, 40, 40)

    SHADOW_COLOR = (0, 0, 0, 60)

    def __init__(self, drone: "Drone") -> None:
        super().__init__()

        self.drone = drone

        self.image = pygame.Surface(
            (self.SIZE, self.SIZE),
            pygame.SRCALPHA,
        )

        self.rect = self.image.get_rect()

        # Animation
        self.propeller_angle = 0
        self.led_visible = True
        self._blink_timer = 0

        self._redraw()

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def update(self) -> None:
        Met à jour l'état graphique

        if self.drone.current_zone:
            self.rect.center = self.drone.current_zone.screen_position

        # Animation des hélices
        if self.drone.status == "moving":
            self.propeller_angle = (self.propeller_angle + 25) % 360

        # Clignotement LED
        self._blink_timer += 1
        if self._blink_timer >= 20:
            self._blink_timer = 0
            self.led_visible = not self.led_visible

        self._redraw()

    # ------------------------------------------------------------------
    # DRAW
    # ------------------------------------------------------------------

    def _redraw(self) -> None:
        self.image.fill((0, 0, 0, 0))

        self._draw_shadow()
        self._draw_arms()
        self._draw_body()
        self._draw_propellers()
        self._draw_led()

    def _draw_shadow(self) -> None:
        pygame.draw.circle(
            self.image,
            self.SHADOW_COLOR,
            (self.CENTER[0], self.CENTER[1] + 2),
            self.BODY_RADIUS + 2,
        )

    def _draw_body(self) -> None:
        pygame.draw.circle(
            self.image,
            self.BODY_COLOR,
            self.CENTER,
            self.BODY_RADIUS,
        )

    def _draw_arms(self) -> None:
        cx, cy = self.CENTER

        points = (
            (cx - self.ARM_LENGTH, cy - self.ARM_LENGTH),
            (cx + self.ARM_LENGTH, cy - self.ARM_LENGTH),
            (cx - self.ARM_LENGTH, cy + self.ARM_LENGTH),
            (cx + self.ARM_LENGTH, cy + self.ARM_LENGTH),
        )

        for px, py in points:
            pygame.draw.line(
                self.image,
                self.ARM_COLOR,
                self.CENTER,
                (px, py),
                self.ARM_WIDTH,
            )

    def _draw_propellers(self) -> None:
        cx, cy = self.CENTER

        offsets = (
            (-self.ARM_LENGTH, -self.ARM_LENGTH),
            (self.ARM_LENGTH, -self.ARM_LENGTH),
            (-self.ARM_LENGTH, self.ARM_LENGTH),
            (self.ARM_LENGTH, self.ARM_LENGTH),
        )

        for ox, oy in offsets:

            x = cx + ox
            y = cy + oy

            pygame.draw.circle(
                self.image,
                self.PROPELLER_COLOR,
                (x, y),
                self.PROPELLER_RADIUS,
            )

            if self.drone.status == "moving":

                angle = math.radians(self.propeller_angle)

                dx = math.cos(angle) * 6
                dy = math.sin(angle) * 6

                pygame.draw.line(
                    self.image,
                    (255, 255, 255),
                    (x - dx, y - dy),
                    (x + dx, y + dy),
                    2,
                )

    def _draw_led(self) -> None:

        if not self.led_visible:
            return

        if self.drone.status == "idle":
            color = self.LED_IDLE

        elif self.drone.status == "moving":
            color = self.LED_MOVING

        else:
            color = self.LED_ERROR

        pygame.draw.circle(
            self.image,
            color,
            self.CENTER,
            self.LED_RADIUS,
        )
"""
