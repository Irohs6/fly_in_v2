import pygame

from src.model.state import ConnectionState, HubState, TurnState
from .utils.camera import Camera


class HubRenderer:
    """Draw recorded hubs, occupants and reserved arrival slots."""

    COLOR_MAP = {
        "beige": (245, 245, 220),
        "black": (40, 40, 45),
        "blue": (0, 128, 255),
        "brown": (120, 70, 30),
        "crimson": (220, 20, 60),
        "cyan": (43, 220, 255),
        "darkred": (139, 0, 0),
        "gold": (255, 215, 0),
        "gray": (128, 128, 128),
        "green": (50, 200, 80),
        "lightblue": (173, 216, 230),
        "lightbrown": (181, 133, 95),
        "lime": (150, 255, 50),
        "magenta": (200, 0, 200),
        "maroon": (128, 0, 0),
        "orange": (255, 128, 0),
        "purple": (160, 60, 200),
        "rainbow": (255, 100, 150),
        "red": (220, 50, 50),
        "teal": (0, 128, 128),
        "violet": (130, 80, 220),
        "yellow": (220, 200, 30),
        "white": (200, 200, 200),
    }

    HUB_BASE_RADIUS = 20
    HUB_SCALE = 3
    HUB_MIN_RADIUS = 20
    HUB_MAX_RADIUS = 55

    def __init__(self, font: pygame.font.Font) -> None:
        """Store the font used for hub labels."""
        self.font = font

    def radius(self, zone: HubState, zoom: float) -> int:
        """Compute a bounded pixel radius from capacity and zoom."""
        radius = self.HUB_BASE_RADIUS + zone.capacity * self.HUB_SCALE
        radius = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS, radius))
        return max(4, int(radius * zoom))

    def draw(
        self,
        screen: pygame.Surface,
        zone: HubState,
        position: tuple[int, int],
        zoom: float,
        is_terminal: bool = False,
    ) -> None:
        """Draw a hub using only the selected turn's recorded values."""
        radius = self.radius(zone, zoom)
        pygame.draw.circle(
            screen, self.COLOR_MAP.get(zone.color, (200, 200, 200)),
            position, radius,
        )
        pygame.draw.circle(
            screen, (255, 215, 0) if is_terminal else (255, 255, 255),
            position, radius, 3 if is_terminal else 2,
        )
        label = self.font.render(zone.name, True, (230, 230, 235))
        label_rect = label.get_rect()
        label_rect.midbottom = (position[0], position[1] - radius - 6)
        screen.blit(label, label_rect)

        capacity = "∞" if zone.capacity == float("inf") else str(zone.capacity)
        occupancy = f"{zone.nb_drones}/{capacity}"
        if zone.reserved:
            occupancy += f" +{zone.reserved} reserved"
        info = self.font.render(occupancy, True, (255, 255, 255))
        info_rect = info.get_rect()
        info_rect.midtop = (position[0], position[1] + radius + 6)
        screen.blit(info, info_rect)


class ConnectionRenderer:
    """Draw connections with recorded usage and remaining transits."""

    CONN_FILL = (55, 60, 78)
    CONN_BORDER = (40, 45, 60)
    BAND_WIDTH = 9

    def __init__(self, font: pygame.font.Font) -> None:
        """Store the font used for connection capacity labels."""
        self.font = font

    def draw(
        self,
        screen: pygame.Surface,
        source_position: tuple[int, int],
        target_position: tuple[int, int],
        zoom: float,
        state: ConnectionState,
    ) -> None:
        """Draw turn usage separately from drones still in transit."""
        if source_position == target_position:
            return
        border_width = max(2, int(self.BAND_WIDTH * zoom))
        pygame.draw.line(
            screen, self.CONN_BORDER, source_position, target_position,
            border_width,
        )
        color = (90, 150, 210) if state.used_capacity else self.CONN_FILL
        pygame.draw.line(
            screen, color, source_position, target_position,
            max(1, border_width - 3),
        )
        capacity = (
            "∞" if state.capacity == float("inf") else str(state.capacity)
        )
        usage = f"{state.used_capacity}/{capacity}"
        if state.in_transit:
            usage += f" ({state.in_transit} in transit)"
        label = self.font.render(usage, True, (210, 220, 235))
        label_rect = label.get_rect()
        label_rect.midbottom = (
            (source_position[0] + target_position[0]) // 2,
            (source_position[1] + target_position[1]) // 2 - 6,
        )
        screen.blit(label, label_rect)


class GraphRenderer:
    """Draw a graph from a complete recorded turn, without live model data."""

    BG_COLOR = (20, 20, 25)

    def __init__(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """Associate the screen and font with the entity renderers."""
        self.screen = screen
        self.hub_renderer = HubRenderer(font)
        self.connection_renderer = ConnectionRenderer(font)

    def draw(
        self,
        camera: Camera,
        frame: TurnState,
        world_positions: dict[str, tuple[float, float]],
    ) -> None:
        """Draw the connections and hubs belonging to the selected turn."""
        screen_width, screen_height = self.screen.get_size()
        self.screen.fill(self.BG_COLOR)
        positions = {
            name: camera.world_to_screen(x, y, screen_width, screen_height)
            for name, (x, y) in world_positions.items()
        }
        for connection in frame.connections.values():
            self.connection_renderer.draw(
                self.screen, positions[connection.source],
                positions[connection.target], camera.zoom, connection,
            )
        for hub in frame.hubs.values():
            self.hub_renderer.draw(
                self.screen, hub, positions[hub.name], camera.zoom,
                is_terminal=hub.name in (frame.start_hub, frame.end_hub),
            )
