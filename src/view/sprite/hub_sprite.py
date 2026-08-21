from __future__ import annotations

from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.model.zone import Zone


class HubSprite:
    def __init__(
        self,
        zone: "Zone",
        radius: int = 30,
        color: tuple[int, int, int] = (100, 100, 100),
    ):
        self.zone = zone
        self.color = color

        self.radius = radius
        self.image = pygame.Surface(
            (self.radius * 2, self.radius * 2), pygame.SRCALPHA
        )
        self._draw()

        self.rect = self.image.get_rect()

    def _draw(self) -> None:
        pygame.draw.circle(
            self.image,
            (200, 200, 200),
            (self.radius, self.radius),
            self.radius,
        )
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius - 5
        )

    def update(self) -> None:
        # Position calculée à partir de la zone
        self.rect.center = self.zone.screen_position

    def draw(self, screen: pygame.Surface,
             position: tuple[int, int] | None = None) -> None:
        if position is not None:
            self.rect.center = position
        screen.blit(self.image, self.rect)
