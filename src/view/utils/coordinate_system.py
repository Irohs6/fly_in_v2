from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.hub import Hub


class CoordinateSystem:
    """Convert map coordinates into world positions."""

    MAX_WORLD_SPAN = 10_000

    def __init__(
        self,
        cell_size: int = 400,
    ) -> None:
        """Initialize world positions with cell_size as the scale factor."""
        self.cell_size = cell_size
        self.world_positions: dict[
            str,
            tuple[float, float]
        ] = {}

    def compute(
        self,
        hubs: Iterable["Hub"],
    ) -> dict[str, tuple[float, float]]:

        """Center hubs and return their world positions by name. Scale by
        cell_size, reducing large extents proportionally on both axes to
        keep positions usable by Pygame. Replace stored positions for
        nonempty input; return an empty dictionary without changing
        stored positions for empty input.
        """
        hub_list = list(hubs)

        if not hub_list:
            return {}

        min_x = min(hub.x for hub in hub_list)
        max_x = max(hub.x for hub in hub_list)

        min_y = min(hub.y for hub in hub_list)
        max_y = max(hub.y for hub in hub_list)

        span = max(max_x - min_x, max_y - min_y)
        if span * self.cell_size > self.MAX_WORLD_SPAN:
            # Diviser les entiers avant de convertir évite un float infini.
            self.world_positions = {
                hub.name: (
                    (2 * hub.x - min_x - max_x) / (2 * span)
                    * self.MAX_WORLD_SPAN,
                    (2 * hub.y - min_y - max_y) / (2 * span)
                    * self.MAX_WORLD_SPAN,
                )
                for hub in hub_list
            }
        else:
            # Soustraire avant la conversion supporte un grand décalage.
            self.world_positions = {
                hub.name: (
                    (2 * hub.x - min_x - max_x) / 2 * self.cell_size,
                    (2 * hub.y - min_y - max_y) / 2 * self.cell_size,
                )
                for hub in hub_list
            }

        return self.world_positions
