import pygame
from src.model.graph import Graph
from src.model.hub import Hub
from .utils.camera import Camera
from .utils.coordinate_system import CoordinateSystem
from src.model.replay import HubReplayState


# ───────────────────────────────────────────────
# HubRenderer
# ───────────────────────────────────────────────


class HubRenderer:
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

    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font

    def radius(self, zone: Hub, zoom: float) -> int:
        # Rayon calculé en fonction de la capacité maximale du hub
        hub_radius = self.HUB_BASE_RADIUS + zone.capacity * self.HUB_SCALE

        # On limite le rayon entre une valeur minimale et maximale
        hub_radius = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS,
                         hub_radius))

        # Application du zoom
        return max(4, int(hub_radius * zoom))

    def draw(
        self,
        screen: pygame.Surface,
        zone: Hub,
        position: tuple[int, int],
        zoom: float,
        hub_state: HubReplayState | None = None,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        hub_color = self.COLOR_MAP.get(
            zone.color,
            (200, 200, 200),
        )

        hub_radius = self.radius(zone, zoom)

        border_color = (255, 255, 255)
        border_width = 2

        if is_start or is_end:
            border_color = (255, 215, 0)
            border_width = 3

        pygame.draw.circle(
            screen,
            hub_color,
            position,
            hub_radius,
        )

        pygame.draw.circle(
            screen,
            border_color,
            position,
            hub_radius,
            border_width,
        )

        self.draw_label(
            screen,
            zone,
            position,
            hub_radius,
        )

        if hub_state is not None:
            capacity = (
                "∞"
                if hub_state.capacity == float("inf")
                else str(hub_state.capacity)
            )

            info = self.font.render(
                f"{hub_state.nb_drones}/{capacity}",
                True,
                (255, 255, 255),
            )

            info_rect = info.get_rect()

            info_rect.midtop = (
                position[0],
                position[1] + hub_radius + 6,
            )

            screen.blit(info, info_rect)

    def draw_label(
        self,
        screen: pygame.Surface,
        zone: Hub,
        position: tuple[int, int],
        radius: int,
    ) -> None:

        label = self.font.render(
            zone.name,
            True,
            (230, 230, 235)
        )

        label_rect = label.get_rect()

        label_rect.midbottom = (
            position[0],
            position[1] - radius - 6
        )

        screen.blit(label, label_rect)
# ───────────────────────────────────────────────
# ConnectionRenderer
# ───────────────────────────────────────────────


class ConnectionRenderer:
    CONN_FILL = (55, 60, 78)
    CONN_BORDER = (40, 45, 60)
    BAND_WIDTH = 9

    def draw(self, screen: pygame.Surface,
             source_position: tuple[int, int],
             target_position: tuple[int, int], zoom: float) -> None:
        # Ne rien dessiner si les deux hubs sont au même endroit
        if source_position == target_position:
            return

        # Épaisseur de la connexion selon le zoom
        border_width = max(
            2,
            int(self.BAND_WIDTH * zoom),
        )

        fill_width = max(
            1,
            border_width - 3,
        )

        pygame.draw.line(
            screen,
            self.CONN_BORDER,
            source_position,
            target_position,
            border_width,
        )

        pygame.draw.line(
            screen,
            self.CONN_FILL,
            source_position,
            target_position,
            fill_width,
        )


# ───────────────────────────────────────────────
# GraphRenderer
# ───────────────────────────────────────────────


class GraphRenderer:
    BG_COLOR = (20, 20, 25)

    def __init__(
        self,
        graph: Graph,
        screen: pygame.Surface,
        coordinate_system: CoordinateSystem,
        font: pygame.font.Font
    ) -> None:
        self.graph = graph
        self.screen = screen
        self.coord = coordinate_system
        self.world_positions = self.coord.world_positions

        self.hub_renderer = HubRenderer(font)
        self.connection_renderer = ConnectionRenderer()

    def draw(self, camera: Camera,
             hub_states: dict[str, HubReplayState]) -> None:
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(self.BG_COLOR)

        hub_screen_positions = {
            name: camera.world_to_screen(x, y, screen_width, screen_height)
            for name, (x, y) in self.world_positions.items()
        }

        for connection in self.graph.connections:
            source_pos = hub_screen_positions.get(connection.source.name)
            target_pos = hub_screen_positions.get(connection.target.name)
            if source_pos is not None and target_pos is not None:
                self.connection_renderer.draw(
                    self.screen, source_pos, target_pos,
                    camera.zoom
                )

        for zone in self.graph.hubs.values():
            hub_pos = hub_screen_positions.get(zone.name)
            if hub_pos is not None:
                self.hub_renderer.draw(
                    self.screen,
                    zone,
                    hub_pos,
                    zoom=camera.zoom,
                    hub_state=hub_states.get(zone.name),
                    is_start=(zone == self.graph.start_zone),
                    is_end=(zone == self.graph.end_zone),
                )
