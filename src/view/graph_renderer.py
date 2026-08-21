import math
import pygame
from .sprite.hub_sprite import HubSprite


# ───────────────────────────────────────────────
# HubRenderer
# ───────────────────────────────────────────────


class HubRenderer:
    BG_COLOR = (20, 20, 25)

    COLOR_MAP = {
        "black": (40, 40, 45),
        "blue": (0, 128, 255),
        "brown": (120, 70, 30),
        "crimson": (220, 20, 60),
        "cyan": (43, 220, 255),
        "darkred": (139, 0, 0),
        "gold": (255, 215, 0),
        "green": (50, 200, 80),
        "lime": (150, 255, 50),
        "magenta": (200, 0, 200),
        "maroon": (128, 0, 0),
        "orange": (255, 128, 0),
        "purple": (160, 60, 200),
        "rainbow": (255, 100, 150),
        "red": (220, 50, 50),
        "violet": (130, 80, 220),
        "yellow": (220, 200, 30),
        "white": (200, 200, 200),
    }

    HUB_BASE_RADIUS = 20
    HUB_SCALE = 3
    HUB_MIN_RADIUS = 20
    HUB_MAX_RADIUS = 55
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, font, font_small):
        self.font = font
        self.font_small = font_small

    def radius(self, zone, zoom):
        # Rayon calculé en fonction de la capacité maximale du hub
        hub_radius = self.HUB_BASE_RADIUS + zone.capacity * self.HUB_SCALE

        # On limite le rayon entre une valeur minimale et maximale
        hub_radius = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS,
                         hub_radius))

        # Application du zoom
        return max(4, int(hub_radius * zoom))

    def draw(self, screen: pygame.Surface, zone, position: tuple[int, int],
             zoom: float, is_start: bool = False,
             is_end: bool = False) -> None:
        # Couleur du hub
        hub_color = self.COLOR_MAP.get(zone.color, (200, 200, 200))

        # Calcul du rayon
        hub_radius = self.radius(zone, zoom)

        # Dessin du cercle principal
        HubSprite(zone, radius=hub_radius,
                  color=hub_color).draw(screen, position)

        # Dessin du contour (or pour départ/arrivée, blanc sinon)
        if is_start or is_end:
            pygame.draw.circle(screen, (255, 215, 0), position, hub_radius, 3)
        else:
            pygame.draw.circle(screen, (255, 255, 255),
                               position, hub_radius, 2)


# ───────────────────────────────────────────────
# ConnectionRenderer
# ───────────────────────────────────────────────

class ConnectionRenderer:
    BG_COLOR = (20, 20, 25)
    CONN_FILL = (55, 60, 78)
    CONN_BORDER = (40, 45, 60)
    BAND_WIDTH = 9

    def __init__(self, font_small):
        self.font_small = font_small

    def draw(self, screen: pygame.Surface, connection,
             source_position: tuple[int, int],
             target_position: tuple[int, int], zoom: float) -> None:
        # Ne rien dessiner si les deux hubs sont au même endroit
        if math.hypot(
            target_position[0] - source_position[0],
            target_position[1] - source_position[1],
        ) == 0:
            return

        # Épaisseur de la connexion selon le zoom
        connection_width = max(2, int(self.BAND_WIDTH * zoom))

        # Bande principale
        pygame.draw.line(
            screen,
            self.CONN_FILL,
            source_position,
            target_position,
            connection_width,
        )

        # Contour de la bande
        pygame.draw.line(
            screen,
            self.CONN_BORDER,
            source_position,
            target_position,
            max(1, connection_width - 2),
        )

# ───────────────────────────────────────────────
# GraphRenderer
# ───────────────────────────────────────────────


class GraphRenderer:
    BG_COLOR = (20, 20, 25)

    def __init__(self, graph, screen, font, font_small, coordinate_system):
        self.graph = graph
        self.screen = screen
        self.coord = coordinate_system
        self.world_positions = self.coord.world_positions

        self.hub_renderer = HubRenderer(font, font_small)
        self.connection_renderer = ConnectionRenderer(font_small)

    def draw(self, camera):
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(self.BG_COLOR)

        hub_screen_positions = {
            name: camera.world_to_screen(x, y, screen_width, screen_height)
            for name, (x, y) in self.world_positions.items()
        }

        for connection in self.graph.connections:
            source_pos = hub_screen_positions.get(connection.source.name)
            target_pos = hub_screen_positions.get(connection.target.name)
            if source_pos and target_pos:
                self.connection_renderer.draw(
                    self.screen, connection, source_pos, target_pos,
                    camera.zoom
                )

        for zone in self.graph.hubs.values():
            hub_pos = hub_screen_positions.get(zone.name)
            if hub_pos:
                self.hub_renderer.draw(
                    self.screen,
                    zone,
                    hub_pos,
                    zoom=camera.zoom,
                    is_start=(zone == self.graph.start_zone),
                    is_end=(zone == self.graph.end_zone),
                )
